from django.contrib import admin
from .models import Post, Comment, UserProfile, Notification
# Register your models here.

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'notification_type',
        'form_user',
        'to_user',
        'post',
        'comment',
        'date',
        'user_has_seen',
    ]
    list_filter = [
        'notification_type',
        'date',
        'user_has_seen',
    ]
    search_fields = [
        'form_user__username',
        'to_user__username',        
    ]
    readonly_fields = [
        'notification_type',
        'form_user',
        'to_user',
        'post',
        'comment',
        'date',
        'user_has_seen',
        'thread',
    ]