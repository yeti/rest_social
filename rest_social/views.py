from rest_framework import viewsets
from rest_social.rest_social.models import Tag, Comment, Follow
from rest_social.rest_social.serializers import TagSerializer, CommentSerializer, FollowSerializer

__author__ = 'baylee'


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
