from rest_framework import serializers
from rest_social.rest_social.models import Tag, Comment, Follow, Flag
from rest_user.rest_user.serializers import UserSerializer

__author__ = 'baylee'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
