# applications/urls.py

from django.urls import path
from .views import apply_for_program, edit_application, delete_application, application_detail

urlpatterns = [
    path('apply/<int:program_id>/', apply_for_program, name='apply_for_program'),
    path('edit/<int:application_id>/', edit_application, name='edit_application'),
    path('delete/<int:application_id>/', delete_application, name='delete_application'),
    path('detail/<int:application_id>/', application_detail, name='application_detail'),
]
