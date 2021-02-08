from rest_framework import serializers

from findingitems.instruction.models import Instruction
from findingitems.api.exceptions.common import ParameterInvalid


class InstructionListSerializer(serializers.ModelSerializer):

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
            'create_time'
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
