from django.contrib import admin

from .models import ReviewRun


@admin.register(ReviewRun)
class ReviewRunAdmin(admin.ModelAdmin):
    list_display = ("created_at", "repo", "pull_number", "status", "duration_ms")
    list_filter = ("status", "created_at")
    search_fields = ("repo", "pull_number", "pr_url")
    readonly_fields = (
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
    )
