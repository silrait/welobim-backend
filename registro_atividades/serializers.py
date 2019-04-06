from rest_framework import serializers
from .models import CompanyUser, Company, Log
from django.contrib.auth.models import User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CompanyUserGetSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    company = CompanySerializer(many=False, read_only=True)

    class Meta:
        model = CompanyUser
        fields = '__all__'


class CompanyUserPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=False)

    class Meta:
        model = CompanyUser
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')
        user = User.objects.create(**user)
        cu = CompanyUser.objects.create(user=user, **validated_data)
        return cu


class LogSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['get', 'put', 'post', 'delete'])

    class Meta:
        model = Log
        fields = '__all__'

