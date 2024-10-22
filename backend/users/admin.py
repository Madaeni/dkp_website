from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password'
            )
        }),
        (_('Personal info'), {
            'fields': (
                'email',
                'avatar'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    list_display = (
        'username', 'email', 'date_joined', 'is_staff', 'last_login'
    )
    search_fields = ['username', 'email']


admin.site.register(User, CustomUserAdmin)
