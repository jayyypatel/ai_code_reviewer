class ReviewError(Exception):
    """Base exception for review orchestration failures."""


class ValidationServiceError(ReviewError):
    """Raised when input is valid structurally but unusable semantically."""


class GitHubServiceError(ReviewError):
    """Raised when GitHub API interactions fail."""


class AIServiceError(ReviewError):
    """Raised when AI analysis cannot be completed."""
