from django.db import models
from django.contrib.auth.models import User
from docpub.settings import UPLOAD_PATH, EMBED_CSS
from docs.choices import ACCESS_CHOICES, NEWSROOM_CHOICES
# from s3direct.fields import S3DirectField


##### GENERAL FUNCTIONS #####

def build_project_list(client):
    """ dynamically create a choices list based on the Document Cloud projects for the associated account """
    projects_list = []
    for project in client.projects.all():
        project_tuple = (project.title, project.title)
        projects_list.append(project_tuple)
    return projects_list

def delete_file(self):
    """ delete PDF on file system """
    os.remove(self.file.path)


##### MODELS #####
class BasicInfo(models.Model):
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True, help_text="When the item was first created.")
    updated = models.DateTimeField(blank=True, null=True, auto_now=True, help_text="When the item was last updated.")

    class Meta:
        abstract = True


class DocumentSet(BasicInfo):
    name = models.CharField(max_length=255, null=True, blank=False)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Document set'

    def __str__(self):
        return self.name


class Document(BasicInfo):
    access = models.CharField(max_length=255, null=True, choices=ACCESS_CHOICES, verbose_name='Who can see this?', help_text='Should the document be publicly visible or only visible to other users in your DocumentCloud organization?')
    account = models.CharField(max_length=100, null=True, blank=True, verbose_name='Who owns this doc?', help_text='This can\'t be changed')
    description = models.TextField(blank=True, null=True, help_text='Optional (but strongly encouraged) description of the document. <strong>PUBLIC</strong>')
    document_set = models.ForeignKey(DocumentSet, null=True, blank=True)
    documentcloud_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud ID', help_text='ID of the document on DocumentCloud')
    documentcloud_pdf_url = models.URLField(max_length=255, blank=True, null=True, verbose_name='PDF hosted by DocumentCloud', help_text='Automatically pulled from DocumentCloud after document finishes processing.')
    # documentcloud_thumbnail = models.URLField(max_length=255, blank=True, null=True, verbose_name='Document thumbail', help_text='Pulled from DocumentCloud after document finishes processing.')
    documentcloud_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud URL', help_text='URL of the document on DocumentCloud')
    embed_code = models.TextField(null=True, blank=True) # , help_text='Copy the full piece of code above.'
    # file = S3DirectField(dest='mccdata', blank=True, null=True, help_text='Choose the PDF you want to upload or...')
    file = models.FileField(blank=True, verbose_name='Upload PDF', help_text='Choose the PDF you want to upload or...', upload_to=UPLOAD_PATH) ## date: (upload_to='uploads/%Y/%m/%d/') ## this path works for uploading, but not when click in admin afterward
    link = models.URLField(max_length=255, null=True, blank=True, verbose_name='Link to PDF', help_text='...paste the URL of a PDF you would like to upload. \
        <br><strong>*** NOTES ***</strong><br> \
        - You can only use one PDF option (upload or link)<br> \
        - The PDF cannot be changed or updated after you hit save for the first time &mdash; no matter which way you add it. <strong>PUBLIC</strong>')
    messy_text = models.BooleanField(default=False, help_text='Check this box if the "Plain text" is too messy to include or clean up manually. A link to the PDF will be displayed on mobile with no plain text version.')
    newsroom = models.CharField(max_length=255, null=True, blank=True, choices=NEWSROOM_CHOICES, help_text='If left blank, it will set the newsroom based on the domain of the email account you use for this tool.')
    # project = models.CharField(max_length=255, null=True, blank=True, choices=build_project_list(client), help_text='Optional, but helpful. Cannot be updated from here after initially set -- must be changed in DocumentCloud.') ## UPDATE: remove blank=True to make required?
    related_article = models.URLField(max_length=255, blank=True, null=True, help_text='Optional link to the story this document relates to. <strong>PUBLIC</strong>')
    secure = models.BooleanField(blank=True, default=False, help_text='Is this document sensitive or should it not be sent to third-party services (e.g. OpenCalais for text analysis)?')
    sidebar = models.BooleanField(blank=True, default=False, verbose_name='Enable document viewer sidebar?', help_text='Not recommended for article page embeds. This really only works well when used with a full-width template.')
    source = models.CharField(max_length=255, blank=True, null=True, verbose_name='Source name', help_text='What organization, person, etc. created this document? Optional, but strongly encouraged if not a senstive/confidential. <strong>PUBLIC</strong>')
    text = models.TextField(null=True, blank=True, verbose_name='Document text', help_text='Text of the PDF extracted by DocumentCloud. Leave this blank when you first upload the document. It will be filled in automatically. If the plain text does not appear after initially creating/saving here, check on DocumentCloud.org to see if the document is finished processing. When it is done, come back here and click "Save and continue editing" below, then verify the text is filled in here. If you would like, you can clean up the text as needed after it appears here. At any point in the process, the plain text will not be overwritten if there is any text here -- original or modified.')
    title = models.CharField(max_length=255, blank=False, null=True, help_text='Short yet descriptive title (e.g. 2017 House budget proposal). <strong>PUBLIC</strong>')
    uploaded_by = models.CharField(max_length=255, null=True, blank=True, help_text='If left blank and your name is not entered on your user profile, then it will grab the first part of your email address (specifically, everything before the @ symbol). You can update this later.')
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='Document owned by', help_text='Which account was used to upload this document?')

    class Meta:
        ordering = ['-created'] # updated might get confusing, but could be more helpful

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # if self.updated:
        #     self.document_update()
        # else:
        #     self.document_upload()
        ## abstract to get_doc_id() function or function with a while loop?
        try:
            obj = documentcloud_object(self, client)
            self.documentcloud_pdf_url = obj.pdf_url
            ## grab the text unless messy text is selected
            # if not self.messy_text:
            #     self.text = obj.full_text
        except:
            pass
        return super(Document, self).save(*args, **kwargs)
        ## if we're going to use delete_file(self), include here and then do another return super to save?

    def data_dict(self):
        """ add key-value pairs to document on DocumentCloud """
        newsrooms = dict(NEWSROOM_CHOICES)
        return {
            'uploaded_by': self.uploaded_by,
            'newsroom': newsrooms[self.newsroom],
        }

    def document_update(self, client):
        """ update info on DocumentCloud on save """
        obj = self.documentcloud_object(client)
        for key, value in self.documentcloud_fields.items():
            setattr(obj, key, value)
        # self.documentcloud_url = obj.canonical_url
        obj.save()

    def document_upload(self, client):
        """ add info to DocumentCloud on create """
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
            # 'project': self.get_project_object(),
            'data': self.data_dict() #{'uploaded_by': 'username', 'newsroom': 'McClatchy'},
        }
        obj = client.documents.upload(pdf, **kwargs)
        self.documentcloud_id = obj.id
        self.documentcloud_url = obj.canonical_url

    def documentcloud_object(self, client):
        """ retrieve a specific document object on DocumentCloud """
        if self.documentcloud_id:
            return client.documents.get(self.documentcloud_id)

    def get_project_object(self, client):
        """ retrieve a specific project on DocumentCloud """
        if self.project:
            project = client.projects.get_by_title(self.project)
            return str(project.id)

    @property
    def documentcloud_fields(self):
        """ map Document model fields to DocumentCloud fields """
        return {
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'access': self.access,
            'secure': self.secure,
            'related_article': self.related_article,
            # 'project': self.get_project_object(),
            'data': self.data_dict() # {'uploaded_by': 'username', 'newsroom': 'McClatchy'},
        }

    def generate_embed(self):
        """ generate the embed code """
        doc_id = self.documentcloud_id
        doc_sidebar = str(self.sidebar).lower()
        style_embed = '<link rel="stylesheet" type="text/css" href="{css}">'.format(css=EMBED_CSS)
        iframe_embed = '<div><iframe class="docpubEmbed" src="https://www.documentcloud.org/documents/{id}.html?sidebar={sidebar}"></iframe></div>'.format(
                id=doc_id,
                sidebar=doc_sidebar
            ) # style="border:none;width:100%;height:500px" # desktop height 930px, mobile height 500px
        self.embed_code = style_embed + iframe_embed

## in save method? post save? for text, etc -- anything else that wouldn't initially be available
    # obj = client.documents.get(obj.id)
    # while obj.access != 'public':
    #     time.sleep(5)
    #     obj = client.documents.get(obj.id)
    ## we'd also want to grab doc text and thumbnail
    # obj.full_text
    # obj.pdf_url


class DocumentCloudCredentials(BasicInfo):
    # email = models.EmailField(max_length=254, help_text='Email address for user in DocPub must be the same as DocumentCloud email address.')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='DocumentCloud password')

    class Meta:
        ordering = ['-created'] # updated might get confusing, but could be more helpful
        verbose_name = 'DocumentCloud account info'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username

