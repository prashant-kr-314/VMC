from django.conf.urls import url
from spreadsheet import views

urlpatterns = [
    url(r'^$', views.home, name='all_sheets'),
    url(r'^display/(?P<sheet_id>[0-9]+)/$', views.display_sheet, name='display_sheet'),
    url(r'^add_column/(?P<sheet_id>[0-9]+)/$', views.add_column, name='add_column'),
    url(r'^delete_column/(?P<sheet_id>[0-9]+)/$', views.delete_column, name='delete_column'),
    url(r'^add_row/(?P<sheet_id>[0-9]+)/$', views.add_row, name='add_row'),
    url(r'^delete_row/(?P<sheet_id>[0-9]+)/$', views.delete_row, name='delete_row'),
    url(r'^edit_row/(?P<sheet_id>[0-9]+)/(?P<row_id>[0-9]+)/$', views.edit_row, name='edit_row'),
    url(r'^delete_sheet/$', views.delete_sheet, name='delete_sheet'),
    url(r'^display_csv/(?P<sheet_id>[0-9]+)/$', views.display_csv, name='display_csv'),
    url(r'^add_multiple_columns/(?P<sheet_id>[0-9]+)/$', views.add_multiple_columns, name='add_multiple_columns'),
    url(r'^add_multiple_rows/(?P<sheet_id>[0-9]+)/$', views.add_multiple_rows, name='add_multiple_rows'),
    url(r'^add_csv/(?P<sheet_id>[0-9]+)/$', views.add_csv, name='add_csv'),
       
    ]
