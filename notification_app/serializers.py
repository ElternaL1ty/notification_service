import rest_framework.serializers as sz
from .models import Client, Notification
from django.core.validators import RegexValidator
import datetime
from rest_framework.serializers import ValidationError


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

    def validate(self, data):
        try:
            start = data['start_datetime']
            end = data['end_datetime']
            if end.replace(tzinfo=None) < datetime.datetime.now():
                raise ValidationError({"end_datetime":"Dates are in the past"})
            if end.replace(tzinfo=None)<start.replace(tzinfo=None):
                raise ValidationError({"end_datetime":"end datetime before start datetime"})
        except KeyError:
            raise ValidationError("Dates are required")
        return data

    class Meta:
        model = Notification
        read_only_fields = ('id','start_datetime', 'end_datetime')
        fields = '__all__'