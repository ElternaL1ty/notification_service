from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ClientSerializer, NotificationSerializer
from .models import Client, Notification
# Create your views here.


class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    http_method_names = ('get','post','put', 'delete')


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names = ('get','post','put','delete')