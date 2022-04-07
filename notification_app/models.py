from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    phone = models.CharField(max_length=11, blank=False)
    operator_code = models.IntegerField(blank=False)
    tag = models.CharField(max_length=20, blank=False)
    utc = models.CharField(max_length=6, blank=False)


class Notification(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    message_text = models.TextField(blank=False)
    operator_code_filter = models.JSONField(blank=True, null=True)
    tag_filter = models.JSONField(blank=True, null=True)


class Message(models.Model):
    id = models.IntegerField(primary_key=True, blank=False)
    sending_datetime = models.DateTimeField(blank=False, auto_now=True)
    sending_status = models.CharField(max_length=10)
    notification_id = models.ForeignKey(Notification, on_delete=models.RESTRICT)
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)