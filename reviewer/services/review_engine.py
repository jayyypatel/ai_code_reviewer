import json
from typing import Any

from .ai_service import analyze_code
from .exceptions import ValidationServiceError
from .github_service import GitHubService
from reviewer.utils.diff_parser import parse_pr_file_patches

ALLOWED_TYPES = {"bug", "performance", "security", "improvement"}
ALLOWED_SEVERITIES = {"low", "medium", "high"}


def _normalize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    issue_type = issue.get("type", "improvement")
    severity = issue.get("severity", "medium")

    if issue_type not in ALLOWED_TYPES:
        issue_type = "improvement"
    if severity not in ALLOWED_SEVERITIES:
        severity = "medium"

    line_value = issue.get("line")
    if not isinstance(line_value, int):
        line_value = None

    return {
        "type": issue_type,
        "severity": severity,
        "file": str(issue.get("file", "")),
        "line": line_value,
        "title": str(issue.get("title", "Code quality finding")),
        "explanation": str(issue.get("explanation", "")),
        "suggestion": str(issue.get("suggestion", "")),
        "fixed_code": issue.get("fixed_code") if isinstance(issue.get("fixed_code"), str) else None,
    }


def _normalize_output(raw_output: Any) -> list[dict[str, Any]]:
    if isinstance(raw_output, list):
        issues = raw_output
    elif isinstance(raw_output, dict):
        candidate = raw_output.get("issues", [])
        issues = candidate if isinstance(candidate, list) else []
    else:
        issues = []

    normalized: list[dict[str, Any]] = []
    for issue in issues:
        if isinstance(issue, dict):
            normalized.append(_normalize_issue(issue))
    return normalized


def _raw_code_prompt(code: str) -> str:
    return (
        "You are an elite staff-level reviewer.\n"
        "Goal: find real, high-signal issues only. Be precise and pragmatic.\n\n"
        "Output rules (STRICT):\n"
        "1) Return JSON only, no markdown, no prose.\n"
        "2) Return a JSON array of objects with keys exactly:\n"
        "   type, severity, file, line, title, explanation, suggestion, fixed_code\n"
        "3) type must be one of [bug, performance, security, improvement]\n"
        "4) severity must be one of [low, medium, high]\n"
        "5) file='raw_input' when file is unknown; line can be null.\n\n"
        "Review policy:\n"
        "- Focus on correctness, security, performance, maintainability.\n"
        "- Report only actionable issues with clear user/system impact.\n"
        "- Avoid style-only nits unless they can cause bugs or maintenance risk.\n"
        "- Keep findings concise and concrete.\n"
        "- If no meaningful issues exist, return [].\n\n"
        "For each finding:\n"
        "- title: short and specific.\n"
        "- explanation: what is wrong and why it matters.\n"
        "- suggestion: exact fix direction.\n"
        "- fixed_code: minimal corrected snippet when confidently possible, else null.\n\n"
        f"Code to review:\n{code}"
    )


def _pr_prompt(repo: str, pull_number: int, parsed_files: list[dict[str, Any]]) -> str:
    serialized_diff = json.dumps(parsed_files, indent=2)
    return (
        f"You are an elite staff-level reviewer auditing PR {repo}#{pull_number}.\n"
        "Your mission is to produce high-signal findings only.\n\n"
        "Scope:\n"
        "- Analyze only changed lines and their direct local context in this diff payload.\n"
        "- Do not invent project details that are not present.\n\n"
        "Output rules (STRICT):\n"
        "1) Return JSON only.\n"
        "2) Return a JSON array of objects with keys exactly:\n"
        "   type, severity, file, line, title, explanation, suggestion, fixed_code\n"
        "3) type in [bug, performance, security, improvement]\n"
        "4) severity in [low, medium, high]\n"
        "5) file must match payload paths; line should map to changed line when possible, else null.\n"
        "6) If there are no meaningful issues, return [].\n\n"
        "Prioritization:\n"
        "- High: security vulnerabilities, data corruption/loss, auth/permission bypass,\n"
        "  crashers, correctness bugs with clear impact.\n"
        "- Medium: likely correctness edge-case bugs, significant performance regressions,\n"
        "  reliability risks, missing validation, risky error handling.\n"
        "- Low: maintainability or clarity issues that can lead to future defects.\n\n"
        "Quality bar:\n"
        "- Prefer fewer, stronger findings over many weak ones.\n"
        "- Avoid generic advice; reference concrete code behavior.\n"
        "- Provide minimally invasive fix suggestions.\n"
        "- fixed_code should be a short patch-like snippet when confident, else null.\n\n"
        f"Changed lines payload:\n{serialized_diff}"
    )


def review_raw_code(code: str) -> list[dict[str, Any]]:
    prompt = _raw_code_prompt(code=code)
    output = analyze_code(prompt=prompt)
    return _normalize_output(output)


def review_github_pr(repo: str, pull_number: int) -> list[dict[str, Any]]:
    github_service = GitHubService()
    files = github_service.fetch_pr_files(repo=repo, pull_number=pull_number)
    parsed_files = parse_pr_file_patches(files)
    if not parsed_files:
        raise ValidationServiceError("No reviewable changed lines were found in PR patches.")

    prompt = _pr_prompt(repo=repo, pull_number=pull_number, parsed_files=parsed_files)
    output = analyze_code(prompt=prompt)
    return _normalize_output(output)
