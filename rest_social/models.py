import abc
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.models import Site
from django.utils.baseconv import base62
import re
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from model_utils import Choices
from manticore_django.manticore_django.models import CoreModel
from rest_user.rest_user.models import AbstractYeti


class FollowableModel():
    """
    Abstract class that used as interface
    This class makes sure that child classes have
    my_method implemented
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def identifier(self):
        return

    @abc.abstractmethod
    def type(self):
        return


class Tag(CoreModel):
    name = models.CharField(max_length=75, unique=True)

    def identifier(self):
        return u"#%s" % self.name

    def type(self):
        return u"tag"

    def __unicode__(self):
        return u"%s" % self.name

FollowableModel.register(Tag)


def relate_tags(sender, **kwargs):
    """
    Intended to be used as a receiver function for a `post_save` signal on models that have tags

    Expects tags is stored in a field called 'related_tags' on implementing model
    and it has a parameter called TAG_FIELD to be parsed
    """
    # If we're saving related_tags, don't save again so we avoid duplicating notifications
    if kwargs['update_fields'] and 'related_tags' not in kwargs['update_fields']:
        return

    changed = False
    # Get the text of the field that holds tags. If there is no field specified, use an empty string. If the field's
    # value is None, use an empty string.
    message = getattr(kwargs['instance'], sender.TAG_FIELD, '') or ''
    for tag in re.findall(ur"#[a-zA-Z0-9_-]+", message):
        tag_obj, created = Tag.objects.get_or_create(name=tag[1:])
        if tag_obj not in kwargs['instance'].related_tags.all():
            kwargs['instance'].related_tags.add(tag_obj)
            changed = True

    if changed:
        kwargs['instance'].save()


def mentions(sender, **kwargs):
    """
    Intended to be used as a receiver function for a `post_save` signal on models that have @mentions
    Implementing model must have an attribute TAG_FIELD where @mentions are stored in raw form

    This function creates notifications but does not associate mentioned users with the created model instance
    """
    if kwargs['created']:
        # Get the text of the field that holds tags. If there is no field specified, use an empty string. If the field's
        # value is None, use an empty string.
        # message = getattr(kwargs['instance'], sender.TAG_FIELD, '') or ''
        # content_object = getattr(kwargs['instance'], 'content_object', kwargs['instance'])
        #
        # for user in re.findall(ur"@[a-zA-Z0-9_.]+", message):
        #     User = get_user_model()
        #     try:
        #         receiver = User.objects.get(username=user[1:])
        #         create_notification(receiver, kwargs['instance'].user, content_object, Notification.TYPES.mention)
        #     except User.DoesNotExist:
        #         pass
        # TODO: implement notifications
        pass


class Comment(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    TAG_FIELD = 'description'
    related_tags = models.ManyToManyField(Tag, blank=True, null=True)

    description = models.CharField(max_length=140)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ['created']

post_save.connect(mentions, sender=Comment)
post_save.connect(relate_tags, sender=Comment)


# Allows a user to 'follow' objects
class Follow(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    @property
    def object_type(self):
        return self.content_type.name

    @property
    def name(self):
        # object must be registered with FollowableModel
        return self.content_object.identifier()

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)
        ordering = ['created']


class Like(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)


# Flag an object for review
class Flag(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("user", "content_type", "object_id"),)


class Share(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_with')

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("user", "content_type", "object_id", "id"),)


class FriendAction(CoreModel):
    TYPES = Choices(*settings.SOCIAL_FRIEND_ACTIONS)

    # Unpack the list of social friend actions from the settings
    action_type = models.PositiveSmallIntegerField(choices=TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    def message(self):
        return unicode(self.TYPES[self.action_type][1])

    def name(self):
        return u"{0}".format(self.TYPES._triples[self.action_type][1])

    def display_name(self):
        return u"{0}".format(self.get_action_type_display())

    class Meta:
        ordering = ['-created']


def create_friend_action(user, content_object, action_type):
    friend_action = FriendAction.objects.create(user=user,
                                                content_object=content_object,
                                                action_type=action_type)
    friend_action.save()


# Currently available social providers
class SocialProvider(CoreModel):
    name = models.CharField(max_length=20)


class BaseSocialModel(models.Model):
    """
    This is an abstract model to be inherited by the main "object" being used in feeds on a social media application.
    It expects that object to override the methods below.
    """

    class Meta:
        abstract = True

    def url(self):
        current_site = Site.objects.get_current()
        return "http://{0}/{1}/".format(current_site.domain, base62.encode(self.pk))

    def facebook_og_info(self):
        # return {'action': '', 'object': '', 'url': self.url()}
        raise NotImplementedError("This has not been implemented")

    def create_social_message(self, provider):
        raise NotImplementedError("This has not been implemented")


class AbstractSocialYeti(AbstractYeti):
    follows = GenericRelation(Follow)

    class Meta:
        abstract = True

    def user_following(self):
        return self.follow_set.filter(
            content_type=ContentType.objects.get(app_label=settings.USER_APP_LABEL, model=settings.USER_MODEL)
        )

    def user_followers(self):
        return Follow.objects.filter(
            content_type=ContentType.objects.get(app_label=settings.USER_APP_LABEL, model=settings.USER_MODEL),
            object_id=self.pk
        )

    def user_following_count(self):
        return self.user_following().count()

    def user_followers_count(self):
        return self.user_followers().count()

    def identifier(self):
        return u"%s" % self.username

    def type(self):
        return u"user"
