from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_filter = ('email', 'username')


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
