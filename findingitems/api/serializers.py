from rest_framework import serializers

from findingitems.users.models import AuthUser


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthUser
        fields = ('id', 'real_name', 'avatar_url', )
