from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .serializers import ClientSerializer, NotificationSerializer
from .models import Client, Notification, Message

from notification_service.celery import app

from datetime import datetime, timezone
import requests
import json


class ClientViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    http_method_names = ('get', 'post', 'put', 'delete')


def _getlist_helper(data):
    res = []
    for qs in data:
        for obj in qs:
            res.append(obj)
    res = set(res)
    return res


@app.task
def start_notification(data):

    # --------------------- GETTING LIST OG CLIENT IDS FOR NOTIFICATIONS -------------------------------
    # ---------- BY OPERATOR CODE
    data = json.loads(data)
    operator_code_list = data['operator_code_filter']
    clients_by_operator_code__tmp = [] # collecting all querysets as lists of ids...
    for i in operator_code_list:
        clients_by_operator_code__tmp.append(list(Client.objects.values_list('id', flat=True).filter(operator_code=i)))
    clients_op = _getlist_helper(clients_by_operator_code__tmp)
    # ---------- BY TAG
    tag_list = data['tag_filter']
    clients_by_tag__tmp = []
    for i in tag_list:
        clients_by_tag__tmp.append(list(Client.objects.values_list('id', flat=True).filter(tag=i)))
    clients_tag = _getlist_helper(clients_by_operator_code__tmp)

    clients = sorted(list(set(list(clients_tag) + list(clients_op))))

    # ------------ MAKING NEW MESSAGES AND SENDING REQUEST FOR THEM, UPDATING STATUS -------------------
    for client in clients:
        obj = Message.objects.create(sending_datetime=datetime.now(), sending_status="IN QUEUE", notification_id=Notification.objects.filter(id=data['id'])[:1].get(), client=Client.objects.filter(id=client)[:1].get())
        obj.save()

        r = requests.post('https://probe.fbrq.cloud/v1/send/'+str(obj.pk), data=json.dumps({
            "id": int(obj.pk),
            "phone": int(Client.objects.filter(id=client)[:1].get().phone),
            "text": Notification.objects.filter(id=data['id'])[:1].get().message_text,
        }),
             headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODA2MDg1ODYsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IlN3YWVhbWkifQ.qg14tI8ZTKp41NqNETST9cautCCp6WsKgsizX6v-FAc"
        })

        if r.status_code == 200:
            print("Message delievered successfully (id: " + str(obj.id)+")")
            obj.sending_status = "SUCCESS"
            obj.save()
        else:
            print("Message not delievered (id: " + str(obj.id)+")")
            obj.sending_status = "ERROR"
            obj.save()


class NotificationViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    http_method_names = ('get','post', 'put', 'delete')



    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        start_dt = datetime.strptime(request.data['start_datetime'], '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
        end_dt = datetime.strptime(request.data['end_datetime'], '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)
        start_notification.apply_async(args=(json.dumps(serializer.data),), eta=start_dt, expires=end_dt)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)