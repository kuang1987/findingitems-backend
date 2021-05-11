from django.conf.urls import url
from .views import *


app_name = 'api:notification'
urlpatterns = [
    url(r'^totalCount/$', NotificationViewSet.as_view({'get': 'count'})),
]