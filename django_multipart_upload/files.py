from django.core.files import File
from django.core.files.storage import DefaultStorage
from storages.backends.s3 import S3File


class TemporaryS3File(S3File):
    pass


class MultipartUploadedFile(File):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """

    def __init__(self, original_name: str, tmp_name: str, *args, **kwargs):
        self.original_name = original_name
        self.tmp_name = tmp_name.lstrip("/")
        storage_class = kwargs.pop("storage_class", DefaultStorage)
        self.storage = storage_class()
        if hasattr(self.storage, "bucket"):
            file = TemporaryS3File(tmp_name.lstrip("/"), "rb", self.storage)
        else:
            file = self.storage.open(tmp_name.lstrip("/"), "rb")
        super().__init__(file, name=original_name, *args, **kwargs)
