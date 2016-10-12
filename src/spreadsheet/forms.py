from django import forms
from spreadsheet.models import SpreadSheetColumn, SpreadSheet2
from datetime import timedelta
from django.utils import timezone
import datetime
##class SpreadSheetFormtest(forms.ModelForm):
##    num=intfield
##    minvalue
##    def clean_number(self):
##        old_no=self.cleaned_data.get("number")
##        if old_value<1:
##            raise validation error
##        else:
##            return clean_data

class FileForm(forms.Form):
    csv_file = forms.FileField()
    def clean_csv_file(self):
        data=self.cleaned_data.get('csv_file')
        k=str(data.name)
        k=k.split('.')
        if k[1] != 'csv':
            raise forms.ValidationError("Please Upload a CSV file")
        return data
    
class NoOfColumnsForm(forms.Form):
    no_of_columns = forms.IntegerField(min_value=1)
class NoOfRowsForm(forms.Form):
    no_of_rows = forms.IntegerField(min_value=1)
    
    
class SpreadSheetForm(forms.ModelForm):
    class Meta:
        model = SpreadSheet2
        fields = ['name']
        


class ColumnForm(forms.ModelForm):
    class Meta:
        model = SpreadSheetColumn
        fields = ['name', 'sort_id']


class RowForm(forms.Form):
    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns', [])
        add = kwargs.pop('add', True)
        initial_data = kwargs.pop('initial_data', [])
        user = kwargs.pop('user', None)
        user_check_override = kwargs.pop('user_check_override', False)
        super(RowForm, self).__init__(*args, **kwargs)

        if add:
            for column in columns:
                self.fields['column_' + str(column.id)] = forms.CharField(max_length=1024, label=column.name,
                                                                          required=False)
        else:
            last_hour_date_time = timezone.now() - timedelta(hours=1)
            
            for column, row in initial_data:
                if user.is_authenticated() and user.is_superuser and not user_check_override:
                    self.fields['column_' + str(column.id)] = forms.CharField(max_length=1024, label=column.name,
                                                                              required=False)
                else:
                    if row.update_time >= last_hour_date_time:
                        self.fields['column_' + str(column.id)] = forms.CharField(max_length=1024, label=column.name,
                                                                                  required=False)
                    else:
                        self.fields['column_' + str(column.id)] = forms.CharField(max_length=1024, label=column.name,
                                                                                  required=False, disabled=True)
