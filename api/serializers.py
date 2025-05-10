from django.contrib.auth.models import User
from rest_framework import serializers

from vcs.models import Repository


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Паролі не співпадають'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['id', 'name', 'slug']


class RepositoryListSerializer(serializers.ModelSerializer):
    is_author = serializers.SerializerMethodField()
    class Meta:
        model = Repository
        fields = ['id', 'name', 'slug', 'is_author']

    def get_is_author(self, obj):
        author = self.context.get('author')
        return obj.author.id == author.id if author else False


class DirectorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    repo_id = serializers.IntegerField()
    path = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        return validated_data


class RenameDirectorySerializer(serializers.Serializer):
    new_name = serializers.CharField(max_length=255)
    repo_id = serializers.IntegerField()
    path = serializers.CharField(required=False, allow_blank=True)


class FileSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    content = serializers.CharField(required=False, allow_blank=True)
    repo_id = serializers.IntegerField()
    path = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        return validated_data


class RenameFileSerializer(serializers.Serializer):
    new_name = serializers.CharField(max_length=255)
    new_content = serializers.CharField(required=False, allow_blank=True)
    repo_id = serializers.IntegerField()
    path = serializers.CharField(required=False, allow_blank=True)


class UsersSerializer(serializers.ModelSerializer):
    is_author = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'is_author']

    def get_is_author(self, obj):
        author = self.context.get('author')
        return obj.id == author.id if author else False


class UserAddDeleteSerializer(serializers.Serializer):
    repo_id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)