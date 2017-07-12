from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.contrib import messages
import sys
from docpub.settings import COMPANY, DC_USERNAME, DC_PASSWORD, DOCPUBENV, TEST_PDF
from .models import Document, DocumentCloudCredentials, DocumentSet
from docs.connection import connection
from docs.choices import NEWSROOM_CHOICES
from docs.decryption import decryption
from docs.forms import PasswordInline


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'uploaded_by', 'newsroom', 'embed_code', 'copy_embed_code', 'documentcloud_url_formatted') #'project', 'copy_embed_code',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article', 'user',)
        })
    )
    # fields = ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted') # 'format_embed_code', 'documentcloud_id', 
    list_display = ('title', 'created', 'source', 'access', 'documentcloud_url_formatted', 'copy_embed_code',)
    list_editable = ('access',)
    list_filter = ('access',) # 'project', 'updated', 'created',
    readonly_fields = ('account', 'copy_embed_code', 'documentcloud_url_formatted', 'embed_code', 'user',) # 'documentcloud_id', 'uploaded_by'
    actions = ('generate_embed_codes')

    def copy_embed_code(self, obj):
        """ create a button in the admin for users to copy a specific embed code """
        if obj.documentcloud_id:
            embed_code = obj.embed_code
            html = '<a class=\'button copyCode\' data-clipboard-action=\'copy\' data-clipboard-text=\'{code}\' href=\'#\' onclick=\'copy(); return false;\'>Copy embed code</a>'.format(code=embed_code)
            button = format_html(html)
        else:
            button = '-'
        return button

    def documentcloud_url_formatted(self, obj):
        """ display the DocumentCloud URL as a clickable link in the admin"""
        if obj.documentcloud_id:
            link = format_html('<a class="button" href="{}" target="_blank">View/edit on DocumentCloud</a>'.format(obj.documentcloud_url))
        elif obj.file or obj.link:
            link = 'Click "Save" again on this doc, or make sure your DocumentCloud credentials are entered and correct'
        else:
            link = 'Upload or link to a PDF, then hit "Save" below.'
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

        ## populate uploaded_by and newsroom
        fullname = user.get_full_name()
        email_split = email_address.split('@')
        uploaded_by = obj.uploaded_by
        newsroom = obj.newsroom

        if not obj.uploaded_by:
            if fullname:
                obj.uploaded_by = fullname
            elif email_address:
                obj.uploaded_by = email_split[0]
            else:
                obj.uploaded_by = user.username
        if not obj.newsroom:
            if email_address:
                obj.newsroom = email_split[1]
            else:
                obj.newsroom = '%s (unspecified)' % (COMPANY)

        ## determine if password exists
        documentcloud_login = DocumentCloudCredentials.objects.filter(user=user)[0]
        if documentcloud_login.password:
            password_exists = True
        else:
            password_exists = False

        ## choose which DocumentCloud.org creds to use
        shared = False
        individual = False

        user_change_link = '<a href="/admin/auth/user/{}/change/#documentcloudcredentials-0" target="_blank">here</a>.'.format(user.id)

        if not obj.created:
            if password_exists:
                individual = True
                obj.account = 'Your account'
            else:
                shared = True   
                obj.account = 'Shared account'
        else:
            if obj.account == 'Shared account' and password_exists:
                shared = True
            elif obj.account == 'Your account' and not password_exists:
                message = format_html('You need to re-enter your DocumentCloud password ' + user_change_link)
                messages.error(request, message)
            else:
                individual = True

        ## set the DocumentCloud.org client
        if individual:
            email = email_address
            password_encrypted = str(documentcloud_login.password)
            password = decryption(password_encrypted)
        elif shared:
            email = DC_USERNAME
            password = DC_PASSWORD
        else:
            message = format_html('No DocumentCloud credentials found for an individual account for you or a shared account for your organization. Please add your individual credentials to your user profile {} and contact an administrator about adding shared account credentials.'.format(user_change_link))
            messages.error(request, message)

        try:
            client = connection(email, password)

            ## determine whether to create or update
            if obj.documentcloud_id:
                obj.document_update(client)
            else:
                obj.document_upload(client)
        except:
            message = format_html('Your DocumentCloud credentials have failed. Please make sure your DocPub email matches your DocumentCloud email and that you have entered the correct DocumentCloud password ' + user_change_link)
            messages.error(request, message)

        ## generate the embed
        if obj.documentcloud_id:
            obj.generate_embed()

        super(DocumentAdmin, self).save_model(request, obj, form, change)    


# class DocumentCloudCredentialsAdmin(admin.ModelAdmin):
#     fields = ('user',)
#     list_display = ('user',)
#     readonly_fields = ('user',)


class UserInline(admin.StackedInline):
    model = DocumentCloudCredentials
    readonly_fields = ('newsroom',)
    form = PasswordInline
    # can_delete = False
    # verbose_name_plural = 'Login'


class UserAdmin(BaseUserAdmin):
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

    # def get_queryset(self, request):
    #     """ only show the current user's fellow newsroom users """
    #     qs = super(DocumentAdmin, self).get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(newsroom=request.user.documentcloudcredentials.newsroom)

    def save_model(self, request, obj, form, change):
        try:
            email = obj.email
            password = obj.documentcloudcredentials.password
            ## set newsroom
            domain = email.split('@')[1]
            DocumentCloudCredentials.objects.filter(user=obj).update(newsroom=domain)
            ## confirm password is correct
            if password and password[-1] != '=':
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
                message = 'Please add your DocumentCloud password at the bottom of this page. This will allow you to upload documents to your account instead of the default shared account.'
                messages.error(request, message)
        except:
            messages.error(request, str(sys.exc_info()))
        super(UserAdmin, self).save_model(request, obj, form, change)


class DocumentSetInline(admin.StackedInline):
    model = Document
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'uploaded_by', 'newsroom', 'embed_code', 'documentcloud_url') #'project', 'copy_embed_code', 'documentcloud_url_formatted'
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article')
        })
    )
    ## for admin.TabularInline
    # fields = ('access', 'title', ('file', 'link',), 'source', 'documentcloud_url',) # 'description', 'source', 'uploaded_by', 'newsroom', 'embed_code')
    readonly_fields = ('documentcloud_url',)
    show_change_link = True
    extra = 1
    # classes = ['collapse'] ## collapses the entire set of inlines


class DocumentSetAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name', 'created',)
    list_filter = ('created',)
    search_fields = ('name',)
    inlines = (DocumentSetInline,)

## TEMPLATE
# class Admin(admin.ModelAdmin):
#     fields = ('')
#     list_display = 
#     # list_editable = ('')
#     list_filter = 
#     search_fields = 
#     # exclude  = ('')


admin.site.register(Document, DocumentAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(DocumentSet, DocumentSetAdmin)
# admin.site.register(DocumentCloudCredentials, DocumentCloudCredentialsAdmin)
## TEMPLATE
# admin.site.register(, )