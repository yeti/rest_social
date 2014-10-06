from social.apps.django_app.default.models import UserSocialAuth
import urllib
from urllib2 import URLError
from django.core.files import File
from manticore_django.manticore_django.utils import retry_cloudfiles


def social_auth_user(strategy, uid, user=None, *args, **kwargs):
    """
    Allows user to create a new account and associate a social account,
    even if that social account is already connected to a different
    user. It effectively 'steals' the social association from the
    existing user. This can be a useful option during the testing phase
    of a project.

    Return UserSocialAuth account for backend/uid pair or None if it
    doesn't exist.

    Delete UserSocialAuth if UserSocialAuth entry belongs to another
    user.
    """
    social = UserSocialAuth.get_social_auth(kwargs['backend'].name, uid)
    if social:
        if user and social.user != user:
            # Delete UserSocialAuth pairing so this account can now connect
            social.delete()
            social = None
        elif not user:
            user = social.user
    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}


def save_extra_data(strategy, details, response, uid, user, social, *args, **kwargs):
    """Attempt to get extra information from facebook about the User"""

    if user is None:
        return

    if kwargs['backend'].name == "facebook":

        if 'email' in response:
            user.email = response['email']

        if 'location' in response:
            user.location = response['location']['name']

        if 'bio' in response:
            user.about = response['bio']

    user.save()


def get_profile_image(strategy, details, response, uid, user, social, is_new=False, *args, **kwargs):
    """Attempt to get a profile image for the User"""

    # If we don't have a user then just return
    if user is None:
        return

    # Save photo from FB
    if kwargs['backend'].name == "facebook":
        try:
            image_url = "https://graph.facebook.com/%s/picture?type=large" % uid
            result = urllib.urlretrieve(image_url)

            def save_image(user, uid, result):
                user.original_photo.save("%s.jpg" % uid, File(open(result[0])))
                user.save(update_fields=['original_photo'])

            retry_cloudfiles(save_image, user, uid, result)
        except URLError:
            pass
    elif kwargs['backend'].name == "twitter" and social:
        try:
            # Get profile image to save
            if response['profile_image_url'] != '':
                image_result = urllib.urlretrieve(response['profile_image_url'])

                def save_image(user, uid, image_result):
                    user.original_photo.save("%s.jpg" % uid, File(open(image_result[0])))
                    user.save(update_fields=['original_photo'])

                retry_cloudfiles(save_image, user, uid, image_result)
        except URLError:
            pass