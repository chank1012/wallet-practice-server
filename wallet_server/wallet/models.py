from __future__ import unicode_literals

from django.conf import settings
from django.db import models, transaction
from django.db.models import F


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='wallet')
    point = models.IntegerField()

    @staticmethod
    def unsafe_use_1(user, point):
        with transaction.atomic():
            wallet = user.wallet
            wallet.point -= point
            wallet.save()

    @staticmethod
    def unsafe_use_2(wallet, point):
        with transaction.atomic():
            _ = Wallet.objects.select_for_update().get(id=wallet.id)
            wallet.point -= point
            wallet.save()

    @staticmethod
    def safe_use_1(wallet, point):
        cached_point = wallet.point
        wallet.point = F('point') - point
        wallet.save()
        wallet.point = cached_point - point  # let me remain serializable!

    @staticmethod
    def safe_use_2(wallet, point):
        with transaction.atomic():
            locked_wallet = Wallet.objects.select_for_update().get(id=wallet.id)
            locked_wallet.point -= point
            locked_wallet.save()
