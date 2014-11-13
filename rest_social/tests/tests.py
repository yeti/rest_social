from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from manticore_django.manticore_django.utils import get_class
from rest_social.rest_social.utils import get_social_model
from rest_user.rest_user.test.factories import UserFactory
from rest_core.rest_core.test import ManticomTestCase
from rest_social.rest_social.models import Follow, Comment, Tag

__author__ = 'winnietong'


User = get_user_model()
SocialModel = get_social_model()
SocialFactory = get_class(settings.SOCIAL_MODEL_FACTORY)


class BaseAPITests(ManticomTestCase):
    def setUp(self):
        super(BaseAPITests, self).setUp()
        self.dev_user = UserFactory()


class FlagTestCase(BaseAPITests):
    def test_users_can_flag_content(self):
        test_user = UserFactory()
        content_type = ContentType.objects.get_for_model(SocialModel)
        flag_url = reverse('flag')
        data = {
            'content_type': content_type.pk,
            'object_id': SocialFactory().pk
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
        data = {
            'content_type': content_type.pk,
            'object_id': SocialFactory().pk,
            'shared_with': [test_user.pk]
        }
        self.assertManticomPOSTResponse(shares_url,
                                       "$shareRequest",
                                       "$shareResponse",
                                       data,
                                       self.dev_user
        )


class LikeTestCase(BaseAPITests):
    def test_users_can_like_content(self):
        content_type = ContentType.objects.get_for_model(SocialModel)
        likes_url = reverse('likes-list')
        data = {
            'content_type': content_type.pk,
            'object_id': SocialFactory().pk,
        }
        self.assertManticomPOSTResponse(likes_url,
                                       "$likeRequest",
                                       "$likeResponse",
                                       data,
                                       self.dev_user
        )


class CommentTestCase(BaseAPITests):
    def test_users_can_comment_on_content(self):
        content_type = ContentType.objects.get_for_model(SocialModel)
        comments_url = reverse('comments-list')
        data = {
            'content_type': content_type.pk,
            'object_id': SocialFactory().pk,
            'description': 'This is a user comment.'
        }
        self.assertManticomPOSTResponse(comments_url,
                                       "$commentRequest",
                                       "$commentResponse",
                                       data,
                                       self.dev_user
        )

    def test_comment_related_tags(self):
        content_type = ContentType.objects.get_for_model(SocialModel)
        Comment.objects.create(content_type=content_type,
                               object_id=1,
                               description='Testing of a hashtag. #django',
                               user=self.dev_user)
        tags_url = reverse('tags-list')
        response = self.assertManticomGETResponse(tags_url,
                                                  None,
                                                  "$tagResponse",
                                                  self.dev_user)
        self.assertEqual(response.data['results'][0]['name'], 'django')
        self.assertIsNotNone(Tag.objects.get(name='django'))


class UserFollowingTestCase(BaseAPITests):
    def test_user_can_follow_each_other(self):
        test_user1 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        follow_url = reverse('follows-list')
        # Dev User to follow Test User 1
        data = {
            'content_type': user_content_type.pk,
            'object_id': test_user1.pk
        }
        response = self.assertManticomPOSTResponse(follow_url,
                                       "$followRequest",
                                       "$followResponse",
                                       data,
                                       self.dev_user
        )
        self.assertEqual(response.data['following']['username'], test_user1.username)

    def test_following_endpoint(self):
        test_user1 = UserFactory()
        test_user2 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        # Dev User to follow User 1, User 2 to follow Dev User
        Follow.objects.create(content_type=user_content_type, object_id=test_user1.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=test_user2)
        following_url = reverse('users-following', args=[self.dev_user.pk])
        response = self.assertManticomGETResponse(following_url,
                                                   None,
                                                   "$followResponse",
                                                   self.dev_user)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['following']['username'], test_user1.username)

    def test_follower_endpoint(self):
        test_user1 = UserFactory()
        test_user2 = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        # Dev User to follow User 1, User 2 to follow Dev User
        Follow.objects.create(content_type=user_content_type, object_id=test_user1.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=test_user2)
        followers_url = reverse('users-followers', args=[self.dev_user.pk])
        response = self.assertManticomGETResponse(followers_url,
                                                   None,
                                                   "$followResponse",
                                                   self.dev_user)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['follower']['username'], test_user2.username)

    def test_user_can_unfollow_user(self):
        follower = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)
        follow_object = Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower)
        follows_url = reverse('follows-detail', kwargs={'pk': follow_object.pk})

        # If you are not the follower of the user, you cannot unfollow the user
        self.assertManticomDELETEResponse(follows_url, self.dev_user, unauthorized=True)

        # If you are the follower of that user, you can unfollow the user
        self.assertManticomDELETEResponse(follows_url, follower)

        # Check that original follow object no longer exists
        self.assertEqual(Follow.objects.filter(pk=follow_object.pk).exists(), False)

    def test_user_following_and_follower_count(self):
        follower1 = UserFactory()
        follower2 = UserFactory()
        following = UserFactory()
        user_content_type = ContentType.objects.get_for_model(User)

        # Follower setup
        Follow.objects.create(content_type=user_content_type, object_id=following.pk, user=self.dev_user)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower1)
        Follow.objects.create(content_type=user_content_type, object_id=self.dev_user.pk, user=follower2)

        users_url = reverse('users-detail', kwargs={'pk': self.dev_user.pk})
        response = self.assertManticomGETResponse(users_url,
                                                  None,
                                                  "$userResponse",
                                                  self.dev_user)
        self.assertEqual(response.data['user_following_count'], 1)
        self.assertEqual(response.data['user_followers_count'], 2)
