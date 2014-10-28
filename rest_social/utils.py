from django.core.exceptions import ImproperlyConfigured
from django.apps import apps
import requests
import urllib
import urllib2
from celery.task import task
from django.conf import settings
from twython import Twython


def post_to_facebook(app_access_token, user_social_auth, message, link):
    url = "https://graph.facebook.com/%s/feed" % user_social_auth.uid

    params = {
        'access_token': app_access_token,
        'message': message,
        'link': link
    }

    req = urllib2.Request(url, urllib.urlencode(params))
    urllib2.urlopen(req)


def post_to_facebook_og(app_access_token, user_social_auth, obj):
    og_info = obj.facebook_og_info()

    url = "https://graph.facebook.com/{0}/{1}:{2}".format(
        user_social_auth.uid,
        settings.FACEBOOK_OG_NAMESPACE,
        og_info['action'],
    )

    params = {
        '{0}'.format(og_info['object']): '{0}'.format(og_info['url']),
        'access_token': app_access_token,
    }

    requests.post(url, params=params)


@task
def post_social_media(user_social_auth, social_obj):
    message = social_obj.create_social_message(user_social_auth.provider)
    link = social_obj.url()

    if user_social_auth.provider == 'facebook':
        if settings.USE_FACEBOOK_OG:
            post_to_facebook_og(settings.SOCIAL_AUTH_FACEBOOK_APP_TOKEN, user_social_auth, social_obj)
        else:
            post_to_facebook(settings.SOCIAL_AUTH_FACEBOOK_APP_TOKEN, user_social_auth, message, link)
    elif user_social_auth.provider == 'twitter':
        twitter = Twython(
            app_key=settings.SOCIAL_AUTH_TWITTER_KEY,
            app_secret=settings.SOCIAL_AUTH_TWITTER_SECRET,
            oauth_token=user_social_auth.tokens['oauth_token'],
            oauth_token_secret=user_social_auth.tokens['oauth_token_secret']
        )

        full_message_url = "{0} {1}".format(message, link)

        # 140 characters minus the length of the link minus the space minus 3 characters for the ellipsis
        message_trunc = 140 - len(link) - 1 - 3

        # Truncate the message if the message + url is over 140
        if len(full_message_url) > 140:
            safe_message = "{0}... {1}".format(message[:message_trunc], link)
        else:
            safe_message = full_message_url

        twitter.update_status(status=safe_message, wrap_links=True)


def get_social_model():
    """
    Returns the social model that is active in this project.
    """
    try:
        return apps.get_model(settings.SOCIAL_MODEL)
    except ValueError:
        raise ImproperlyConfigured("SOCIAL_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "SOCIAL_MODEL refers to model '%s' that has not been installed" % settings.SOCIAL_MODEL)
