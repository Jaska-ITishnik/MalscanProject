import hashlib

import magic
from django.conf import settings
from django.urls import reverse
from django.views.generic import FormView, DetailView, ListView

from mlapp.features import extract_features
from mlapp.model import (
    load_model, load_schema, vectorize, predict_proba,
    verdict_from_score, top_feature_contributions
)
from .forms import UploadForm
from .models import Sample, Scan


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class UploadScanView(FormView):
    template_name = "scanner/upload.html"
    form_class = UploadForm

    def form_valid(self, form):
        uploaded = form.cleaned_data["file"]

        sample = Sample.objects.create(
            original_name=uploaded.name,
            stored_file=uploaded,
            size_bytes=uploaded.size,
            sha256="",
            mime_type="",
        )

        file_path = sample.stored_file.path

        sample.sha256 = sha256_file(file_path)
        try:
            sample.mime_type = magic.from_file(file_path, mime=True) or ""
        except Exception:
            sample.mime_type = ""
        sample.save()

        model = load_model(settings.ML_MODEL_PATH)
        feature_names = load_schema(settings.ML_SCHEMA_PATH)

        with open(file_path, "rb") as f:
            data = f.read()

        features, evidence = extract_features(data, mime_type=sample.mime_type)
        x = vectorize(features, feature_names)
        p = predict_proba(model, x)

        score = int(round(p * 100))
        verdict = verdict_from_score(score)
        top_feats = top_feature_contributions(model, x, feature_names, top_k=8)

        reasons = {"top_features": top_feats, "evidence": evidence}

        scan = Scan.objects.create(
            sample=sample,
            score_percent=score,
            verdict=verdict,
            model_version="v1",
            features_json=features,
            reasons_json=reasons,
        )

        self._scan_id = scan.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("scanner:result", kwargs={"scan_id": self._scan_id})


class ScanDetailView(DetailView):
    model = Scan
    pk_url_kwarg = "scan_id"
    context_object_name = "scan"
    template_name = "scanner/result.html"


class ScanHistoryView(ListView):
    model = Scan
    context_object_name = "scans"
    template_name = "scanner/history.html"
    paginate_by = 50

    def get_queryset(self):
        return Scan.objects.select_related("sample").order_by("-created_at")
