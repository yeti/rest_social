import abc
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.baseconv import base62
import re
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from model_utils import Choices
# import urbanairship
from manticore_django.manticore_django.models import CoreModel


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
    message = getattr(kwargs['instance'], sender.TAG_FIELD, '')
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
        message = getattr(kwargs['instance'], sender.TAG_FIELD, '')
        content_object = getattr(kwargs['instance'], 'content_object', kwargs['instance'])

        for user in re.findall(ur"@[a-zA-Z0-9_.]+", message):
            User = get_user_model()
            try:
                receiver = User.objects.get(username=user[1:])
                create_notification(receiver, kwargs['instance'].user, content_object, Notification.TYPES.mention)
            except User.DoesNotExist:
                pass


class Comment(CoreModel):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    TAG_FIELD = 'description'

    description = models.CharField(max_length=140)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ['created']

post_save.connect(mentions, sender=Comment)


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


# Stores user tokens from Urban Airship
class AirshipToken(CoreModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    token = models.CharField(max_length=100)
    expired = models.BooleanField(default=False)


class Notification(CoreModel):
    TYPES = Choices(*settings.SOCIAL_NOTIFICATION_TYPES)
    notification_type = models.PositiveSmallIntegerField(choices=TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="receiver", null=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reporter", null=True, blank=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey()

    def message(self):
        return unicode(Notification.TYPES._triples[self.notification_type][2])

    def push_message(self):
        return "{0} {1}".format(self.reporter, self.message())

    def name(self):
        return u"{0}".format(Notification.TYPES._triples[self.notification_type][1])

    def display_name(self):
        return u"{0}".format(self.get_notification_type_display())

    class Meta:
        ordering = ['-created']


def create_notification(receiver, reporter, content_object, notification_type):
    # # If the receiver of this notification is the same as the reporter or
    # # if the user has blocked this type, then don't create
    # if receiver == reporter or not NotificationSetting.objects.get(
    #         notification_type=notification_type, user=receiver).allow:
    #     return
    #
    # notification = Notification.objects.create(user=receiver,
    #                                            reporter=reporter,
    #                                            content_object=content_object,
    #                                            notification_type=notification_type)
    # notification.save()
    #
    # if AirshipToken.objects.filter(user=receiver, expired=False).exists():
    #     try:
    #         device_tokens = list(AirshipToken.objects.filter(user=receiver, expired=False).
    #                              values_list('token', flat=True))
    #         airship = urbanairship.Airship(settings.AIRSHIP_APP_KEY, settings.AIRSHIP_APP_MASTER_SECRET)
    #
    #         for device_token in device_tokens:
    #             push = airship.create_push()
    #             push.audience = urbanairship.device_token(device_token)
    #             push.notification = urbanairship.notification(
    #                 ios=urbanairship.ios(alert=notification.push_message(), badge='+1'))
    #             push.device_types = urbanairship.device_types('ios')
    #             push.send()
    #     except urbanairship.AirshipFailure:
    #         pass
    pass  # Not sure if we're using Urban Airship going forward


class NotificationSetting(CoreModel):
    notification_type = models.PositiveSmallIntegerField(choices=Notification.TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    allow = models.BooleanField(default=True)

    class Meta:
        unique_together = ('notification_type', 'user')

    def name(self):
        return u"{0}".format(Notification.TYPES._triples[self.notification_type][1])

    def display_name(self):
        return u"{0}".format(self.get_notification_type_display())

def create_notifications(sender, **kwargs):
    sender_name = "{0}.{1}".format(sender._meta.app_label, sender._meta.object_name)
    if sender_name.lower() != settings.AUTH_USER_MODEL.lower():
        return

    if kwargs['created']:
        user = kwargs['instance']
        NotificationSetting.objects.bulk_create(
            [NotificationSetting(user=user, notification_type=pk) for pk, name in Notification.TYPES]
        )

post_save.connect(create_notifications)


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
