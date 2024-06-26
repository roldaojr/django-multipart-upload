from urllib.parse import quote
from django.conf import settings as django_settings
from django.urls import reverse
from django.core.exceptions import BadRequest
from django.utils.crypto import get_random_string
from django.core.files.storage import DefaultStorage, Storage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, FileUploadParser
from rest_framework.exceptions import NotFound
from .serializers import (
    CompleteMultipartUploadSerializer,
)
from . import settings


class BaseMultipartUploader:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def init_multipart_upload(self, filename: str, part_count: int) -> Response:
        raise NotImplemented()

    def put_multipart_upload(
        self, filename: str, upload_id: str, part_num: int, file_data
    ) -> Response:
        raise NotImplemented()

    def complete_multipart_upload(
        self, filename: str, upload_id: str, parts_data: dict
    ) -> Response:
        raise NotImplemented()

    def abort_multipart_upload(self, filename: str, upload_id: str) -> Response:
        raise NotImplemented()


class BasicMultipartUploader(BaseMultipartUploader):
    def get_tmp_upload_path(self, upload_id, part_num=None):
        file_path = [settings.TMP_PATH, upload_id]
        if part_num:
            file_path.append(f"{part_num}")
        return "/".join(file_path)

    def init_multipart_upload(self, filename: str, part_count: int) -> Response:
        upload_id = get_random_string(32)
        upload_urls = [
            "{}?uploadId={}&partNumber={}".format(
                reverse(settings.VIEW_NAME, kwargs=dict(filename=filename)),
                upload_id,
                part_num + 1,
            )
            for part_num in range(part_count)
        ]

        return Response(
            {
                "server_id": filename,
                "parts_urls": upload_urls,
                "complete_url": "{}?uploadId={}".format(
                    reverse(settings.VIEW_NAME, kwargs=dict(filename=filename)),
                    upload_id,
                ),
            },
            headers={"Cache-control": "no-cache"},
        )

    def put_multipart_upload(self, filename, upload_id, part_num, file_data):
        part_file_path = self.get_tmp_upload_path(upload_id, part_num)
        self.storage.save(part_file_path, file_data)
        return Response(headers={"ETag": ""})

    def complete_multipart_upload(self, filename, upload_id, parts_data):
        uploaded_parts = [
            self.get_tmp_upload_path(upload_id, part["PartNumber"])
            for part in sorted(parts_data["Parts"], key=lambda p: p["PartNumber"])
        ]
        with self.storage.open(filename.lstrip("/"), "wb+") as full_file:
            for part_file in uploaded_parts:
                with self.storage.open(part_file, "rb+") as part:
                    full_file.write(part.read())
                self.storage.delete(part_file)
        full_file.close()
        # delete temp upload data
        self.storage.delete(self.get_tmp_upload_path(upload_id))

        # File upload complete
        return Response({"Location": f"{django_settings.MEDIA_URL}{filename}"})

    def abort_multipart_upload(self, filename, upload_id):
        self.storage.delete(self.get_tmp_upload_path(upload_id))
        return Response(status=204)


class S3MultipartUploader(BaseMultipartUploader):
    def init_multipart_upload(self, filename, part_count):
        upload_id = get_random_string(32)
        filename = f"z-uploads.tmp/{upload_id}.tmp"
        bucket_object = self.storage.bucket.Object(filename)
        upload = bucket_object.initiate_multipart_upload(
            **self.storage._get_write_parameters(bucket_object.key)
        )
        upload_urls = [
            upload.meta.client.generate_presigned_url(
                ClientMethod="upload_part",
                Params={
                    "Bucket": upload.bucket_name,
                    "Key": upload.object_key,
                    "PartNumber": partN + 1,
                    "UploadId": upload.id,
                },
                ExpiresIn=3600,
            )
            for partN in range(part_count)
        ]
        return Response(
            {
                "server_id": filename,
                "parts_urls": upload_urls,
                "complete_url": "{}?uploadId={}".format(
                    reverse(
                        settings.VIEW_NAME,
                        kwargs=dict(filename=quote(filename)),
                    ),
                    upload.id,
                ),
            },
            headers={"Cache-control": "no-cache"},
        )

    def put_multipart_upload(self, filename, upload_id, part_num, file_data):
        raise BadRequest("put_multipart_upload not available for S3 uploads.")

    def complete_multipart_upload(self, filename, upload_id, parts_data):
        try:
            result = self.storage.connection.meta.client.complete_multipart_upload(
                Bucket=self.storage.bucket.name,
                Key=filename,
                UploadId=upload_id,
                MultipartUpload=dict(parts_data),
            )
            return Response({"ETag": result["ETag"], "Location": result["Location"]})
        except Exception as ex:
            if type(ex).__name__ != "NoSuchUpload":
                raise ex
            raise NotFound("Upload with id not found")

    def abort_multipart_upload(self, filename, upload_id):
        result = self.storage.connection.meta.client.abort_multipart_upload(
            Bucket=self.storage.bucket.name, Key=filename, UploadId=upload_id
        )
        return Response({"ETag": result["ETag"], "Location": result["Location"]})


class MultiPartUploadView(APIView):
    parser_classes = [JSONParser, FormParser, FileUploadParser]
    permission_classes = settings.get_setting("PERMISSION_CLASSES", [])

    def __init__(self, *args, **kwargs) -> None:
        storage_class = kwargs.pop("storage_class", DefaultStorage)
        self.storage = storage_class()
        super().__init__(*args, **kwargs)
        # detect if is S3 storage backend
        if hasattr(self.storage, "get_cloudfront_signer"):
            self.uploader = S3MultipartUploader(self.storage)
        else:
            self.uploader = BasicMultipartUploader(self.storage)

    def get(self, request, filename=None, *args, **kwargs):
        self.request = request
        # create django multi part upload
        if not filename:
            raise BadRequest("Invalid file name")
        try:
            part_count = int(request.GET.get("partCount"))
        except TypeError:
            raise BadRequest("Invalid part count")
        return self.uploader.init_multipart_upload(filename, part_count)

    def put(self, request, filename, *args, **kwargs):
        try:
            upload_id = request.GET["uploadId"]
            part_num = int(request.GET["partNumber"])
        except KeyError or TypeError:
            raise BadRequest("Invalid uploadId or partNumber")
        return self.uploader.put_multipart_upload(
            filename, upload_id, part_num, request.data["file"]
        )

    def post(self, request, filename, *args, **kwargs):
        if "uploads" in request.GET:
            # init multipart upload
            return self.uploader.init_multipart_upload(filename)
        elif "uploadId" in request.GET:
            # complete multi-part upload
            upload_id = request.GET.get("uploadId", None)
            serializer = CompleteMultipartUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return self.uploader.complete_multipart_upload(
                filename, upload_id, dict(serializer.data)
            )

    def delete(self, request, filename, *args, **kwargs):
        """Cancel multipart upload"""
        try:
            upload_id = request.GET["uploadId"]
        except KeyError:
            raise BadRequest("Invalid upload id")
        return self.uploader.abort_multipart_upload(filename, upload_id)
