from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    GitHubCommentRequestSerializer,
    GitHubReviewRequestSerializer,
    ReviewRunSerializer,
)
from .models import ReviewRun
from .services.exceptions import AIServiceError, GitHubServiceError, ValidationServiceError
from .services.github_service import GitHubService
from .services.review_engine import review_github_pr


class GitHubReviewView(APIView):
    def post(self, request):
        serializer = GitHubReviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            findings = review_github_pr(
                repo=serializer.validated_data["repo"],
                pull_number=serializer.validated_data["pull_number"],
                user_context=serializer.validated_data.get("user_context", ""),
                pr_url=serializer.validated_data.get("pr_url", ""),
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


class ReviewRunListView(APIView):
    def get(self, request):
        runs = ReviewRun.objects.all()[:20]
        serializer = ReviewRunSerializer(runs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
