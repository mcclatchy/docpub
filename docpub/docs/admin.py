from django.contrib import admin
from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    fields = ('documentcloud_id', 'title', ('file', 'link',), 'description', 'source', 'access', 'project', 'embed_code') # 'format_embed_code'
    list_display = ('title', 'source', 'access', 'project','document_admin_url') ## copy_embed_code
    list_filter = ('access', 'project')
    readonly_fields = ('embed_code', 'documentcloud_id',)
    actions = ('generate_embed_codes')

    ## add admin action to generate document embed code list for user
    def generate_embed_codes(self, request, queryset):
        message = ''
        for document in queryset:
            message += str(document.embed_code)
            # message.append(race.embed_code)
        self.message_user(request, '%s' % message)
    generate_embed_codes.short_description = 'Get embed codes for selected documents'


## TEMPLATE
# class Admin(admin.ModelAdmin):
#     fields = ('')
#     list_display = 
#     # list_editable = ('')
#     list_filter = 
#     search_fields = 
#     # exclude  = ('')


admin.site.register(Document, DocumentAdmin)
## TEMPLATE
# admin.site.register(, )