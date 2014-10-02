from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_social.rest_social.models import Tag, Comment, Follow, Flag, Share, Like
from rest_social.rest_social.serializers import TagSerializer, CommentSerializer, FollowSerializer, FlagSerializer, \
    ShareSerializer, FollowPaginationSerializer, LikeSerializer
from rest_user.rest_user.views import UserViewSet
from django.contrib.auth import get_user_model

__author__ = 'baylee'


User = get_user_model()


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

    def pre_save(self, obj):
        obj.user = self.request.user


class ShareViewSet(viewsets.ModelViewSet):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer

    def pre_save(self, obj):
        obj.user = self.request.user


class UserFollowViewSet(UserViewSet):

    @detail_route(methods=['get'])
    def following(self, request, pk):
        requested_user = User.objects.get(pk=pk)
        following = requested_user.user_following()
        page = self.paginate_queryset(following)
        serializer = FollowPaginationSerializer(instance=page)
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def followers(self, request, pk):
        requested_user = User.objects.get(pk=pk)
        follower = requested_user.user_followers()
        page = self.paginate_queryset(follower)
        serializer = FollowPaginationSerializer(instance=page)
        return Response(serializer.data)
