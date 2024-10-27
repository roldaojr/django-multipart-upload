from django.db.models.fields.files import FieldFile, FileField
from storages.utils import clean_name

from .files import MultipartUploadedFile
from .forms import MultipartFileField as MultipartFileFormField
from .settings import DEFAULT_ACL

__all__ = ["MultipartFieldFile", "MultipartFileField"]


class MultipartFieldFile(FieldFile):
    def save(self, name, content, save=True):
        if not hasattr(self.storage, "bucket"):
            return super().save(name, content, save)

        if not isinstance(content, MultipartUploadedFile):
            # is a invalid file do nothing
            return

        original_name = getattr(content, "original_name", content.name)
        tmp_name = getattr(content, "tmp_name", content.name)
        new_name = self.field.generate_filename(self.instance, original_name)
        new_name = self.storage._normalize_name(clean_name(new_name))
        # copy file name to new_name
        self.storage.connection.meta.client.copy(
            {"Bucket": self.storage.bucket_name, "Key": tmp_name},
            self.storage.bucket_name,
            new_name,
        )
        if DEFAULT_ACL:
            self.storage.connection.meta.client.put_object_acl(
                ACL=DEFAULT_ACL,
                Bucket=self.storage.bucket_name,
                Key=new_name,
            )
        # set new name
        self.name = new_name
        setattr(self.instance, self.field.attname, self.name)
        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()

    save.alters_data = True


class MultipartFileField(FileField):
    attr_class = MultipartFieldFile

    def formfield(self, **kwargs):
        return super().formfield(
            form_class=MultipartFileFormField, max_length=self.max_length, **kwargs
        )
