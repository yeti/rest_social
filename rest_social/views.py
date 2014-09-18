from rest_framework import viewsets
from rest_social.rest_social.models import Tag, Comment, Follow, Flag
from rest_social.rest_social.serializers import TagSerializer, CommentSerializer, FollowSerializer, FlagSerializer

__author__ = 'baylee'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
