from django.urls import path

from .views import CodeReviewView, GitHubCommentView, GitHubReviewView


urlpatterns = [
    path("review/", CodeReviewView.as_view(), name="review"),
    path("github-review/", GitHubReviewView.as_view(), name="github-review"),
    path("github-comment/", GitHubCommentView.as_view(), name="github-comment"),
]
