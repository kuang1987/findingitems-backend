from rest_framework.viewsets import GenericViewSet
from findingitems.api.generics import *
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from findingitems.api.permissions import IsUserAuthenticated

from findingitems.location.models import (
    LocationMemberInvitation,
)


class NotificationViewSet(GenericViewSet):
    permission_classes = [IsUserAuthenticated, ]

    @action(methods=['get'], detail=False)
    def count(self, request, *args, **kwargs):
        invitation_qs = LocationMemberInvitation.objects.filter(
            location__owner=self.request.user,
            status=LocationMemberInvitation.LOCATION_INVITATION_STATUS_PENDING
        )
        return Response({'code': 0,
                         'error_msg': '',
                         'data': {
                              'invitation_count': invitation_qs.count()
                          }
                        },
                        status=status.HTTP_200_OK)
