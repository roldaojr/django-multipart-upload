from django.contrib import admin
from .models import FileUpload, MutipartFileUpload
from .forms import FileUploadForm


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("name",)
    form = FileUploadForm


@admin.register(MutipartFileUpload)
class MutipartFileUploadAdmin(admin.ModelAdmin):
    list_display = ("name",)
    form = FileUploadForm
