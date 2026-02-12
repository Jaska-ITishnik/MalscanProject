from django.db import models

class Sample(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_name = models.CharField(max_length=255)
    stored_file = models.FileField(upload_to="uploads/")
    size_bytes = models.BigIntegerField()
    sha256 = models.CharField(max_length=64, db_index=True)
    mime_type = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.original_name} ({self.sha256[:10]}...)"

class Scan(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name="scans")

    score_percent = models.IntegerField()
    verdict = models.CharField(max_length=32)
    model_version = models.CharField(max_length=64, default="v1")

    features_json = models.JSONField(default=dict)
    reasons_json = models.JSONField(default=dict)

    def __str__(self):
        return f"Scan {self.id} - {self.verdict} {self.score_percent}%"
