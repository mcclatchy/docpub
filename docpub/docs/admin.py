from django.contrib import admin
# from django.contrib import messages
from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    fields = ('access', 'title', ('file', 'link',), 'description', 'source', 'project', 'embed_code', 'documentcloud_url_formatted') # 'format_embed_code', 'documentcloud_id', 
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