from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'is_staff',
        'confirmation_code',
        'is_admin',
        'is_moderator',
    )
    list_display_links = ('username',)
    list_filter = ('role',)
    search_fields = ('username', 'email', 'role',)
    empty_value_display = '-пусто-'
    save_on_top = True
    actions = ['Delete', ]
