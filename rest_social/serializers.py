from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from rest_social.rest_social.models import Tag, Comment, Follow, Flag, Share, Like
from rest_user.rest_user.serializers import UserSerializer, LoginSerializer

__author__ = 'baylee'


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'id')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ('related_tags',)

    def __init__(self, *args, **kwargs):
        """
        The `user` field is added here to help with recursive import issues mentioned in rest_user.serializers
        """
        super(CommentSerializer, self).__init__(*args, **kwargs)
        self.fields["user"] = UserSerializer(read_only=True)


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True, source="user")
    following = serializers.SerializerMethodField('get_user_follow')

    class Meta:
        model = Follow
        exclude = ('user',)

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
        read_only_fields = ('username',)
