from rest_framework import serializers

from findingitems.instruction.models import Instruction
from findingitems.api.exceptions.common import ParameterInvalid
from findingitems.users.models import AuthUser
from findingitems.location.models import LocationMemberShip


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthUser
        fields = ('id', 'real_name', 'avatar_url')


class InstructionListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    location_alias_name = serializers.SerializerMethodField(method_name='get_location_alias_name', read_only=True)
    location_id = serializers.IntegerField(required=False)

    def get_location_alias_name(self, obj):
        lms = LocationMemberShip.objects.filter(
            location=obj.location,
            member=self.context['request'].user
        )
        if lms.count() == 1:
            return lms[0].alias_name

        return obj.location.name if obj.location else ''

    def validate_text(self, value):
        if value == '':
            raise ParameterInvalid()

        return value

    class Meta:
        model = Instruction
        fields = (
            'id',
            'audio_url',
            'text',
            'type',
            'create_time',
            'owner',
            'location_id',
            'location_alias_name'
        )
        extra_kwargs = {
            "id": {
                'read_only': True
            },
            "create_time": {
                'read_only': True
            },
            "audio_url": {
                'required': True,
            },
            "text": {
                'required': True,
            },
            "type": {
                'required': True,
            },
        }
