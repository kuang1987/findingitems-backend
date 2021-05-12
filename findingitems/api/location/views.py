from rest_framework.viewsets import GenericViewSet
from findingitems.api.generics import *
from rest_framework.decorators import action
from django.db.models import Q
from .serializers import (
    # LocationListSerializer,
    LocationUpdateSerializer,
    LocationCreateSerializer,
    LocationMemberUpdateSerializer,
    LocationMemberShipListSerializer,
    LocationInvitationSerializer,
)
from findingitems.instruction.models import Instruction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from findingitems.api.permissions import IsUserAuthenticated
from findingitems.location.models import (
    LocationMemberShip,
    LocationMemberInvitation
)
from findingitems.instruction.models import (
    Instruction,
)
from findingitems.users.models import AuthUser

from findingitems.location.models import Location
from findingitems.api.exceptions.common import (
    ParameterInvalid,
    UnknownException
)
from findingitems.api.exceptions import error_msg
from rest_framework import filters
from django.db import transaction
from .permissions import (
    IsLocationOwner,
    IsLocationMemberShipMember,
    IsLocationMemberShipOwner,
    IsLocationInvitationOwner,
    IsLocationMemberShip
)


class LocationViewSet(CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsUserAuthenticated, ]
    lookup_url_kwarg = 'location_id'
    filter_backends = [filters.OrderingFilter,]
    ordering_fields = ['is_default', 'create_time', 'id']

    def get_queryset(self):
        if self.action == 'list':
            return self.request.user.joined_locations.all()
        return self.request.user.locations.all()

    def get_serializer_class(self):
        if self.action == 'edit':
            return LocationUpdateSerializer
        return LocationCreateSerializer

    def get_permissions(self):
        if self.action in ['edit', 'delete']:
            self.permission_classes = [IsUserAuthenticated, IsLocationOwner,]
        else:
            self.permission_classes = [IsUserAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    def set_default(self, serializer):
        is_default = serializer.validated_data.get('is_default', False)
        # if is_default:
        #     locs = self.get_queryset()
        #     for loc in locs:
        #         loc.is_default = False
        #         loc.save()

        serializer.save(
            owner=self.request.user,
            is_default=is_default,
        )
        print(is_default)
        if is_default:
            profile = self.request.user.get_profile()
            profile.default_loc = serializer.instance
            profile.save()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                self.set_default(serializer)
                lms, created = LocationMemberShip.objects.get_or_create(
                    member=self.request.user,
                    location=serializer.instance,
                    role=LocationMemberShip.LOCATION_MEMBER_ROLE_OWNER,
                    alias_name=serializer.instance.name,
                )
                lms.save()
        except:
            raise UnknownException(error_msg.LOCATION_CREATION_FAILURE)
        return self.set_default(serializer)

    @action(methods=['post'], detail=False)
    def add(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                self.set_default(serializer)
                lmss = LocationMemberShip.objects.filter(
                    location=serializer.instance,
                    member=self.request.user,
                    role=LocationMemberShip.LOCATION_MEMBER_ROLE_OWNER
                )
                if lmss.count() == 1:
                    lmss[0].alias_name = serializer.instance.name
                    lmss[0].save()

        except:
            raise UnknownException(error_msg.LOCATION_CREATION_FAILURE)

        return

    @action(methods=['post'], detail=True)
    def edit(self, request, *args, **kwargs):
        name = self.request.data.get('name', None)
        r_locs = self.get_queryset().filter(name=name).exclude(id=self.kwargs['location_id'])
        if r_locs.count() > 0:
            raise ParameterInvalid(error_msg.LOCATION_NAME_REPEAT)
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        try:
            with transaction.atomic():
                ins = Instruction.objects.filter(location=instance)
                ins.delete()

                lms = LocationMemberShip.objects.filter(location=instance)
                lms.delete()

                instance.delete()
        except:
            raise UnknownException(error_msg.LOCATION_DELETION_FAILURE)
        return

    @action(methods=['post'], detail=True)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class LocationMemberShipViewSet(ListModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsUserAuthenticated, ]
    lookup_url_kwarg = 'location_membership_id'

    def get_queryset(self):
        return self.request.user.joined_locations.all()

    def get_permissions(self):
        if self.action in ['delete']:
            self.permission_classes = [IsUserAuthenticated, IsLocationMemberShipMember,]
        elif self.action in ['remove_member']:
            self.permission_classes = [IsUserAuthenticated, IsLocationMemberShipOwner,]
        else:
            self.permission_classes = [IsUserAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'edit':
            return LocationMemberUpdateSerializer
        return LocationMemberShipListSerializer

    def set_default(self, serializer):
        is_default = serializer.validated_data.get('is_default', False)
        if is_default:
            profile = self.request.user.get_profile()
            profile.default_loc = serializer.instance.location
            profile.save()

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
                self.set_default(serializer)
                if self.request.user.id == serializer.instance.location.owner.id:
                    print(serializer.instance.alias_name)
                    print(serializer.instance.location.name)
                    serializer.instance.location.name = serializer.instance.alias_name
                    serializer.instance.location.save()
        except:
            raise UnknownException(error_msg.LOCATION_CREATION_FAILURE)
        return

    @action(methods=['post'], detail=True)
    def edit(self, request, *args, **kwargs):
        name = self.request.data.get('name', None)
        r_locs = self.get_queryset().filter(alias_name=name).exclude(id=self.kwargs['location_membership_id'])
        if r_locs.count() > 0:
            raise ParameterInvalid(error_msg.LOCATION_NAME_REPEAT)
        return self.partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if instance.member == self.request.user and instance.role == LocationMemberShip.LOCATION_MEMBER_ROLE_OWNER:
            raise UnknownException(error_msg.LOCATION_OWNER_CANNOT_BE_MEMBER)

        instance.delete()

    @action(methods=['post'], detail=True)
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=True)
    def remove_member(self, request, *args, **kwargs):
        member_user_id = self.request.data.get('member_user_id', -1)
        try:
            member_user = AuthUser.objects.get(id=member_user_id)
        except ObjectDoesNotExist:
            raise ParameterInvalid(error_msg.LOCATION_MEMBERSHIP_WRONG_USER_ID)

        instance = self.get_object()
        lms = LocationMemberShip.objects.filter(
            member=member_user,
            location=instance.location,
            role=LocationMemberShip.LOCATION_MEMBER_ROLE_MEMBER
        )
        if lms.count() != 1:
            raise ParameterInvalid(error_msg.LOCATION_MEMBERSHIP_WRONG_USER_ID)

        lms.delete()
        return Response({'code': 0,
                         'error_msg': '',
                          'data': {}
                        },
                        status=status.HTTP_200_OK)



class LocationInvitationViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsUserAuthenticated, ]
    lookup_url_kwarg = 'invitation_id'
    filterset_fields = ['status']

    def get_permissions(self):
        if self.action in ['edit']:
            self.permission_classes = [IsUserAuthenticated, IsLocationInvitationOwner,]
        else:
            self.permission_classes = [IsUserAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    def get_queryset(self):
        return LocationMemberInvitation.objects.filter(Q(location__owner=self.request.user)|Q(member=self.request.user)).order_by('-update_date')

    def get_serializer_class(self):
        return LocationInvitationSerializer

    def perform_create(self, serializer):
        loc_id = serializer.data.get('loc_id', -1)
        try:
            loc = Location.objects.get(id=loc_id)
        except ObjectDoesNotExist:
            raise ParameterInvalid(error_msg.LOCATION_PARAMETER_MISSING)

        if loc.owner == self.request.user:
            raise ParameterInvalid(error_msg.LOCATION_PARAMETER_MISSING)

        serializer.save(
            location=loc,
            member=self.request.user,

        )

    @action(methods=['post'], detail=False)
    def add(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loc_id = serializer.validated_data.get('loc_id', -1)
        print(loc_id)
        try:
            loc = Location.objects.get(id=loc_id)
        except ObjectDoesNotExist:
            raise ParameterInvalid(error_msg.LOCATION_NOT_EXIST)

        if loc.owner == self.request.user:
            raise ParameterInvalid(error_msg.LOCATION_OWNER_CANNOT_BE_MEMBER)

        loc_invitation, created = LocationMemberInvitation.objects.get_or_create(
            location=loc,
            member=self.request.user
        )

        lms = LocationMemberShip.objects.filter(
            location=loc,
            member=self.request.user,
            role=LocationMemberShip.LOCATION_MEMBER_ROLE_MEMBER
        )
        if lms.count() > 0:
            raise ParameterInvalid(error_msg.LOCATION_ALREADY_JOINED)

        loc_invitation.status = LocationMemberInvitation.LOCATION_INVITATION_STATUS_PENDING
        loc_invitation.save()

        s = self.get_serializer(instance=loc_invitation)
        headers = self.get_success_headers(s.data)
        return Response({'code': 0,
                         'error_msg': '',
                          'data': s.data
                        },
                        status=status.HTTP_200_OK, headers=headers)

    def perform_update(self, serializer):
        status = serializer.validated_data.get('status', None)
        if status is None:
            raise ParameterInvalid()

        if status == LocationMemberInvitation.LOCATION_INVITATION_STATUS_CONFIRM:
            try:
                with transaction.atomic():
                    invitation = serializer.instance
                    loc_membership, created = LocationMemberShip.objects.get_or_create(
                        location=invitation.location,
                        member=invitation.member,
                        role=LocationMemberShip.LOCATION_MEMBER_ROLE_MEMBER
                    )
                    print(invitation.location.owner.id)
                    if created:
                        loc_membership.alias_name = invitation.location.name
                        loc_membership.save()
                    serializer.save()
            except:
                raise UnknownException(error_msg.LOCATION_MEMBERSHIP_FAIL)

        elif status == LocationMemberInvitation.LOCATION_INVITATION_STATUS_REJECT:
            serializer.save()

        else:
            raise ParameterInvalid()

        return

    @action(methods=['post'], detail=True, permission_classes=[IsUserAuthenticated, IsLocationInvitationOwner, ])
    def edit(self, request, *args, **kwargs):
        print(self.request.user.id)
        return self.partial_update(request, *args, **kwargs)


