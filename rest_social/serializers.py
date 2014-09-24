from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from rest_social.rest_social.models import Tag, Comment, Follow, Flag
from rest_user.rest_user.serializers import UserSerializer
from videos.models import User

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
    user = UserSerializer(read_only=True)
    user_following = serializers.SerializerMethodField('get_user_follow')

    class Meta:
        model = Follow

    def get_user_follow(self, obj):
        user = User.objects.get(pk=obj.object_id)
        serializer = UserSerializer(user)
        return serializer.data


class PaginatedFollowSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = FollowSerializer


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
