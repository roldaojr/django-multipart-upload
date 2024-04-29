from rest_framework import serializers


class StartMultiPartUploadSerializer(serializers.Serializer):
    server_id = serializers.CharField()
    parts_urls = serializers.ListField(child=serializers.CharField())
    complete_url = serializers.CharField()


class UploadPartSerializer(serializers.Serializer):
    PartNumber = serializers.IntegerField()
    ETag = serializers.CharField(allow_null=True, allow_blank=True)


class CompleteMultipartUploadSerializer(serializers.Serializer):
    Parts = UploadPartSerializer(many=True, required=False)
