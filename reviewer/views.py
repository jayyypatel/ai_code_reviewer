from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CodeReviewRequestSerializer,
    GitHubCommentRequestSerializer,
    GitHubReviewRequestSerializer,
)
from .services.exceptions import AIServiceError, GitHubServiceError, ValidationServiceError
from .services.github_service import GitHubService
from .services.review_engine import review_github_pr, review_raw_code


class CodeReviewView(APIView):
    def post(self, request):
        serializer = CodeReviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            findings = review_raw_code(code=serializer.validated_data["code"])
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(findings, status=status.HTTP_200_OK)


class GitHubReviewView(APIView):
    def post(self, request):
        serializer = GitHubReviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            findings = review_github_pr(
                repo=serializer.validated_data["repo"],
                pull_number=serializer.validated_data["pull_number"],
            )
        except ValidationServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except GitHubServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except AIServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(findings, status=status.HTTP_200_OK)


class GitHubCommentView(APIView):
    def post(self, request):
        serializer = GitHubCommentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        github_service = GitHubService()
        try:
            comment = github_service.post_pr_comment(
                repo=data["repo"],
                pull_number=data["pull_number"],
                body=data["body"],
                path=data.get("path"),
                line=data.get("line"),
                commit_id=data.get("commit_id"),
            )
        except GitHubServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(comment, status=status.HTTP_201_CREATED)
