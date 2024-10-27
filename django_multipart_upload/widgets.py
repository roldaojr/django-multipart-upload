from django.conf import settings as django_settings
from django.forms.widgets import (
    FILE_INPUT_CONTRADICTION,
    CheckboxInput,
    ClearableFileInput,
)
from django.urls import reverse_lazy

from . import settings
from .files import MultipartUploadedFile


class MultipartFileInput(ClearableFileInput):
    template_name = "django_multipart_upload/file_input.html"
    is_multipart = True

    def __init__(self, chunk_size=None, attrs=None):
        super().__init__(attrs)
        self.attrs.setdefault("class", "multipart")
        self.attrs.setdefault("data-upload-url", reverse_lazy(settings.VIEW_NAME))
        self.attrs.setdefault("data-required", self.is_required or "")
        self.attrs.setdefault("data-chunk-size", chunk_size or settings.CHUNK_SIZE)

    def value_from_datadict(self, data, files, name):
        filename = data.get(name, "")
        if not filename:
            return

        self.checked = self.clear_checkbox_name(name) in data
        if not self.is_required and CheckboxInput().value_from_datadict(
            data, files, self.clear_checkbox_name(name)
        ):
            if filename:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False

        if ";" in filename:
            original_name, tmp_name = filename.split(";")
        else:
            original_name = filename
            tmp_name = filename

        upload = MultipartUploadedFile(original_name, tmp_name)
        return upload

    def value_omitted_from_data(self, data, files, name):
        name_omitted = not bool(data.get(name))
        return name_omitted and self.clear_checkbox_name(name) not in data

    class Media:
        js = [
            f"{django_settings.STATIC_URL}django-multipart-upload/dropzone.js",
            f"{django_settings.STATIC_URL}django-multipart-upload/multipart-file-input.js",
        ]
        css = {
            "screen": [
                # f"{django_settings.STATIC_URL}django-multipart-upload/dropzone.css",
                f"{django_settings.STATIC_URL}django-multipart-upload/multipart-file-input.css",
            ]
        }
