from django.urls import path, re_path

from . import settings
from .views import MultiPartUploadView

urlpatterns = [
    re_path(
        "(?P<filename>.+)$",
        MultiPartUploadView.as_view(),
        name=settings.VIEW_NAME,
    ),
    path(
        "",
        MultiPartUploadView.as_view(),
        name=settings.VIEW_NAME,
    ),
]
