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
        "Review the following code and return JSON only as a list of issues with keys: "
        "type, severity, file, line, title, explanation, suggestion, fixed_code.\n\n"
        "Use type in [bug, performance, security, improvement], severity in [low, medium, high].\n"
        "If file is unknown use 'raw_input'. line can be null.\n\n"
        f"Code:\n{code}"
    )


def _pr_prompt(repo: str, pull_number: int, parsed_files: list[dict[str, Any]]) -> str:
    serialized_diff = json.dumps(parsed_files, indent=2)
    return (
        f"Review this pull request diff for {repo}#{pull_number}. "
        "Focus only on changed lines.\n"
        "Return JSON only as a list with keys: "
        "type, severity, file, line, title, explanation, suggestion, fixed_code.\n"
        "Use type in [bug, performance, security, improvement], severity in [low, medium, high].\n"
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
