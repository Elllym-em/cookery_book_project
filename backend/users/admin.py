from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import register

from .models import Follow, User


@register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('email', 'username',)
    search_fields = ('email', 'username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'follower',
        'author',
    )
    search_fields = ('follower', 'author',)
