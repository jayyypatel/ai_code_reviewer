import re
from urllib.parse import urlparse

from rest_framework import serializers

from .models import ReviewRun


REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PR_URL_PATTERN = re.compile(r"^/([^/]+)/([^/]+)/pull/(\d+)$")


class CodeReviewRequestSerializer(serializers.Serializer):
    code = serializers.CharField(allow_blank=False, trim_whitespace=False)


class GitHubReviewRequestSerializer(serializers.Serializer):
    repo = serializers.CharField(required=False, allow_blank=False)
    pull_number = serializers.IntegerField(required=False, min_value=1)
    pr_url = serializers.URLField(required=False)
    user_context = serializers.CharField(required=False, allow_blank=True, max_length=4000)

    def validate_repo(self, value: str) -> str:
        if not REPO_PATTERN.match(value):
            raise serializers.ValidationError("repo must be in the format owner/repo.")
        return value

    def validate(self, attrs):
        pr_url = attrs.get("pr_url")
        repo = attrs.get("repo")
        pull_number = attrs.get("pull_number")

        if pr_url:
            parsed = urlparse(pr_url)
            if parsed.netloc not in {"github.com", "www.github.com"}:
                raise serializers.ValidationError({"pr_url": "Only github.com PR URLs are supported."})
            match = PR_URL_PATTERN.match(parsed.path.rstrip("/"))
            if not match:
                raise serializers.ValidationError({"pr_url": "PR URL must be like https://github.com/owner/repo/pull/123"})
            owner, repo_name, pull_number_str = match.groups()
            attrs["repo"] = f"{owner}/{repo_name}"
            attrs["pull_number"] = int(pull_number_str)
            return attrs

        if not repo or pull_number is None:
            raise serializers.ValidationError(
                "Provide either pr_url or both repo and pull_number."
            )
        return attrs


class GitHubCommentRequestSerializer(serializers.Serializer):
    repo = serializers.CharField()
    pull_number = serializers.IntegerField(min_value=1)
    body = serializers.CharField(allow_blank=False)
    path = serializers.CharField(required=False, allow_blank=False)
    line = serializers.IntegerField(required=False, min_value=1, allow_null=False)
    commit_id = serializers.CharField(required=False, allow_blank=False)

    def validate_repo(self, value: str) -> str:
        if not REPO_PATTERN.match(value):
            raise serializers.ValidationError("repo must be in the format owner/repo.")
        return value

    def validate(self, attrs):
        path = attrs.get("path")
        line = attrs.get("line")
        commit_id = attrs.get("commit_id")

        # Line-level review comments on GitHub require file path, line number, and commit SHA.
        any_inline = any(item is not None for item in (path, line, commit_id))
        all_inline = all(item is not None for item in (path, line, commit_id))
        if any_inline and not all_inline:
            raise serializers.ValidationError(
                "To post an inline comment, provide path, line, and commit_id together."
            )
        return attrs


class ReviewRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRun
        fields = [
            "id",
            "repo",
            "pull_number",
            "pr_url",
            "user_context",
            "changed_lines_payload",
            "prompt_sent",
            "raw_ai_output",
            "normalized_findings",
            "status",
            "error_message",
            "duration_ms",
            "created_at",
        ]
