from django.db.models.aggregates import Max
from django.db.models.functions import Coalesce
from django.http.response import HttpResponseNotFound, HttpResponseRedirect,HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from spreadsheet.forms import ColumnForm, RowForm, SpreadSheetForm,NoOfColumnsForm,NoOfRowsForm,FileForm
from spreadsheet.models import SpreadSheet2, SpreadSheetRow, SpreadSheetColumn
import uuid
import csv
import datetime
from io import TextIOWrapper


def add_csv(request,sheet_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    
    
    if request.POST and request.FILES:
        csv_form = FileForm(request.POST, request.FILES)
        if csv_form.is_valid():
            csv_file= request.FILES['csv_file']
            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding=request.encoding)


            
            data_list = list(list(rec) for rec in csv.reader(csv_file, delimiter=','))
            column_values=data_list[0]
            column_to_add_list=[]
            for column in column_values:
                column_to_add=SpreadSheetColumn(spread_sheet=sheet,name=column)
                column_to_add_list.append(column_to_add)
            
            SpreadSheetColumn.objects.bulk_create(column_to_add_list)
            
            columns, sheet_data = sheet.get_sheet_data()
            row_values=data_list[1:]
            max_row_num = SpreadSheetRow.objects.aggregate(num=Coalesce(Max('row_number'), -1))
            new_row_num = max_row_num['num'] +1
            for row in row_values:
                obj_list=[]
                for i in range(0,len(row)):
                    obj_list.append(SpreadSheetRow(row_number=new_row_num,column=columns[i],value=row[i]))
                new_row_num= new_row_num+1
                SpreadSheetRow.objects.bulk_create(obj_list)
            return HttpResponseRedirect('/display/' + str(sheet.id))
        else:                             
            form = ColumnForm()
            columns, sheet_data = sheet.get_sheet_data()
            add_row_form = RowForm(columns=columns)
            context = {
            "sheet": sheet,
            "columns": columns,
            "rows": sheet_data,
            "add_column_form": form,
            "add_row_form": add_row_form,
            "csv_form":csv_form        }
        return render(request, 'spreadsheet/display_sheet.html', context)
    else:
        csv_form=FileForm()
        return render(request,'spreadsheet/name.html',{'csv_form':csv_form})
    
def add_multiple_columns(request,sheet_id):
    form=NoOfColumnsForm(request.POST or None)
    if request.POST and form.is_valid():
        no_of_columns=form.cleaned_data.get('no_of_columns')
        try:
            sheet=SpreadSheet2.objects.get(id=sheet_id)
        except:
            return HttpResponseNotFound("<h1>Not Found</h1>")
        columns, sheet_data = sheet.get_sheet_data()
        if not columns:
            for i in range(0,no_of_columns):
                column=SpreadSheetColumn(spread_sheet=sheet,name=" ")
                column.save()
            
        else:
            row_number_list = columns[0].spreadsheetrow_set.values_list('row_number', flat=True).order_by('row_number')
            for i in range(0,no_of_columns):
                column=SpreadSheetColumn(spread_sheet=sheet,name=" ")
                column.save()
                obj_list = []
                for el in row_number_list:
                    obj_list.append(SpreadSheetRow(row_number=el, column=column))
                SpreadSheetRow.objects.bulk_create(obj_list)
            
        return HttpResponseRedirect('/display/' + str(sheet_id))

def add_multiple_rows(request,sheet_id):
    form=NoOfRowsForm(request.POST or None)
    if request.POST and form.is_valid():
        no_of_rows=form.cleaned_data.get('no_of_rows')
        try:
            sheet=SpreadSheet2.objects.get(id=sheet_id)
        except:
            return HttpResponseNotFound("<h1>Not Found</h1>")
        max_row_num = SpreadSheetRow.objects.aggregate(num=Coalesce(Max('row_number'), -1))
        new_row_num = max_row_num['num'] +1

        columns, sheet_data = sheet.get_sheet_data()
        for i in range(0,no_of_rows):
            new_row_num=new_row_num+i
            new_obj_list=[]
            for column in columns:
                new_obj_list.append(SpreadSheetRow(row_number=new_row_num, value=" ", column=column))
            SpreadSheetRow.objects.bulk_create(new_obj_list)
    return HttpResponseRedirect('/display/' + str(sheet_id))


    
   
def home(request):
    sheets = SpreadSheet2.objects.all()
    form = SpreadSheetForm(request.POST or None)
    context = {
        'sheets': sheets,
        'form': form
    }
    if request.POST and form.is_valid():
        new_sheet = form.save()
        return HttpResponseRedirect('/display/' + str(new_sheet.id))
    return render(request, 'spreadsheet/all_sheets.html', context)


@require_POST
def delete_sheet(request):
    sheet_id = request.POST.get('sheet_id')
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    sheet.delete()
    return HttpResponseRedirect('/')


def display_sheet(request, sheet_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    
    columns, sheet_data = sheet.get_sheet_data()
    add_multiple_columns_form=NoOfColumnsForm(initial={'no_of_columns': 1})
    add_multiple_rows_form=NoOfRowsForm(initial={'no_of_rows': 1})

    add_column_form = ColumnForm()
    add_row_form = RowForm(columns=columns)
    csv_form=FileForm()
    context = {
        "sheet": sheet,
        "columns": columns,
        "rows": sheet_data,
        "add_column_form": add_column_form,
        "add_row_form": add_row_form,
        "add_multiple_columns":add_multiple_columns_form,
        "add_multiple_rows":add_multiple_rows_form,
        "csv_form":csv_form

    }
    return render(request, 'spreadsheet/display_sheet.html', context)


def display_csv(request, sheet_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    list_cols=[]
    list_row=[]
    list_list_row=[]
    columns, sheet_data = sheet.get_sheet_data()
    for column in columns:
        list_cols.append(column.name)
    for row_num, row in sheet_data:
        list_row=[]
        for cell in row:
            list_row.append(cell.value)
        list_list_row.append(list_row)
    response_csv = HttpResponse(content_type='text/csv')
    a=str(uuid.uuid4())+".csv"
    response_csv['Content-Disposition'] = "attachment; filename=%s"%a
    writer = csv.writer(response_csv)
    writer.writerow(list_cols)
    for row in list_list_row:
        writer.writerow(row)
    return response_csv


def add_column(request, sheet_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    columns, sheet_data = sheet.get_sheet_data()
    form = ColumnForm(request.POST or None)
    add_row_form = RowForm(columns=columns)
    if form.is_valid() and request.POST:
        column = form.save(commit=False)
        column.spread_sheet = sheet
        column.save()
        if not columns:
            return HttpResponseRedirect('/display/' + str(sheet.id))
        else:
            row_number_list = columns[0].spreadsheetrow_set.values_list('row_number', flat=True).order_by('row_number')
            obj_list = []
            for el in row_number_list:
                obj_list.append(SpreadSheetRow(row_number=el, column=column))
            SpreadSheetRow.objects.bulk_create(obj_list)
            return HttpResponseRedirect('/display/' + str(sheet.id))
    else:
        context = {
            "sheet": sheet,
            "columns": columns,
            "rows": sheet_data,
            "add_column_form": form,
            "add_row_form": add_row_form
        }
        return render(request, 'spreadsheet/display_sheet.html', context)


def delete_column(request, sheet_id):
    if request.POST:
        column_id = request.POST.get('delete_column')
        try:
            column = SpreadSheetColumn.objects.get(id=column_id, spread_sheet__id=sheet_id)
        except:
            return HttpResponseNotFound("<h1>Not Found</h1>")
        else:
            column.delete()
            return HttpResponseRedirect('/display/' + str(sheet_id))
    else:
        return HttpResponseNotFound()


def add_row(request, sheet_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    columns, sheet_data = sheet.get_sheet_data()
    add_column_form = ColumnForm()
    add_row_form = RowForm(request.POST or None, columns=columns)
    if add_row_form.is_valid() and request.POST:
        max_row_num = SpreadSheetRow.objects.aggregate(num=Coalesce(Max('row_number'), -1))
        new_row_num = max_row_num['num'] + 1
        new_obj_list = []
        for column in columns:
            value = add_row_form.cleaned_data.get('column_' + str(column.id), None)
            new_obj_list.append(SpreadSheetRow(row_number=new_row_num, value=value, column=column))
        SpreadSheetRow.objects.bulk_create(new_obj_list)
        return HttpResponseRedirect('/display/' + str(sheet.id))
    else:
        context = {
            "sheet": sheet,
            "columns": columns,
            "rows": sheet_data,
            "add_column_form": add_column_form,
            "add_row_form": add_row_form
        }
        return render(request, 'spreadsheet/display_sheet.html', context)


def delete_row(request, sheet_id):
    if request.POST:
        row_id = request.POST.get('row_id')
        SpreadSheetRow.objects.filter(row_number=row_id, column__spread_sheet__id=sheet_id).delete()
        return HttpResponseRedirect('/display/' + str(sheet_id))
    else:
        return HttpResponseNotFound()


def edit_row(request, sheet_id, row_id):
    try:
        sheet = SpreadSheet2.objects.get(id=sheet_id)
    except:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    columns = sheet.get_columns()
    row_data = SpreadSheetRow.objects.filter(row_number=row_id).order_by('column__sort_id', 'column__id')
    if not row_data:
        return HttpResponseNotFound("<h1>Not Found</h1>")
    initial_data = zip(columns, row_data)
    column_list = map(map_column, columns)
    row_list = map(map_row, row_data)
    form_initial_data = dict(zip(column_list, row_list))
    edit_row_form = RowForm(request.POST or None, add=False, initial=form_initial_data, columns=columns,
                            initial_data=initial_data, user=request.user)
    context = {
        "form": edit_row_form,
        "sheet": sheet,
        "row_id": row_id
    }
    if request.POST and edit_row_form.is_valid():
        changed_columns = map(map_parse_column, edit_row_form.changed_data)
        for column_field, col_num in changed_columns:
            try:
                row = SpreadSheetRow.objects.get(row_number=row_id, column__id=col_num)
            except:
                return HttpResponseNotFound('Something Went Wrong')
            row.value = edit_row_form.cleaned_data.get(column_field)
            row.save()
        return HttpResponseRedirect('/display/' + sheet_id)
    else:
        return render(request, 'spreadsheet/edit_row.html', context)


def map_column(column):
    return 'column_' + str(column.id)


def map_parse_column(column_field):
    column = column_field.split('_')
    return column_field, column[1]


def map_row(row):
    return row.value
