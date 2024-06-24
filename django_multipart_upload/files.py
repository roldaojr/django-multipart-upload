from django.core.files import File
from django.core.files.storage import DefaultStorage


class MultipartUploadedFile(File):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """

    def __init__(self, original_name: str, tmp_name: str, *args, **kwargs):
        self.original_name = original_name
        self.filename = tmp_name.lstrip("/")
        storage_class = kwargs.pop("storage_class", DefaultStorage)
        self.storage = storage_class()
        file = self.storage.open(tmp_name.lstrip("/"), "rb")
        # file._commited = True
        super().__init__(file, *args, **kwargs)

    def close(self):
        try:
            self.storage.delete(self.filename)
            return self.file.close()
        except FileNotFoundError:
            # The file was moved or deleted before the tempfile could unlink
            # it. Still sets self.file.close_called and calls
            # self.file.file.close() before the exception.
            pass
