from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("uploads", include("django_multipart_upload.urls")),
    path("", include("demo_app.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
