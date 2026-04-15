import re
from typing import Any


HUNK_HEADER_PATTERN = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def extract_changed_lines(patch: str) -> list[dict[str, Any]]:
    """
    Parse a unified diff patch and return only newly added/changed lines.

    Output item shape:
    {"line": int, "content": str}
    """
    changed_lines: list[dict[str, Any]] = []
    current_new_line: int | None = None

    for raw_line in patch.splitlines():
        hunk_match = HUNK_HEADER_PATTERN.match(raw_line)
        if hunk_match:
            current_new_line = int(hunk_match.group(1))
            continue

        if current_new_line is None:
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            changed_lines.append({"line": current_new_line, "content": raw_line[1:]})
            current_new_line += 1
            continue

        if raw_line.startswith("-") and not raw_line.startswith("---"):
            continue

        if raw_line.startswith(" "):
            current_new_line += 1

    return changed_lines


def parse_pr_file_patches(pr_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert GitHub PR files response into LLM-friendly changed-line payload.
    """
    parsed_files: list[dict[str, Any]] = []
    for pr_file in pr_files:
        patch = pr_file.get("patch")
        if not patch:
            continue

        changed_lines = extract_changed_lines(patch)
        if not changed_lines:
            continue

        parsed_files.append(
            {
                "file": pr_file.get("filename"),
                "status": pr_file.get("status"),
                "changed_lines": changed_lines,
            }
        )

    return parsed_files
