from django.db.models.aggregates import Max
from django.db.models.functions import Coalesce
from django.http.response import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from spreadsheet.forms import ColumnForm, RowForm, SpreadSheetForm
from spreadsheet.models import SpreadSheet2, SpreadSheetRow, SpreadSheetColumn


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
    add_column_form = ColumnForm()
    add_row_form = RowForm(columns=columns)
    context = {
        "sheet": sheet,
        "columns": columns,
        "rows": sheet_data,
        "add_column_form": add_column_form,
        "add_row_form": add_row_form
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
    row_data = SpreadSheetRow.objects.filter(row_number=row_id).order_by('column__sort_id')
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
        return HttpResponseRedirect('/edit_row/' + sheet_id + '/' + row_id)
    else:
        return render(request, 'spreadsheet/edit_row.html', context)


def map_column(column):
    return 'column_' + str(column.id)


def map_parse_column(column_field):
    column = column_field.split('_')
    return column_field, column[1]


def map_row(row):
    return row.value
