from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# from django.contrib import messages
from .models import Document, DocumentCloudCredentials
from docs.connection import connection
from docpub.settings import DC_USERNAME, DC_PASSWORD, COMPANY
from docs.forms import PasswordInline


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'uploaded_by', 'newsroom', 'embed_code', 'documentcloud_url_formatted') #'project',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article')
        })
    )
    # fields = ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted') # 'format_embed_code', 'documentcloud_id', 
    list_display = ('title', 'created', 'source', 'access', 'documentcloud_url_formatted') ## copy_embed_code
    list_filter = ('access',) # 'project', 'updated', 'created',
    readonly_fields = ('embed_code', 'documentcloud_url_formatted',) # 'documentcloud_id', 'uploaded_by'
    actions = ('generate_embed_codes')

    def get_queryset(self, request):
        """ only show the current users docs """
        qs = super(DocumentAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(uploaded_by=request.user)

    # def copy_embed_code(self, obj):
        """ create a button in the admin for users to copy a specific embed code """


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
# admin.site.register(DocumentCloudCredentials, DocumentCloudCredentialsAdmin)
## TEMPLATE
# admin.site.register(, )