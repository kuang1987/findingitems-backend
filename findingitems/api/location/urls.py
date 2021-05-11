from django.conf.urls import url
from .views import *


app_name = 'api:instruction'
urlpatterns = [
    url(r'^add/$', LocationViewSet.as_view({'post': 'add'})),
    url(r'membership/list/$', LocationMemberShipViewSet.as_view({'get': 'list'})),
    url(r'membership/(?P<location_membership_id>\d+)/edit/$', LocationMemberShipViewSet.as_view({'post': 'edit'})),
    url(r'membership/(?P<location_membership_id>\d+)/delete/$', LocationMemberShipViewSet.as_view({'post': 'delete'})),
    url(r'membership/(?P<location_membership_id>\d+)/removeMember/$', LocationMemberShipViewSet.as_view({'post': 'remove_member'})),
    url(r'(?P<location_id>\d+)/delete/$', LocationViewSet.as_view({'post': 'destroy'})),
    url(r'invitation/list/$', LocationInvitationViewSet.as_view({'get': 'list'})),
    url(r'invitation/add/$', LocationInvitationViewSet.as_view({'post': 'add'})),
    url(r'invitation/(?P<invitation_id>\d+)/edit/$', LocationInvitationViewSet.as_view({'post': 'edit'})),
    # url(r'(?P<instruction_id>\d+)/delete/$', InstructionViewSet.as_view({'post': 'remove'})),
    # url(r'search/$', InstructionViewSet.as_view({'get': 'search'})),
]