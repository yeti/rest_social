from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from rest_social.rest_social.models import Tag, Comment, Follow, Flag, Share, Like
from rest_user.rest_user.serializers import UserSerializer, LoginSerializer
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


class ShareSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Share


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like


class PaginatedFollowSerializer(PaginationSerializer):
    class Meta:
        object_serializer_class = FollowSerializer


class FlagSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Flag


class FollowPaginationSerializer(PaginationSerializer):
    def __init__(self, *args, **kwargs):
        """
        Overrode BasePaginationSerializer init to set object serializer as Follow Serializer.
        """
        super(FollowPaginationSerializer, self).__init__(*args, **kwargs)
        results_field = self.results_field
        object_serializer = FollowSerializer
        if 'context' in kwargs:
            context_kwarg = {'context': kwargs['context']}
        else:
            context_kwarg = {}

        self.fields[results_field] = object_serializer(source='object_list',
                                                       many=True,
                                                       **context_kwarg)


class SocialSignUpSerializer(LoginSerializer):
    class Meta(LoginSerializer.Meta):
        fields = ('email', 'username', 'client_id', 'client_secret')
