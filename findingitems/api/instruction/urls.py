from django.conf.urls import url
from .views import *


app_name = 'api:instruction'
urlpatterns = [
    url(r'add/$', InstructionViewSet.as_view({'post': 'add'})),
    url(r'list/$', InstructionViewSet.as_view({'get': 'list'})),
    url(r'(?P<instruction_id>\d+)/delete/$', InstructionViewSet.as_view({'post': 'remove'})),
    url(r'search/$', InstructionViewSet.as_view({'get': 'search'})),
]