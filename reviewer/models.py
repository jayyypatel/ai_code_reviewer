from django.db import models


class ReviewRun(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    repo = models.CharField(max_length=255)
    pull_number = models.PositiveIntegerField()
    pr_url = models.URLField(blank=True)
    user_context = models.TextField(blank=True)
    changed_lines_payload = models.JSONField(default=list)
    prompt_sent = models.TextField()
    raw_ai_output = models.JSONField(null=True, blank=True)
    normalized_findings = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.repo}#{self.pull_number} ({self.status})"
