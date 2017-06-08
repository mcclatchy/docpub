from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# from django.contrib import messages
from .models import Document, DocumentCloudCredentials


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('secure', 'sidebar', 'related_article')
        })
    )
    # fields = ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted') # 'format_embed_code', 'documentcloud_id', 
    list_display = ('title', 'created', 'source', 'access', 'documentcloud_url_formatted') ## copy_embed_code
    list_filter = ('access', 'project') # 'updated', 'created', 
    readonly_fields = ('embed_code', 'documentcloud_url_formatted',) # 'documentcloud_id'
    actions = ('generate_embed_codes')

    # def save_model(self, request, obj, form, change):
    #     if not 'file' or 'link' in form.changed_data:
    #         messages.add_message(request, messages.INFO, 'You must upload or link to a PDF')
    #     # super(CarAdmin, self).save_model(request, obj, form, change)

    ## add admin action to generate document embed code list for user
    def generate_embed_codes(self, request, queryset):
        message = ''
        for document in queryset:
            message += str(document.embed_code)
            # message.append(race.embed_code)
        self.message_user(request, '%s' % message)
    generate_embed_codes.short_description = 'Get embed codes for selected documents'


class DocumentCloudCredentialsAdmin(admin.ModelAdmin):
    fields = ('user', 'password')
    list_display = ('user',)
    # list_editable = ('')
    # list_filter = 
    # search_fields = 
    # exclude  = ('')


class UserInline(admin.StackedInline):
    model = DocumentCloudCredentials
    # can_delete = False
    # verbose_name_plural = 'Login'

class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)


# from django.forms import CharField, ModelForm, PasswordInput

# class UserForm(ModelForm):
#     class Meta:
#         password = CharField(widget=PasswordInput)
#         model = DocumentCloudCredentials
#         fields = ('password',)
#         widgets = {
#             'password': PasswordInput(),
#         }


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
admin.site.register(DocumentCloudCredentials, DocumentCloudCredentialsAdmin)
## TEMPLATE
# admin.site.register(, )