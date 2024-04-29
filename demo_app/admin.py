from django.contrib import admin
from .models import FileUpload
from .forms import FileUploadForm


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("name",)
    form = FileUploadForm
