from django.conf.urls import patterns, url, include
from rest_social.rest_social import views
from rest_framework import routers
from rest_social.rest_social.views import FollowViewSet, FlagViewSet, CommentViewSet, ShareViewSet, \
    LikeViewSet, TagViewSet, SocialUserViewSet


router = routers.DefaultRouter()

router.register(r'tags', TagViewSet, base_name='tags')
router.register(r'follows', FollowViewSet, base_name='follows')
router.register(r'likes', LikeViewSet, base_name='likes')
router.register(r'shares', ShareViewSet, base_name='shares')
router.register(r'user_follows', SocialUserViewSet, base_name='user_follows')
router.register(r'comments', CommentViewSet, base_name='comments')
router.register(r'flags', FlagViewSet, base_name='flags')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^social_sign_up/$', views.SocialSignUp.as_view(), name="social_sign_up"),
)
