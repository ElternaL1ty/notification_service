from django.contrib import admin
from .models import Client, Notification, Message
# Register your models here.
admin.site.register(Client)
admin.site.register(Notification)
admin.site.register(Message)