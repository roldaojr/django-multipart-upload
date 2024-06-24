from django.db import models
from django_multipart_upload.fields import MultipartFileField


class FileUpload(models.Model):
    name = models.CharField(max_length=1000)
    file = models.FileField(upload_to="files/")


class MutipartFileUpload(models.Model):
    name = models.CharField(max_length=1000)
    file = MultipartFileField(upload_to="files/")
