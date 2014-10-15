from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from social.apps.django_app.utils import load_strategy, load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from rest_social.rest_social.models import Tag, Comment, Follow, Flag, Share, Like
from rest_social.rest_social.serializers import TagSerializer, CommentSerializer, FollowSerializer, FlagSerializer, \
    ShareSerializer, FollowPaginationSerializer, LikeSerializer, SocialSignUpSerializer
from rest_user.rest_user.views import UserViewSet, SignUp
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


class SocialUserViewSet(UserViewSet):

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


class SocialSignUp(SignUp):
    serializer_class = SocialSignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            provider = request.DATA['provider']

            # If this request was made with an authenticated user, try to associate this social account with it
            user = request.user if not request.user.is_anonymous() else None

            strategy = load_strategy(request)
            backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)

            if isinstance(backend, BaseOAuth1):
                token = {
                    'oauth_token': request.DATA['access_token'],
                    'oauth_token_secret': request.DATA['access_token_secret'],
                }
            elif isinstance(backend, BaseOAuth2):
                token = request.DATA['access_token']

            user = backend.do_auth(token, user=user)
            serializer.object = user

            if user and user.is_active:
                self.post_save(serializer.object, created=True)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"errors": "Error with social authentication"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
