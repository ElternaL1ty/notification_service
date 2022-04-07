from rest_framework import routers
from django.contrib import admin
from django.urls import path, include
from .views import ClientViewSet, NotificationViewSet


class OptionalSlashRouter(routers.SimpleRouter):

    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register(r'clients', ClientViewSet)
router.register(r'notifications', NotificationViewSet)
urlpatterns = [
    path('', include(router.urls))
]