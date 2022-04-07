from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ClientSerializer
from .models import Client
# Create your views here.


class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    http_method_names = ('get','post','put', 'delete')
