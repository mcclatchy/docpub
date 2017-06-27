from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
# from django.contrib import messages
from docpub.settings import DC_USERNAME, DC_PASSWORD, COMPANY
from .models import Document, DocumentCloudCredentials, DocumentSet
from docs.connection import connection
from docs.forms import PasswordInline


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'uploaded_by', 'newsroom', 'embed_code', 'documentcloud_url_formatted') #'project', 'copy_embed_code',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article')
        })
    )
    # fields = ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted') # 'format_embed_code', 'documentcloud_id', 
    list_display = ('title', 'created', 'source', 'access', 'documentcloud_url_formatted',) # 'copy_embed_code'
    list_filter = ('access',) # 'project', 'updated', 'created',
    readonly_fields = ('embed_code', 'documentcloud_url_formatted',) # 'documentcloud_id', 'uploaded_by'
    actions = ('generate_embed_codes')

    # def copy_embed_code(self, obj):
    #     """ create a button in the admin for users to copy a specific embed code """
    #     # embed_code = obj.embed_code
    #     embed_code = 'test copy text'
    #     script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/1.7.1/clipboard.min.js"></script><script>var clipboard=new Clipboard(".copyCode",{{text: function(){{return "{code}";}}}});</script>'.format(code=embed_code)
    #     # <script>$(function(){{$(".copyCode").click(function(){{ var temp=$(".copyCode"); $("body").append(temp); temp.val("' + embed_code + '").select(); document.execCommand("copy")}}); }});</script>
    #     button = format_html(script + '<a class="button copyCode" href="#">Copy embed code</a>')
    #     return button

    def documentcloud_url_formatted(self, obj):
        """ display the DocumentCloud URL as a clickable link in the admin"""
        link = '-'
        if obj.documentcloud_id:
            link = format_html('<a class="button" href="{}">View/edit on DocumentCloud</a>'.format(obj.documentcloud_url))
        return link
    documentcloud_url_formatted.short_description = 'DocumentCloud link'

    def get_queryset(self, request):
        """ only show the current users docs """
        qs = super(DocumentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(uploaded_by=request.user)

    def generate_embed_codes(self, request, queryset):
        """ add admin action to generate document embed code list for user """
        message = ''
        for document in queryset:
            message += str(document.embed_code)
            # message.append(race.embed_code)
        self.message_user(request, '%s' % message)
    generate_embed_codes.short_description = 'Get embed codes for selected documents'

    def save_model(self, request, obj, form, change):
        """ save/add to DocumentCloud.org """
        user = request.user
        email_address = user.email

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
                obj.newsroom = '%s (unspecified)' % (company)

        ## choose which DocumentCloud.org creds to use
        documentcloud_login = DocumentCloudCredentials.objects.filter(user=user)
        documentcloud_password = documentcloud_login[0].password
        if documentcloud_password:
            client = connection(email_address, documentcloud_password)
            ## if this fails, need a way to notify user that their creds are wrong; and/or fallback to shared account?
        else:
            client = connection(DC_USERNAME, DC_PASSWORD)
        if obj.updated:
            obj.document_update(client)
        else:
            obj.document_upload(client)

        ## generate the embed
        obj.generate_embed()

        super(DocumentAdmin, self).save_model(request, obj, form, change)    


# class DocumentCloudCredentialsAdmin(admin.ModelAdmin):
#     fields = ('user',)
#     list_display = ('user',)
#     readonly_fields = ('user',)


class UserInline(admin.StackedInline):
    model = DocumentCloudCredentials
    form = PasswordInline
    # can_delete = False
    # verbose_name_plural = 'Login'

class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)


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