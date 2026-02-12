from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from root.settings import STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("scanner.urls")),
]

if settings.DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)
