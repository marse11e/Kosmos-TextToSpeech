from django.db.models.signals import post_save
from django.dispatch import receiver

from telegrambot.models import TelegramUser, TryTransform


@receiver(post_save, sender=TelegramUser)
def create_try_transform(sender, instance, created, **kwargs):
    if created:
        TryTransform.objects.create(tuser=instance)