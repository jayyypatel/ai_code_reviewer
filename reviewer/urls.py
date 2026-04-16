from django.urls import path

from .views import GitHubCommentView, GitHubReviewView, ReviewRunListView


urlpatterns = [
    path("github-review/", GitHubReviewView.as_view(), name="github-review"),
    path("github-comment/", GitHubCommentView.as_view(), name="github-comment"),
    path("review-runs/", ReviewRunListView.as_view(), name="review-runs"),
]
