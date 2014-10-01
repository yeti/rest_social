from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from rest_core.rest_core.factories import UserFactory
from rest_core.rest_core.test import ManticomTestCase
from django.conf import settings
from django.apps import apps as django_apps

__author__ = 'winnietong'


User = get_user_model()
SocialModel = django_apps.get_model(settings.SOCIAL_MODEL)


class BaseAPITests(ManticomTestCase):
    def setUp(self):
        super(BaseAPITests, self).setUp()
        self.dev_user = UserFactory()


class FlagTestCase(BaseAPITests):
    def test_users_can_flag_content(self):
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(SocialModel)
        flag_url = reverse('flags-list')
        # Dev User to follow Test User 1
        data = {
            'content_type': content_type.pk,
            'object_id': 1,
            'user': test_user.pk
        }
        self.assertManticomPOSTResponse(flag_url,
                                       "$flagRequest",
                                       "$flagResponse",
                                       data,
                                       test_user
        )


class ShareTestCase(BaseAPITests):
    def test_users_can_share_content(self):
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(SocialModel)
        shares_url = reverse('shares-list')
        # Dev User to follow Test User 1
        data = {
            'content_type': content_type.pk,
            'object_id': 1,
            'shared_with': [test_user.pk],
            'user': self.dev_user.pk
        }
        self.assertManticomPOSTResponse(shares_url,
                                       "$shareRequest",
                                       "$shareResponse",
                                       data,
                                       self.dev_user
        )


class CommentTestCase(BaseAPITests):
    def test_users_can_comment_on_content(self):
        content_type = ContentType.objects.get_for_model(SocialModel)
        comments_url = reverse('comments-list')
        data = {
            'content_type': content_type.pk,
            'object_id': 1,
            'description': 'This is a user comment.',
            'user': self.dev_user.pk
        }
        self.assertManticomPOSTResponse(comments_url,
                                       "$commentRequest",
                                       "$commentResponse",
                                       data,
                                       self.dev_user
        )
