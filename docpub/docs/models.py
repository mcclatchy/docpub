from django.db import models


class BasicInfo(models.Model):
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True, help_text="When the item was first created.")
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, help_text="When the item was last updated.")

    class Meta:
        abstract = True


class Document(BasicInfo):
    description = models.TextField(blank=True, null=True, help_text='Optional (but strongly encouraged) description of the document.')
    file = models.FileField(blank=True, upload_to='uploads/pdf/') ## date: (upload_to='uploads/%Y/%m/%d/')
    link = models.URLField(max_length=255, null=True, blank=True, help_text='Optional and only needed if you want to use a PDF from a URL and not by uploading directly.')
    title = models.CharField(max_length=255, blank=False, null=True, help_text='Short yet descriptive title (e.g. 2017 House budget proposal).')
    source = models.CharField(max_length=255, blank=True, null=True, help_text='Who created this document or from where did you obtain it? Optional, but strongly encouraged if not senstive/confidential source.')

