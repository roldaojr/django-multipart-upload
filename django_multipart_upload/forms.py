from django.forms.fields import FileField

from .widgets import MultipartFileInput


class MultipartFileField(FileField):
    widget = MultipartFileInput
