from django.contrib import admin
from .models import Sample, Scan

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "sha256", "size_bytes", "mime_type", "uploaded_at")
    search_fields = ("original_name", "sha256")

@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("id", "verdict", "score_percent", "model_version", "created_at", "sample")
    list_filter = ("verdict", "model_version")
