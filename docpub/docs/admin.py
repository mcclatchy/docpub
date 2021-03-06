from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.contrib import messages
import sys #, traceback
from urllib.error import HTTPError
from docpub.settings import COMPANY, DC_USERNAME, DC_PASSWORD, DOCPUBENV, TEST_PDF
from .models import Document, DocumentCloudCredentials, DocumentSet
from docs.connection import connection
from docs.choices import NEWSROOM_CHOICES
from docs.decryption import decryption
from docs.forms import PasswordInline
from docs.slackbot import slackbot


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Key details'.upper(), {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source',) #'project', 'copy_embed_code',
        }),
        ('Embed code + live link'.upper(), {
            'fields': ('embed_code', 'copy_embed_code', 'documentcloud_url_formatted', 'copy_pdf_link')
        }),
        ('About this document'.upper(), {
            'fields': ('user', 'account', 'newsroom',) #'project', 'copy_embed_code',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article',)
        })
    )
    list_display = ('title', 'created', 'access', 'copy_embed_code',) # , 'documentcloud_url_formatted', 'source'
    list_editable = ('access',)
    list_filter = ('access', 'updated', 'created') # 'project', 'updated', 'created',
    search_fields = ('title', 'user__username')
    readonly_fields = ('account', 'copy_embed_code', 'documentcloud_url_formatted', 'embed_code', 'user', 'copy_pdf_link') # 'documentcloud_id'
    actions = ('generate_embed_codes')
    save_on_top = True

    def copy_embed_code(self, obj):
        """ create a button in the admin for users to copy a specific embed code """
        if obj.documentcloud_id:
            embed_code = obj.embed_code
            html = '<a class=\'button copyCode\' data-clipboard-action=\'copy\' data-clipboard-text=\'{code}\' href=\'#\' onclick=\'copy(); return false;\'>Copy embed code</a>'.format(code=embed_code)
            button = format_html(html)
        else:
            button = '-'
        return button

    def copy_pdf_link(self, obj):
        """ create a button in the admin for users to copy a link to the PDF hosted by DocumentCloud """
        if obj.documentcloud_id:
            if obj.documentcloud_pdf_url:
                pdf = obj.documentcloud_pdf_url
            else:
                pdf = obj.documentcloud_url.replace('.html', '.pdf')
            html = '<a class=\'button copyCode\' data-clipboard-action=\'copy\' data-clipboard-text=\'{code}\' href=\'#\' onclick=\'copy(); return false;\'>Copy URL to PDF</a>'.format(code=pdf)
            button = format_html(html)
        else:
            button = '-'
        return button
    copy_pdf_link.short_description = 'Copy PDF link'

    def documentcloud_url_formatted(self, obj):
        """ display the DocumentCloud URL as a clickable link in the admin"""
        if obj.documentcloud_id:
            message = ''
            spaces = '&nbsp;' * 5
            if obj.account == 'shared':
                message = '<p style="margin-top:10px;"><strong>NOTE:</strong> Because this was uploaded to the shared account, you will not be able to edit it. Also, it will not be visible to you if it is not set to "Public" access.</p>'
            link = format_html('\
                <a class="button" href="{url}" target="_blank">View/edit on DocumentCloud</a>\
                {spaces}\
                <a class=\'button copyCode\' data-clipboard-action=\'copy\' data-clipboard-text=\'{url}\' href=\'#\' onclick=\'copy(); return false;\'>Copy URL to DocumentCloud</a>\
                {message}'.format(
                    url=obj.documentcloud_url,
                    spaces=spaces,
                    message=message)
                )
        elif obj.file or obj.link:
            link = 'Click "Save" again on this document.' # , or make sure your DocumentCloud credentials are entered and correct
        else:
            link = 'Upload or link to a PDF, then hit "Save."'
        return link
    documentcloud_url_formatted.short_description = 'DocumentCloud link'

    def generate_embed_codes(self, request, queryset):
        """ add admin action to generate document embed code list for user """
        message = ''
        for document in queryset:
            message += str(document.embed_code)
            # message.append(race.embed_code)
        self.message_user(request, '%s' % message)
    generate_embed_codes.short_description = 'Get embed codes for selected documents'

    def get_queryset(self, request):
        """ only show the current user's docs """
        qs = super(DocumentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user=request.user)
            # return qs.filter(newsroom=request.user.documentcloudcredentials.newsroom)

    def save_model(self, request, obj, form, change):
        """ save/update document on DocumentCloud.org and related Document model fields """

        user = request.user
        email_address = user.email

        ## populate user FK on model
        if not obj.created:
            obj.user = user

        ## populate newsroom field
        try:
            email_split = email_address.split('@')
            if not obj.newsroom and email_address:
                obj.newsroom = email_split[1]
        except:
            message = str(sys.exc_info())
            messages.error(request, message)

        ## DocumentCloud credential vars
        try:
            doccloud_creds = DocumentCloudCredentials.objects.filter(user=user)[0]
            verified = doccloud_creds.verified
        except:
            verified = False

        ## assign the password if creds verified
        if verified:
            doccloud_password = doccloud_creds.password
        else:
            doccloud_password = None

        ## choose which DocumentCloud.org creds to use
        shared = False
        individual = False

        user_change_link = '<a href="/admin/auth/user/{}/change/#documentcloudcredentials-0" target="_blank">here</a>.'.format(user.id)

        ## if it's a new document
        if not obj.created:
            if verified:
                individual = True
                obj.account = 'yours'
            else:
                shared = True
                obj.account = 'shared'
        ## if it's an existing document
        elif obj.created:
            if obj.account == 'shared':
                shared = True
            elif obj.account == 'yours' and not verified:
                message = format_html('You need to re-enter your DocumentCloud password ' + user_change_link)
                messages.error(request, message)
            elif obj.account == 'yours':
                individual = True

        ## set the DocumentCloud.org client
        if individual and doccloud_password and not shared:
            email = email_address
            password_encrypted = doccloud_password
            try:
                password = decryption(password_encrypted)
            # except InvalidToken:
            except:
                message = format_html('Your DocumentCloud password was not able to be decrypted correctly. Your administrator has been notified.')
                messages.error(request, message)
                message = str(user) + ': ' + str(sys.exc_info())
                slackbot(message)
        else:
            email = DC_USERNAME
            password = DC_PASSWORD
        # else:
            # message = '!!! No shared account information found. Please add to private settings file or disable this option.'
            # slackbot(message)
            # message = format_html('No DocumentCloud credentials found for an individual account for you or a shared account for your organization. Please add your individual credentials to your user profile {} and contact an administrator about adding shared account credentials.'.format(user_change_link))
            # message = 'Your administrator has not added a shared account login for DocPub. Please contact them to add one or disable this option.'
            # messages.error(request, message)

        try:
            ## create a client for connecting to DocumentCloud
            client = connection(email, password)
            ## determine whether to create or update
            if obj.documentcloud_id:
                obj.document_update(client)
            else:
                obj.document_upload(client)
        except HTTPError:
            message = format_html('Your DocumentCloud credentials have failed. Please make sure your DocPub email matches your DocumentCloud email and that you have entered the correct DocumentCloud password ' + user_change_link)
            messages.error(request, message)
        except FileNotFoundError:
            message = format_html('File not found. Please confirm:<br><br> \
                    - you are uploading the correct file<br> \
                    - your PDF is unlocked<br> \
                    - your PDF opens as expected in your browser or Acrobat<br><br> \
                If this issue persists, please contact your administrator.')
            messages.error(request, message)
        except:
            message = str(user) + ': ' + str(sys.exc_info())
            slackbot(message)
            # message = traceback.print_exc()
            # slackbot(message)
            # messages.error(request, message)

        ## generate the embed
        try:
            if obj.documentcloud_id:
                obj.generate_embed()
        except:
            message = str(sys.exc_info())
            messages.error(request, message)

        super(DocumentAdmin, self).save_model(request, obj, form, change)    


# class DocumentCloudCredentialsAdmin(admin.ModelAdmin):
#     fields = ('user',)
#     list_display = ('user',)
#     readonly_fields = ('user',)


class UserInline(admin.StackedInline):
    model = DocumentCloudCredentials
    readonly_fields = ('newsroom', 'verified', 'encrypted')
    form = PasswordInline
    # can_delete = False
    # verbose_name_plural = 'Login'


class DocUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'newsroom_name', 'is_verified', 'is_superuser', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    inlines = (UserInline,)

    def is_verified(self,obj):
        return obj.documentcloudcredentials.verified
    is_verified.short_description = 'Verified?'
    is_verified.boolean = True

    def newsroom_name(self, obj):
        """ display the newsroom for a user in the admin"""
        if obj.documentcloudcredentials.newsroom:
            try:
                newsroom = dict(NEWSROOM_CHOICES)[obj.documentcloudcredentials.newsroom]
            except:
                newsroom = None
            return newsroom
        else:
            return None
    newsroom_name.short_description = 'Newsroom'

    staff_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        # (_('Groups'), {'fields': ('groups',)}),
    )

    def change_view(self, request, *args, **kwargs):
        # for non-superuser
        if not request.user.is_superuser:
            try:
                self.fieldsets = self.staff_fieldsets
                response = super(DocUserAdmin, self).change_view(request, *args, **kwargs)
            finally:
                # reset fieldsets to its original value
                self.fieldsets = DocUserAdmin.fieldsets
            return response
        else:
            return super(DocUserAdmin, self).change_view(request, *args, **kwargs)

    def get_queryset(self, request):
        """ only show the current user's User object """
        qs = super(DocUserAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(email=request.user.email)

    def save_model(self, request, obj, form, change):
        message_no_pw = 'Please add your DocumentCloud password at the bottom of your user profile. This will allow you to upload documents to your account instead of the default shared account.'
        if obj.email:
            email = obj.email
            # set the newsroom 
            domain = email.split('@')[1]
            DocumentCloudCredentials.objects.filter(user=obj).update(newsroom=domain)
        password = ''
        try:
            password = obj.documentcloudcredentials.password
        except:
            messages.error(request, message_no_pw)
        encrypted = ''
        try:
            encrypted = obj.documentcloudcredentials.encrypted
        except:
            pass
        ## confirm password is correct
        if password and not encrypted:
            client = connection(email, password)
            try:
                ## upload a test doc
                doc = client.documents.upload(TEST_PDF, title='Verify login', access='organization', secure=True)
                ## if upload works, mark this account as verified
                if doc.id:
                    obj.documentcloudcredentials.verified = True
                ## delete the test doc on DocumentCloud
                doc.delete()
            except:
                message = 'Your DocumentCloud credentials have failed. Please make sure your DocumentCloud password (not your DocPub password) matches your account. Also, make sure your DocPub email matches your DocumentCloud account email.'
                messages.error(request, message)
        elif not password:
            messages.error(request, message_no_pw)
        super(DocUserAdmin, self).save_model(request, obj, form, change)


class DocumentSetInline(admin.StackedInline):
    model = Document
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'user', 'newsroom', 'embed_code', 'documentcloud_url') #'project', 'copy_embed_code', 'documentcloud_url_formatted'
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article')
        })
    )
    ## for admin.TabularInline
    # fields = ('access', 'title', ('file', 'link',), 'source', 'documentcloud_url',) # 'description', 'source', 'newsroom', 'embed_code')
    readonly_fields = ('documentcloud_url', 'user')
    show_change_link = True
    extra = 1
    # classes = ['collapse'] ## collapses the entire set of inlines


class DocumentSetAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name', 'created',)
    list_filter = ('created',)
    search_fields = ('name',)
    inlines = (DocumentSetInline,)


admin.site.register(Document, DocumentAdmin)
admin.site.unregister(User)
admin.site.register(User, DocUserAdmin)
admin.site.register(DocumentSet, DocumentSetAdmin)
# admin.site.register(DocumentCloudCredentials, DocumentCloudCredentialsAdmin)

