# programs/urls.py

from django.urls import path
from dashboard.views import add_program, edit_program, delete_program

urlpatterns = [
    path('add/', add_program, name='add_program'),
    path('edit/<int:program_id>/', edit_program, name='edit_program'),
    path('delete/<int:program_id>/', delete_program, name='delete_program'),
]
