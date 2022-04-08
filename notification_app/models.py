from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    phone = models.CharField(max_length=11, blank=False)
    operator_code = models.IntegerField(blank=False)
    tag = models.CharField(max_length=20, blank=False)
    utc = models.CharField(max_length=6, blank=False)

    class Meta:
        verbose_name = "Клиент",
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return str(self.id)


class Notification(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    message_text = models.TextField(blank=False)
    operator_code_filter = models.JSONField(blank=True, null=True)
    tag_filter = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Рассылка",
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    id = models.AutoField(primary_key=True, blank=False)
    sending_datetime = models.DateTimeField(blank=False, auto_now=True)
    sending_status = models.CharField(max_length=10)
    notification_id = models.ForeignKey(Notification, on_delete=models.RESTRICT)
    client = models.ForeignKey(Client, on_delete=models.RESTRICT)

    class Meta:
        verbose_name = "Сообщение",
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return str(self.id)