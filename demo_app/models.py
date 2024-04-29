from django.db import models


class FileUpload(models.Model):
    name = models.CharField(max_length=1000)
    file = models.FileField()
