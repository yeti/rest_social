from django.conf.urls import patterns, url, include
from rest_social.rest_social import views
from rest_framework import routers
from rest_social.rest_social.views import TagViewSet


router = routers.DefaultRouter()

# These views will normally be overwritten by notification-related views to account for notifications
# They can still be used as-is by registering with the main project router
# router.register(r'follows', FollowViewSet, base_name='follows')
# router.register(r'likes', LikeViewSet, base_name='likes')
# router.register(r'shares', ShareViewSet, base_name='shares')
# router.register(r'comments', CommentViewSet, base_name='comments')

# These views do not expect app-specific notifications
router.register(r'tags', TagViewSet, base_name='tags')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^flag/$', views.FlagView.as_view(), name="flag"),
    url(r'^social_sign_up/$', views.SocialSignUp.as_view(), name="social_sign_up"),
    url(r'^social_friends/$', views.SocialFriends.as_view(), name="social_friends"),
)
