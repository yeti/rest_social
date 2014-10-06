from django.conf.urls import patterns, url
from rest_social.rest_social import views

urlpatterns = patterns('',
    url(r'^social_sign_up/$', views.SocialSignUp.as_view(), name="social_sign_up"),
)
