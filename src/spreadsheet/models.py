from __future__ import unicode_literals

from django.db import models

# Create your models here.


class SpreadSheet(models.Model):
    name = models.CharField(max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class SpreadSheet2(models.Model):
    name = models.CharField(max_length=128)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def get_sheet_data(self):
        columns = self.get_columns().prefetch_related('spreadsheetrow_set')
        sheet_data = []
        for column in columns:
            column_values = column.spreadsheetrow_set.all().order_by('row_number')
            sheet_data.append(column_values)
        if not columns:
            return columns, zip(*sheet_data)
        else:
            row_number_list = columns[0].spreadsheetrow_set.values_list('row_number', flat=True).order_by('row_number')
            sheet_data = zip(*sheet_data)
            sheet_data = zip(row_number_list, sheet_data)
            return columns, sheet_data

    def get_columns(self):
        return self.spreadsheetcolumn_set.all().order_by('sort_id').prefetch_related('spreadsheetrow_set')


class SpreadSheetColumn(models.Model):
    spread_sheet = models.ForeignKey(SpreadSheet2)
    name = models.CharField(max_length=128)
    sort_id = models.PositiveIntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Column - ' + self.name


class SpreadSheetRow(models.Model):
    row_number = models.BigIntegerField(default=1)
    value = models.TextField(null=True, blank=True)
    column = models.ForeignKey(SpreadSheetColumn)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.value if self.value else 'NONE'

    class Meta:
        unique_together = ('row_number', 'column')
