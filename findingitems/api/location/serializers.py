from rest_framework import serializers

from findingitems.location.models import (
    Location,
    LocationMemberShip,
    LocationMemberInvitation,
)
from findingitems.users.models import AuthUser
from findingitems.api.exceptions.common import ParameterInvalid
from findingitems.api.exceptions import error_msg


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthUser
        fields = ('id', 'real_name', 'avatar_url')


class LocationCreateSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)

    def validate_name(self, value):
        print('validate')
        if value is None or value == '':
            raise ParameterInvalid(error_msg.LOCATION_NAME_EMPTY)
        locs = Location.objects.filter(name=value)
        if locs.count() > 0:
            raise ParameterInvalid(error_msg.LOCATION_NAME_REPEAT)

        return value

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'owner',
            'create_time',
            'is_default',
        )
        extra_kwargs = {
            "id": {
                'read_only': True
            },
            "create_time": {
                'read_only': True
            },
            "name": {
                'required': True
            },
            "is_default": {
                'write_only': True
            },
        }


class LocationMemberShipListSerializer(serializers.ModelSerializer):
    location = LocationCreateSerializer(many=False, read_only=True)
    owner = UserSerializer(source='get_location_owner', many=False, read_only=True)
    members = UserSerializer(source='get_location_members', many=True, read_only=True)


    class Meta:
        model = LocationMemberShip
        fields = (
            'id',
            'location',
            'role',
            'alias_name',
            'members',
            'owner',
        )
        extra_kwargs = {
            "id": {
                'read_only': True,
            },
            "role": {
                'read_only': True,
            },
            "alias_name": {
                'read_only': True,
            }
        }


class LocationUpdateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        name = attrs.get('name', None)
        is_default = attrs.get('is_default', None)

        if name is None and is_default is None:
            raise ParameterInvalid(error_msg.LOCATION_PARAMETER_MISSING)

        if name == '':
            raise ParameterInvalid(error_msg.LOCATION_NAME_EMPTY)

        return attrs

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'is_default',
            'create_time',
        )
        extra_kwargs = {
            "id": {
                'read_only': True
            },
            "name": {
                'required': False
            },
            "is_default": {
                'required': False,
            },
            "create_time": {
                'read_only': True
            },
        }


class LocationMemberUpdateSerializer(serializers.ModelSerializer):
    location = LocationCreateSerializer(many=False, read_only=True)
    owner = UserSerializer(source='get_location_owner', many=False, read_only=True)
    name = serializers.CharField(write_only=True, required=False)
    is_default = serializers.BooleanField(write_only=True, required=False)

    def validate(self, attrs):
        name = attrs.pop('name', None)
        is_default = attrs.get('is_default', None)

        if name is None and is_default is None:
            raise ParameterInvalid(error_msg.LOCATION_PARAMETER_MISSING)

        if name == '':
            raise ParameterInvalid(error_msg.LOCATION_NAME_EMPTY)

        if name is not None:
            attrs['alias_name'] = name

        return attrs

    class Meta:
        model = LocationMemberShip
        fields = (
            'id',
            'name',
            'location',
            'is_default',
            'role',
            'alias_name',
            'owner',
        )
        extra_kwargs = {
            "id": {
                'read_only': True
            },
            # "name": {
            #     'write_only': True,
            #     'required': False
            # },
            # "is_default": {
            #     'write_only': True,
            #     'required': False,
            # },
            "role": {
                'read_only': True,
            },
            "alias_name": {
                'read_only': True,
            }
        }


class LocationInvitationSerializer(serializers.ModelSerializer):
    location = LocationCreateSerializer(many=False, read_only=True)
    member = UserSerializer(many=False, read_only=True)
    loc_id = serializers.IntegerField(write_only=True, required=True)
    is_owner = serializers.SerializerMethodField(method_name='get_is_owner', read_only=True)

    def get_is_owner(self, obj):
        if obj.location.owner == self.context['request'].user:
            return True

        return False

    class Meta:
        model = LocationMemberInvitation
        fields = (
            'id',
            'location',
            'status',
            'member',
            'loc_id',
            'is_owner'
        )
        extra_kwargs = {
            "id": {
                'read_only': True
            },
        }
