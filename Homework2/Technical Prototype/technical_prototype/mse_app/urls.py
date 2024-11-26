from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('login'), name='root'),
    path('create-account/', views.create_account, name='create_account'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report-analysis/', views.report_analysis, name='report_analysis'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('detailed_report/', views.report_analysis, name='detailed_report'),
    path('get_stock_data/', views.get_stock_data, name='get_stock_data'),

]
