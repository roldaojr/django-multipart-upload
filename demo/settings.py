import os
from urllib.parse import urlparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-8k5by1+w0334swnj614co8089ce#zwe_*_#tr_-3e=fy4%*rwz"
DEBUG = True
ALLOWED_HOSTS = []
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "demo_app",
    "django_multipart_upload",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "media")
MEDIA_URL = "/media/"

if MEDIA_ROOT.startswith("s3://"):
    # media root is a S3 bucket
    MEDIA_BUCKET_URL = urlparse(MEDIA_ROOT)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = False
    AWS_ACCESS_KEY_ID = MEDIA_BUCKET_URL.username
    AWS_SECRET_ACCESS_KEY = MEDIA_BUCKET_URL.password
    AWS_STORAGE_BUCKET_NAME = MEDIA_BUCKET_URL.path.strip("/")
    AWS_QUERYSTRING_EXPIRE = 3600

    if MEDIA_BUCKET_URL.hostname and MEDIA_BUCKET_URL.hostname != "s3":
        # custom S3 endpoint
        scheme = "http" if MEDIA_BUCKET_URL.query == "insecure" else "https"
        port = MEDIA_BUCKET_URL.port or 80 if scheme == "http" else 443
        AWS_S3_ENDPOINT_URL = f"{scheme}://{MEDIA_BUCKET_URL.hostname}:{port}"
