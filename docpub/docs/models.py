from django.db import models


class Document(models.Model):
	description = models.TextField(blank=True, null=True, help_text='Optional (but strongly encouraged) description of the document.')
	file = models.FileField(upload_to='uploads/pdf/') ## date: (upload_to='uploads/%Y/%m/%d/')
	link = models.URLField(max_length=255, null=True, blank=True, help_text='Optional and only needed if you want to use a PDF from a URL and not by uploading directly.')
	title = models.CharField(blank=False, null=True, help_text='Short yet descriptive title (e.g. 2017 House budget proposal')
	source = models.CharField(blank=True, null=True, help_text='Who created this document or from where did you obtain it? Optional, but strongly encouraged if not senstive/confidential source.')

