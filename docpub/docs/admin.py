from django.contrib import admin
from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'source', 'file', 'link']
    list_display = ['title', 'source']

## TEMPLATE
# class Admin(admin.ModelAdmin):
#     fields = ['']
#     list_display = 
#     # list_editable = ['']
#     list_filter = 
#     search_fields = 
#     # exclude  = ['']


admin.site.register(Document, DocumentAdmin)
## TEMPLATE
# admin.site.register(, )