from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User
from docs.connection import client
from docs.choices import ACCESS_CHOICES
from docpub.settings import DOMAIN, UPLOAD_PATH
from docpub.settings_private import CDN_DOMAIN
# import boto3


##### DOCUMNET METHODS #####
def build_project_list():
    ''' dynamically creates a choices list of two-tuples based on the
    DocumentCloud projects for this account. '''
    projects_list = []
    for project in client.projects.all():
        project_tuple = (project.title, project.title)
        projects_list.append(project_tuple)
    return projects_list

## deletes PDF on file system
def delete_file(self):
    os.remove(self.file.path)

## get a specific document object on DocumentCloud
def documentcloud_object(self):
    if self.documentcloud_id:
        return client.documents.get(self.documentcloud_id)

# update info on documentcloud.org on save
def document_update(self):
    obj = self.documentcloud_object()
    for key, value in self.documentcloud_fields.items():
        setattr(obj, key, value)
    # self.documentcloud_url = obj.canonical_url
    obj.save()

# add info to documentcloud.org on create
def document_upload(self):
    if self.file or self.link:
        if self.link:
            pdf = self.link
        elif self.file:
            pdf = self.file

    kwargs = {
        'title': self.title,
        'source': self.source,
        'description': self.description,
        'related_article': self.related_article,
        'access': self.access,
        'secure': self.secure,
        'project': self.get_project_object(),
    }
    obj = client.documents.upload(pdf, **kwargs)
    self.documentcloud_id = obj.id
    self.documentcloud_url = obj.canonical_url

## generate/update embed code
def generate_embed(self):
    doc_id = self.documentcloud_id
    # doc_title = self.title
    # doc_id_number = doc_id.split('-')[0]
    # doc_title_hyphenated = doc_title.replace(' ', '-')
    doc_sidebar = str(self.sidebar).lower()
    # doc_thumb = self.documentcloud_thumbnail
    # if not doc_thumb:
        # doc_thumb = ''
    # doc_pdf = self.documentcloud_pdf_url
    ## styles for hiding Document Viewer on native apps and showing thumbnail
    # script = '<script>if (!window.jQuery){var embeds=document.getElementsByClassName("doccloud"); var thumbs=document.getElementsByClassName("docthumb"); for (var i=0;i<embeds.length;i++){embeds[i].style.display="none";} for (var i=0;i<thumbs.length;i++){thumbs[i].style.display="inline";}}</script>'
    # embed_prefix = '<style>#DV-viewer-{id} {{ display: inline; }} .docthumb {{ display: none; }}</style><div class="docthumb"><a href="{pdf}"><img src="{thumb}" width="100%" /></a></div>'.format(
        #     id=doc_id,
        #     pdf=doc_pdf,
        #     thumb=doc_thumb
        # )
    ## construct the DocumentCloud embed code wrapped in div we'll hide for apps
    # standard_embed = '<div class="doccloud"><div id="DV-viewer-{id}" class="DC-embed DC-embed-document DV-container"></div><script src="//assets.documentcloud.org/viewer/loader.js"></script><script>DV.load("https://www.documentcloud.org/documents/{id}.js", {{responsive: true, sidebar: {sidebar}, container: "#DV-viewer-{id}"}});</script></div><noscript><a href="https://assets.documentcloud.org/documents/{id_number}/{title_hyphenated}.pdf">{title} (PDF)</a><br /><a href="https://assets.documentcloud.org/documents/{id_number}/{title_hyphenated}.txt">{title} (Text)</a></noscript>'.format(
    #         id=doc_id,
    #         title=doc_title,
    #         id_number=doc_id_number, 
    #         title_hyphenated=doc_title_hyphenated, 
    #         sidebar=doc_sidebar
    #     )
    iframe_embed = '<div><iframe src="https://www.documentcloud.org/documents/{id}.html?sidebar={sidebar}" style="border:none;width:100%;height:500px"></iframe></div>'.format(
            id=doc_id,
            sidebar=doc_sidebar
            # title=doc_title, 
            # id_number=doc_id_number, 
            # title_hyphenated=doc_title_hyphenated, 
        ) # desktop height 930px, mobile height 500px

    # self.embed_code = script + embed_prefix + standard_embed
    self.embed_code = iframe_embed


##### MODELS #####
class BasicInfo(models.Model):
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True, help_text="When the item was first created.")
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, help_text="When the item was last updated.")

    class Meta:
        abstract = True


class Document(BasicInfo):
    access = models.CharField(max_length=255, null=True, choices=ACCESS_CHOICES, verbose_name='Who can see this?', help_text='Should the document be publicly visible or only visible to other users in your DocumentCloud organization?')
    description = models.TextField(blank=True, null=True, help_text='Optional (but strongly encouraged) description of the document.')
    documentcloud_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud ID', help_text='ID of the document on DocumentCloud')
    documentcloud_pdf_url = models.URLField(max_length=255, blank=True, null=True, verbose_name='PDF hosted by DocumentCloud', help_text='Automatically pulled from DocumentCloud after document finishes processing.')
    # documentcloud_thumbnail = models.URLField(max_length=255, blank=True, null=True, verbose_name='Document thumbail', help_text='Pulled from DocumentCloud after document finishes processing.')
    documentcloud_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud URL', help_text='URL of the document on DocumentCloud')
    embed_code = models.TextField(null=True, blank=True, help_text='Copy the full piece of code above.')
    file = models.FileField(blank=True, verbose_name='Upload PDF', help_text='Choose the PDF you want to upload or...', upload_to=UPLOAD_PATH) ## date: (upload_to='uploads/%Y/%m/%d/') ## this path works for uploading, but not when click in admin afterward
    link = models.URLField(max_length=255, null=True, blank=True, verbose_name='Link to PDF', help_text='...paste the URL of a PDF you would like to upload. \
        <br><strong>*** NOTES ***</strong><br> \
        - You can only use one PDF option (upload or link)<br> \
        - The PDF cannot be changed or updated after you hit save for the first time &mdash; no matter which way you add it.')
    messy_text = models.BooleanField(default=False, help_text='Check this box if the "Plain text" is too messy to include or clean up manually. A link to the PDF will be displayed on mobile with no plain text version.')
    project = models.CharField(max_length=255, null=True, blank=True, choices=build_project_list(), help_text='Optional, but helpful. Cannot be updated from here after initially set -- must be changed in DocumentCloud.') ## UPDATE: remove blank=True to make required?
    text = models.TextField(null=True, blank=True, verbose_name='Document text', help_text='Text of the PDF extracted by DocumentCloud. Leave this blank when you first upload the document. It will be filled in automatically. If the plain text does not appear after initially creating/saving here, check on DocumentCloud.org to see if the document is finished processing. When it is done, come back here and click "Save and continue editing" below, then verify the text is filled in here. If you would like, you can clean up the text as needed after it appears here. At any point in the process, the plain text will not be overwritten if there is any text here -- original or modified.')
    title = models.CharField(max_length=255, blank=False, null=True, help_text='Short yet descriptive title (e.g. 2017 House budget proposal).')
    related_article = models.URLField(max_length=255, blank=True, null=True, help_text='Optional link to the story this document relates to.')
    secure = models.BooleanField(blank=True, default=False, help_text='Is this document sensitive or should it not be sent to third-party services (e.g. OpenCalais for text analysis)?')
    sidebar = models.BooleanField(blank=True, default=False, verbose_name='Enable document viewer sidebar?', help_text='Not recommended for article page embeds.')
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name='Source name', help_text='What organization, person, etc. created this document? Optional, but strongly encouraged if not a senstive/confidential.')

    def documentcloud_url_formatted(self):
        link = '-'
        if self.documentcloud_id:
            link = format_html('<a href="{}">View/edit on DocumentCloud</a>'.format(self.documentcloud_url))
        return link
    documentcloud_url_formatted.short_description = 'DocumentCloud link'

    ## get a specific document object on DocumentCloud
    def documentcloud_object(self):
        if self.documentcloud_id:
            return client.documents.get(self.documentcloud_id)

    def get_project_object(self):
        if self.project:
            project = client.projects.get_by_title(self.project)
            return str(project.id)

    # map django model fields to documentcloud.org fields
    @property
    def documentcloud_fields(self):
        return {
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'access': self.access,
            'secure': self.secure,
            'related_article': self.related_article,
            'project': self.get_project_object(),
        }

    ## create a button in the admin listview for users to copy a specific embed code
    # def copy_embed_code(self):
        # or put this in admin.py?

    def save(self, *args, **kwargs):
        if self.updated:
            document_update(self)
        else:
            document_upload(self)
        ## abstract to get_doc_id() function or function with a while loop?
        if documentcloud_object(self):
            obj = documentcloud_object(self)
            self.documentcloud_pdf_url = obj.pdf_url
            ## grab the text unless messy text is selected
            # if not self.messy_text:
            #     self.text = obj.full_text
            ## generate the embed
            generate_embed(self)
        return super(Document, self).save(*args, **kwargs)
        ## if we're going to use delete_file(self), include here and then do another return super to save?

    class Meta:
        ordering = ['-created'] # updated might get confusing, but could be more helpful

    def __str__(self):
        return self.title

## in save method? post save? for text, etc -- anything else that wouldn't initially be available
    # obj = client.documents.get(obj.id)
    # while obj.access != 'public':
    #     time.sleep(5)
    #     obj = client.documents.get(obj.id)
    ## we'd also want to grab doc text and thumbnail
    # obj.full_text
    # obj.pdf_url
