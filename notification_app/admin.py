from django.contrib import admin
from .models import Client, Notification, Message
# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id','phone','operator_code','tag','utc')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','start_datetime','end_datetime','message_text','operator_code_filter','tag_filter')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sending_datetime', 'sending_status', 'notification_id', 'client')