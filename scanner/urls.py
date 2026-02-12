from django.urls import path
from .views import UploadScanView, ScanDetailView, ScanHistoryView

app_name = "scanner"

urlpatterns = [
    path("", UploadScanView.as_view(), name="upload"),
    path("result/<int:scan_id>/", ScanDetailView.as_view(), name="result"),
    path("history/", ScanHistoryView.as_view(), name="history"),
]
