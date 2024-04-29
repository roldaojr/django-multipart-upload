from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from .forms import FileUploadForm
from .models import FileUpload


class FileUploadMixin:
    model = FileUpload
    success_url = reverse_lazy("fileupload-list")


class CreateFileUpload(FileUploadMixin, CreateView):
    form_class = FileUploadForm


class UpdateFileUpload(FileUploadMixin, UpdateView):
    form_class = FileUploadForm


class ListFileUpload(FileUploadMixin, ListView):
    pass


class DeleteFileUpload(FileUploadMixin, DeleteView):
    pass
