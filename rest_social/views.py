from rest_framework import viewsets
from rest_social.rest_social.models import Tag, Comment, Follow, Flag
from rest_social.rest_social.serializers import TagSerializer, CommentSerializer, FollowSerializer, FlagSerializer
from rest_user.rest_user.serializers import UserSerializer

__author__ = 'baylee'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    user = UserSerializer(read_only=True)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
