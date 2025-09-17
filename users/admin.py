from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ['stories_generated', 'favorite_stories_count', 'average_rating', 'created_at', 'updated_at']

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'favorite_genre', 'preferred_length', 'preferred_tone', 'stories_generated', 'average_rating']
    list_filter = ['favorite_genre', 'preferred_length', 'preferred_tone']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['stories_generated', 'favorite_stories_count', 'average_rating', 'created_at', 'updated_at']
