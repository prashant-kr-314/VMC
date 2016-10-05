from django import forms
from spreadsheet.models import SpreadSheetColumn
from datetime import timedelta
from django.utils import timezone


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
