from django.conf import settings as django_settings
from django.forms.widgets import ClearableFileInput
from django.urls import reverse_lazy

from . import settings
from .files import MultipartUploadedFile


class MultipartFileInput(ClearableFileInput):
    template_name = "django_multipart_upload/file_input.html"

    def __init__(self, chunk_size=None, attrs=None):
        super().__init__(attrs)
        self.attrs.setdefault("class", "multipart")
        self.attrs.setdefault("data-upload-url", reverse_lazy(settings.VIEW_NAME))
        self.attrs.setdefault("data-required", self.is_required or "")
        self.attrs.setdefault("data-chunk-size", chunk_size or settings.CHUNK_SIZE)

    def value_from_datadict(self, data, files, name):
        print(data)
        filename = data.get(name, "").split(";")
        if len(filename) > 1:
            original_name, tmp_name = filename
        else:
            original_name = filename[0]
            tmp_name = filename[0]
        upload = MultipartUploadedFile(original_name, tmp_name)
        return upload

    def value_omitted_from_data(self, data, files, name):
        name_omitted = not bool(data.get(name, ""))
        return name_omitted and self.clear_checkbox_name(name) not in data

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
