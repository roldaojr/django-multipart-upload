from django.conf import settings as django_settings
from django.forms.widgets import ClearableFileInput
from django.urls import reverse_lazy
from .files import MultipartUploadedFile
from . import settings


class MultipartFileInput(ClearableFileInput):
    template_name = "django_multipart_upload/file_input.html"

    def __init__(self, chunk_size=None, attrs=None):
        super().__init__(attrs)
        self.attrs.setdefault("class", "multipart")
        self.attrs.setdefault("data-upload-url", reverse_lazy(settings.VIEW_NAME))
        self.attrs.setdefault("data-required", self.is_required or "")
        self.attrs.setdefault("data-chunk-size", chunk_size or settings.CHUNK_SIZE)

    def value_from_datadict(self, data, files, name):
        filename = data.get(name, "").split(";")
        if len(filename) > 1:
            original_name, tmp_name = filename
            upload = MultipartUploadedFile(original_name, tmp_name)
            return upload
        return super().value_from_datadict(data, files, name)

    class Media:
        js = [
            f"{django_settings.STATIC_URL}django-multipart-upload/dropzone.js",
            f"{django_settings.STATIC_URL}django-multipart-upload/multipart-file-input.js",
        ]
        css = {
            "screen": [
                f"{django_settings.STATIC_URL}django-multipart-upload/dropzone.css",
                f"{django_settings.STATIC_URL}django-multipart-upload/multipart-file-input.css",
            ]
        }
