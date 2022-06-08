from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'is_staff',
    )
    list_display_links = ('username',)
    list_filter = ('role',)
    search_fields = ('username', 'email', 'role',)
    empty_value_display = '-пусто-'
    save_on_top = True
