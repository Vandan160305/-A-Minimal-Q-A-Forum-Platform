from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'body', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(models.Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('short_body', 'user', 'question', 'parent', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('body', 'user__username', 'question__title')
    date_hierarchy = 'created_at'
    
    def short_body(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    short_body.short_description = 'Response'

@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'text', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'text')
    date_hierarchy = 'created_at'
    list_editable = ('is_read',)
