from django.contrib import admin
from .models import Post, Comment, UserProfile, Notification, MessageModel, ThreadModel
# Register your models here.
admin.site.register(ThreadModel)
admin.site.register(MessageModel)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'body',
        'author',
        'created_on',
        'shared_body',
        'shared_user',
        'shared_on',
        
    ]
    list_filter = [
        'body',
        'author',
        'created_on'
        
    ]

    search_fields = [
        'author__username',
        'shared_user__username'
    ]
    
    readonly_fields = [
        'body',
        'image',
        'author',
        'created_on',
        'shared_body',
        'shared_user',
        'shared_on',
        'likes',
        'dislikes',
        'tags',
    ]
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'comment',
        'author',
        'created_on',

        
    ]
    list_filter = [
        'comment',
        'author',
        'created_on'

        
    ]

    search_fields = [
        'author__username',
    ]

    
    readonly_fields = [
        'post',
        'comment',
        'author',
        'created_on',
        'likes',
        'dislikes',
        'parent',
        'tags',
    ]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'bio',
        'birth_date',
        'location',
        'picture',
    ]
    
    list_filter = [
        'user',
        'location',       
    ]
    
    search_fields = [
        'user__username',
    ]

    readonly_fields = [
        'user',
        'name',
        'bio',
        'birth_date',
        'location',
        'picture',
        'followers',
    ]
    
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
        'to_user__username'
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
