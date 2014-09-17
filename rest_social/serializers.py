from rest_framework import serializers
from rest_social.rest_social.models import Tag, Comment, Follow

__author__ = 'baylee'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('description', 'user')


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow