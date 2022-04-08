from django.core import serializers
from django.forms import model_to_dict
from django.shortcuts import render
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .serializers import ClientSerializer, NotificationSerializer
from .models import Client, Notification, Message

from notification_service.celery import app

from datetime import datetime, timezone, timedelta
import requests
import json


@extend_schema_view(
    list=extend_schema(
        summary="Get list of all users",
        responses={
            200: OpenApiResponse(response=ClientSerializer,
                                 description='OK. Got list of all users'),
            401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
        },
    ),
    create=extend_schema(
            summary="Create new user",
            responses={
                201: OpenApiResponse(response=ClientSerializer,
                                     description='Created new user'),
                400: OpenApiResponse(description='Bad request. Something is wrong'),
                401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
            },
        ),
    update=extend_schema(
                summary="Update user info",
                responses={
                    200: OpenApiResponse(response=ClientSerializer,
                                         description='Updated a user'),
                    400: OpenApiResponse(description='Bad request. Something is wrong'),
                    401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                },
            ),
    destroy=extend_schema(
                    summary="Delete user",
                    responses={
                        204: OpenApiResponse(response=ClientSerializer,
                                             description='Deleted a user'),
                        404: OpenApiResponse(description='Not found such user id'),
                        401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                    },
                ),
    retrieve=extend_schema(
                    summary="Get user by id",
                    responses={
                        200: OpenApiResponse(response=ClientSerializer,
                                             description='OK. Got user by id'),
                        401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                    },
                ),


)
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
def send_message(data, client, obj):
    msg = Message.objects.filter(id=obj['id'])[:1].get()
    r = requests.post('https://probe.fbrq.cloud/v1/send/' + str(obj['id']), data=json.dumps({
        "id": int(obj['id']),
        "phone": int(Client.objects.filter(id=client)[:1].get().phone),
        "text": Notification.objects.filter(id=data['id'])[:1].get().message_text,
    }),
      headers={
          "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODA2MDg1ODYsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6IlN3YWVhbWkifQ.qg14tI8ZTKp41NqNETST9cautCCp6WsKgsizX6v-FAc"
      })
    if r.status_code == 200:
        print("Message delievered successfully (id: " + str(obj['id']) + ")")
        msg.sending_status = "SUCCESS"
        msg.save()
    else:
        end_dt = datetime.fromisoformat(data['end_datetime'][:-1]).astimezone(timezone.utc)
        if end_dt>=datetime.now(tz=timezone.utc)+timedelta(seconds=600):
            send_message.apply_async(args=[data, client, obj], countdown=600)
            msg.sending_status = "IN QUEUE"
            msg.save()
            print("Message not delievered (id: " + str(obj['id']) + "). Next try in 10 minutes")
        else:
            msg.sending_status = "ERROR"
            msg.save()
            print("Message not delievered (id: " + str(obj['id']) + "). Notification is over")


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
        send_message.apply_async(args=[data, client, model_to_dict(obj)])






@extend_schema_view(
    list=extend_schema(
        summary="Get list of all notifications with message statistics",
        responses={
            200: OpenApiResponse(response=NotificationSerializer,
                                 description='OK. Got list of all notifications'),
            401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
        },
    ),
    create=extend_schema(
            summary="Create new notification",
            responses={
                201: OpenApiResponse(response=NotificationSerializer,
                                     description='Created new notifications'),
                400: OpenApiResponse(description='Bad request. Something is wrong'),
                401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
            },
        ),
    update=extend_schema(
                summary="Update notification info",
                responses={
                    200: OpenApiResponse(response=NotificationSerializer,
                                         description='Updated a notification'),
                    400: OpenApiResponse(description='Bad request. Something is wrong'),
                    401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                },
            ),
    destroy=extend_schema(
                    summary="Delete notification",
                    responses={
                        204: OpenApiResponse(response=NotificationSerializer,
                                             description='Deleted a notification'),
                        404: OpenApiResponse(description='Not found such notification id'),
                        401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                    },
                ),
    retrieve=extend_schema(
                    summary="Get notification by id with message statistics",
                    responses={
                        200: OpenApiResponse(response=NotificationSerializer,
                                             description='OK. Got notification by id'),
                        401: OpenApiResponse(description='Unauthorized. Insert JWT token into Authorization header'),
                    },
                ),


)
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
        start_dt = datetime.fromisoformat(request.data['start_datetime']).astimezone(timezone.utc)
        end_dt = datetime.fromisoformat(request.data['end_datetime']).astimezone(timezone.utc)
        start_notification.apply_async(args=(json.dumps(serializer.data),), eta=start_dt, expires=end_dt)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


