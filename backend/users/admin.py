from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, Avatar


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': (
                'username',
                'password',
                'email',
                'avatar',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined'
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
    )
    list_display = (
        'username', 'email', 'date_joined', 'is_staff', 'last_login'
    )
    search_fields = ['username', 'email', 'character']
    list_filter = ['username', 'is_staff']


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ['id', 'avatar']


admin.site.register(User, CustomUserAdmin)
