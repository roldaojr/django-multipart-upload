=======================
django-multipart-upload
=======================

A drop in replacement for Django Admin using django class based views.
The interface made with semantic-ui framework.

The admin uses the following existing django apps.

- django-crispy-forms
- django-filter
- django-simple-menu
- django-tables2

Getting started
===============

``pip install django-multipart-upload``

Or Install from git

``pip install git+https://github.com/roldaojr/django-multipart-upload.git``

Add the following to django settings.py

.. code-block:: python

    installed_apps [
        ...
        "django_multipart_upload"
    ]

Add widget to your form FileField

.. code-block:: python

    from django import forms
    from django_multipart_upload.widgets import MultipartFileInput

    class FileUploadForm(forms.Form):
        file = forms.FileField(widget=MultipartFileInput())
