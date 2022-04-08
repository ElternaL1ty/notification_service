from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from . import tasks
from .serializers import ClientSerializer, NotificationSerializer

from .models import Client, Notification

import json
from datetime import datetime, timezone


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
    http_method_names = ('get', 'post', 'put', 'delete')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        start_dt = datetime.fromisoformat(request.data['start_datetime']).astimezone(timezone.utc)
        end_dt = datetime.fromisoformat(request.data['end_datetime']).astimezone(timezone.utc)
        tasks.start_notification.apply_async(args=(json.dumps(serializer.data),), eta=start_dt, expires=end_dt)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


