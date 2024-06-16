from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        *UserAdmin.fieldsets, 
        (
            'Custom Field Heading', 
            {
                'fields': (
                    'is_customer', 
                    'is_officer'
                )
            }
        )
    )
    list_display = ('email', 'is_staff', 'is_active', 'is_customer', 'is_officer')
    list_filter = ('email', 'is_staff', 'is_active', 'is_customer', 'is_officer')
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
