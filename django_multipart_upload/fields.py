from django.db.models.fields.files import FieldFile, FileField
from storages.utils import clean_name


class MultipartFieldFile(FieldFile):
    def save(self, name, content, save=True):
        if not hasattr(self.storage, "bucket"):
            return super().save(name, content, save)

        new_name = self.field.generate_filename(self.instance, content.original_name)
        new_name = self.storage._normalize_name(clean_name(new_name))
        # copy file name to new_name
        new_file = self.storage.bucket.Object(new_name)
        new_file.copy_from(CopySource=f"{self.storage.bucket.name}/{content.tmp_name}")
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
