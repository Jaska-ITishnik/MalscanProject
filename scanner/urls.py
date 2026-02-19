from django.urls import path
from .views import HomeView, UploadScanView, ScanDetailView, HistoryView

app_name = "scanner"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("scan/", UploadScanView.as_view(), name="upload"),
    path("history/", HistoryView.as_view(), name="history"),
    path("scan/<int:pk>/", ScanDetailView.as_view(), name="scan_detail"),
]
