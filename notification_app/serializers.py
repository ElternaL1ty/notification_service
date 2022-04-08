import rest_framework.serializers as sz
from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import Client, Notification, Message

import datetime


class ClientSerializer(sz.ModelSerializer):
    PhoneValidator = RegexValidator(regex='^7[0-9]{10}', message="phone number must be 7XXXXXXXXXX")
    UTCValidator = RegexValidator(regex='^UTC[+?-][0-9]{1,2}', message="phone number must be 7XXXXXXXXXX")

    phone = sz.CharField(max_length=11, validators=[PhoneValidator])
    utc = sz.CharField(max_length=6, validators=[UTCValidator])

    class Meta:
        model = Client
        read_only_fields = ('id',)
        fields = '__all__'


class NotificationSerializer(sz.ModelSerializer):
    start_datetime = sz.DateTimeField(required=True)
    end_datetime = sz.DateTimeField(required=True)
    operator_code_filter = sz.JSONField(required=True)
    tag_filter = sz.JSONField(required=True)
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        data = Message.objects.filter(notification_id=int(obj.id))
        data_success = data.filter(sending_status="SUCCESS").count()
        data_error = data.filter(sending_status="ERROR").count()
        data_queue = data.filter(sending_status="IN QUEUE").count()
        messages = {
            "success": data_success,
            "error": data_error,
            "in queue": data_queue
        }
        return messages

    def validate(self, data):
        opcode_filter = data['operator_code_filter']
        for i in opcode_filter:
            if not isinstance(i, int):
                raise sz.ValidationError({"operator_code_filter": "All codes must be INTEGER"})

        tag_filter = data['tag_filter']
        for i in tag_filter:
            if not isinstance(i, str):
                raise sz.ValidationError({"tag_filter": "All tags must be STRING"})

        try:
            start = data['start_datetime']
            end = data['end_datetime']
            if end.replace(tzinfo=None) < datetime.datetime.now():
                raise sz.ValidationError({"end_datetime": "Dates are in the past"})
            if end.replace(tzinfo=None) < start.replace(tzinfo=None):
                raise sz.ValidationError({"end_datetime": "end datetime before start datetime"})
        except KeyError:
            raise sz.ValidationError("Dates are required")
        return data

    class Meta:
        model = Notification
        read_only_fields = ('id', 'start_datetime', 'end_datetime')
        fields = ('id','start_datetime','end_datetime','operator_code_filter','tag_filter', 'messages',)

