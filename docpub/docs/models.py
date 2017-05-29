from django.db import models
from docs.connection import client
from docs.choices import ACCESS_CHOICES
from django.utils.html import format_html
from django.contrib import messages


class BasicInfo(models.Model):
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True, help_text="When the item was first created.")
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, help_text="When the item was last updated.")

    class Meta:
        abstract = True


def build_project_list():
    ''' dynamically creates a choices list of two-tuples based on the
    DocumentCloud projects for this account. '''
    projects_list = []
    for project in client.projects.all():
        project_tuple = (project.title, project.title)
        projects_list.append(project_tuple)
    return projects_list

# update info on documentcloud.org on save
def document_update(self):
    obj = self.document_cloud_object()
    for key, value in self.document_cloud_fields.items():
        setattr(obj, key, value)
    obj.save()

# add info to documentcloud.org on create
def document_upload(self):
    try:
        if self.file:
            pdf = self.file
        elif self.link:
            pdf = self.link
    except:
        messages.error(request, 'You must upload a file or include a URL to a PDF')
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
    doc_title = self.title
    doc_id_number = doc_id.split('-')[0]
    doc_title_hyphenated = doc_title.replace(' ', '-')
    doc_sidebar = str(self.sidebar).lower()
    # self.embed_code = '<div id="DV-viewer-' + doc_id + '" class="DC-embed DC-embed-document DV-container"></div><script src="//assets.documentcloud.org/viewer/loader.js"></script><script>DV.load("https://www.documentcloud.org/documents/' + doc_id + '.js", {responsive: true, sidebar: ' + str(self.sidebar).lower() + ', container: "#DV-viewer-' + doc_id + '"});</script><noscript><a href="https://assets.documentcloud.org/documents/' + doc_id_number + '/' + doc_title_hyphenated + '.pdf">' + doc_title + ' (PDF)</a><br /><a href="https://assets.documentcloud.org/documents/' + doc_id_number + '/' + doc_title_hyphenated + '.txt">' + doc_title + ' (Text)</a></noscript>'
    # self.embed_code = self.documentcloud_url
    self.embed_code = '<div id="DV-viewer-{id}" class="DC-embed DC-embed-document DV-container"></div><script src="//assets.documentcloud.org/viewer/loader.js"></script><script>DV.load("https://www.documentcloud.org/documents/{id}.js", {{responsive: true, sidebar: {sidebar}, container: "#DV-viewer-{id}"}});</script><noscript><a href="https://assets.documentcloud.org/documents/{id_number}/{title_hyphenated}.pdf">{title} (PDF)</a><br /><a href="https://assets.documentcloud.org/documents/{id_number}/{title_hyphenated}.txt">{title} (Text)</a></noscript>'.format(id=doc_id, title=doc_title, id_number=doc_id_number, title_hyphenated=doc_title_hyphenated, sidebar=doc_sidebar)
    ## example original
    # self.embed_code = '<div id="DV-viewer-3497784-American-Health-Care-Act" class="DC-embed DC-embed-document DV-container"></div><script src="//assets.documentcloud.org/viewer/loader.js"></script><script>  DV.load("https://www.documentcloud.org/documents/3497784-American-Health-Care-Act.js", {  responsive: true,    sidebar: false,    container: "#DV-viewer-3497784-American-Health-Care-Act"  });</script><noscript>  <a href="https://assets.documentcloud.org/documents/3497784/American-Health-Care-Act.pdf">American Health Care Act (PDF)</a>  <br />  <a href="https://assets.documentcloud.org/documents/3497784/American-Health-Care-Act.txt">American Health Care Act (Text)</a></noscript>'


class Document(BasicInfo):
    access = models.CharField(max_length=255, null=True, choices=ACCESS_CHOICES, help_text='Should the document be visible publicly or only to other users in your DocumentCloud organization.')
    description = models.TextField(blank=True, null=True, help_text='Optional (but strongly encouraged) description of the document.')
    documentcloud_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud ID', help_text='ID of the document on DocumentCloud')
    documentcloud_url = models.URLField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud URL', help_text='URL of the document on DocumentCloud')
    embed_code = models.TextField(null=True, blank=True, help_text='Copy the full piece of code above.')
    file = models.FileField(blank=True, verbose_name='Upload PDF', help_text='Choose the PDF you want to upload or...', upload_to='uploads/pdf/') ## date: (upload_to='uploads/%Y/%m/%d/')
    link = models.URLField(max_length=255, null=True, blank=True, verbose_name='Link to PDF', help_text='...paste the URL of a PDF you would like to upload.')
    messy_text = models.BooleanField(default=False, help_text='Check this box if the "Plain text" is too messy to include or clean up manually. A link to the PDF will be displayed on mobile with no plain text version.')
    project = models.CharField(max_length=255, null=True, blank=True, choices=build_project_list(), help_text='Cannot be updated from here after initially set -- must be changed in DocumentCloud.') ## UPDATE: remove blank=True to make required
    text = models.TextField(null=True, blank=True, verbose_name='Document text', help_text='Text of the PDF extracted by DocumentCloud. Leave this blank when you first upload the document. It will be filled in automatically. If the plain text does not appear after initially creating/saving here, check on DocumentCloud.org to see if the document is finished processing. When it is done, come back here and click "Save and continue editing" below, then verify the text is filled in here. If you would like, you can clean up the text as needed after it appears here. At any point in the process, the plain text will not be overwritten if there is any text here -- original or modified.')
    title = models.CharField(max_length=255, blank=False, null=True, help_text='Short yet descriptive title (e.g. 2017 House budget proposal).')
    related_article = models.URLField(max_length=255, blank=True, null=True, help_text='Optional link to the story this document relates to.')
    secure = models.BooleanField(blank=True, default=False, help_text='Is this document sensitive or should it not be sent to third-party services (e.g. OpenCalais for text analysis)?')
    sidebar = models.BooleanField(blank=True, default=False, verbose_name='Enable document viewer sidebar?', help_text='Not recommended for article page embeds.')
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name='Source name', help_text='What organization, person, etc. created this document? Optional, but strongly encouraged if not a senstive/confidential.')

    # def format_embed_code(self):
    #     return format_html('{}'.format(self.embed_code))

    def document_admin_url(self):
        return format_html('<a href="{}">View on Document Cloud</a>'.format(self.documentcloud_url))

    def get_project_object(self):
        project = client.projects.get_by_title(self.project)
        return str(project.id)

    def document_cloud_object(self):
        return client.documents.get(self.documentcloud_id)

    # map django model fields to documentcloud.org fields
    @property
    def document_cloud_fields(self):
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
        ## abstract to get_doc_id() function?
        # self.documentcloud_id = obj.id
        if self.documentcloud_id:
            generate_embed(self)
        return super(Document, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created'] # updated might get confusing, but could be more helpful

    def __str__(self):
        return self.title

## post save? for text, etc -- anything else that wouldn't initially be available
    # obj = client.documents.get(obj.id)
    # while obj.access != 'public':
    #     time.sleep(5)
    #     obj = client.documents.get(obj.id)
