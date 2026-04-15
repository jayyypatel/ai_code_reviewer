import re

from rest_framework import serializers


REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class CodeReviewRequestSerializer(serializers.Serializer):
    code = serializers.CharField(allow_blank=False, trim_whitespace=False)


class GitHubReviewRequestSerializer(serializers.Serializer):
    repo = serializers.CharField()
    pull_number = serializers.IntegerField(min_value=1)

    def validate_repo(self, value: str) -> str:
        if not REPO_PATTERN.match(value):
            raise serializers.ValidationError("repo must be in the format owner/repo.")
        return value


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
