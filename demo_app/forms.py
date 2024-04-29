from django import forms
from django_multipart_upload.widgets import MultipartFileInput
from .models import FileUpload


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ["name", "file"]
        widgets = {"file": MultipartFileInput()}
