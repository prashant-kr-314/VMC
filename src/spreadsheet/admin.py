from django.contrib import admin

# Register your models here.
from spreadsheet.models import SpreadSheet, SpreadSheet2, SpreadSheetColumn, SpreadSheetRow


class SpreadSheetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'create_time', 'update_time']
    list_display_links = ['id']


admin.site.register(SpreadSheet, SpreadSheetAdmin)
admin.site.register(SpreadSheet2)
admin.site.register(SpreadSheetColumn)
admin.site.register(SpreadSheetRow)
