import rest_framework.serializers as sz
from .models import Client
from django.core.validators import RegexValidator


class ClientSerializer(sz.ModelSerializer):
    PhoneValidator = RegexValidator(regex='^7[0-9]{10}', message="phone number must be 7XXXXXXXXXX")
    UTCValidator = RegexValidator(regex='^UTC[+?-][0-9]{1,2}', message="phone number must be 7XXXXXXXXXX")

    phone = sz.CharField(max_length=11, validators=[PhoneValidator])
    utc = sz.CharField(max_length=6, validators=[UTCValidator])

    class Meta:
        model = Client
        read_only_fields = ('id',)
        fields = '__all__'