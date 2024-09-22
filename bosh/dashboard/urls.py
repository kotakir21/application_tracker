# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.user_dashboard, name='user_dashboard'),
    path('officer/', views.officer_dashboard, name='officer_dashboard'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/edit/<int:application_id>/', views.edit_application, name='edit_application'),
    path('application/delete/<int:application_id>/', views.delete_application, name='delete_application'),
    path('application/status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('application/upload_documents/<int:application_id>/', views.upload_additional_documents, name='upload_documents'),
    path('programs/add/', views.add_program, name='add_program'),
    path('programs/edit/<int:program_id>/', views.edit_program, name='edit_program'),
    path('programs/delete/<int:program_id>/', views.delete_program, name='delete_program'),
]
