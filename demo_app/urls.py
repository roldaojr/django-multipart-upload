from django.urls import path
from .views import CreateFileUpload, UpdateFileUpload, ListFileUpload, DeleteFileUpload

urlpatterns = [
    path("add", CreateFileUpload.as_view(), name="fileupload-create"),
    path("<int:pk>", UpdateFileUpload.as_view(), name="fileupload-update"),
    path("<int:pk>/delete", DeleteFileUpload.as_view(), name="fileupload-delete"),
    path("", ListFileUpload.as_view(), name="fileupload-list"),
]
