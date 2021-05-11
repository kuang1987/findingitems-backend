from rest_framework import serializers

from findingitems.users.models import (
    AuthUser,
    UserSettings
)


class UserSettingSerializer(serializers.ModelSerializer):
    default_loc = serializers.IntegerField(source='default_loc.id', read_only=True)

    class Meta:
        model = UserSettings
        fields = ('default_loc',)


class UserLoginSerializer(serializers.ModelSerializer):
    settings = UserSettingSerializer(many=False, source='get_profile')

    class Meta:
        model = AuthUser
        fields = ('id', 'real_name', 'avatar_url', 'settings',)
