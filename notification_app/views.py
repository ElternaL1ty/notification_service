from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .serializers import ClientSerializer, NotificationSerializer
from .models import Client, Notification
from rest_framework.response import Response
from notification_service.celery import app
from datetime import datetime, timezone

class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    http_method_names = ('get','post','put', 'delete')

@app.task
def start_notification():
    print("Test")


class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names = ('get','post','put','delete')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        start_dt = datetime.strptime(request.data['start_datetime'], '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
        end_dt = datetime.strptime(request.data['end_datetime'], '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
        start_notification.apply_async(eta=start_dt, expires=end_dt)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)