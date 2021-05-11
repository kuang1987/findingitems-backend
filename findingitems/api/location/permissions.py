from rest_framework import permissions
from findingitems.location.models import LocationMemberShip


class IsLocationOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsLocationMemberShipMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.member == request.user and obj.role == LocationMemberShip.LOCATION_MEMBER_ROLE_MEMBER


class IsLocationMemberShipOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.user.id)
        return obj.member == request.user and obj.role == LocationMemberShip.LOCATION_MEMBER_ROLE_OWNER


class IsLocationMemberShip(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.member == request.user


class IsLocationInvitationOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.location.owner == request.user
