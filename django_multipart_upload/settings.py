from typing import Any

from django.conf import settings as django_settings

PREFIX = "MULTIPART_UPLOAD"
VIEW_NAME = "multipart-upload"


def get_setting(name: str, default: Any = None) -> Any:
    return getattr(django_settings, f"{PREFIX}_{name}", default)


TMP_PATH = get_setting("TMP_PATH", "z-uploads.tmp")
CHUNK_SIZE = get_setting("CHUNK_SIZE", 50 * 1024 * 1024)
