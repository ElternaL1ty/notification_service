from django.conf.urls import url
from rest_framework import routers
from django.urls import path, include
from .views import ClientViewSet, NotificationViewSet
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token


class OptionalSlashRouter(routers.SimpleRouter):

    def __init__(self):
        super().__init__()
        self.trailing_slash = '/?'


router = OptionalSlashRouter()
router.register(r'clients', ClientViewSet)
router.register(r'notifications', NotificationViewSet)
urlpatterns = [
    path('', include(router.urls)),
    url(r'^token/', obtain_jwt_token),
    url(r'^token-verify/', verify_jwt_token)

]