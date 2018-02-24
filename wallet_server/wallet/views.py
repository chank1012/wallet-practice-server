from django.db import transaction
from rest_framework import permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.cooldown import apply_unsafe_cooldown, apply_safe_cooldown
from wallet.models import Wallet
from wallet.serializers import PointSerializer


class WalletViewSet(GenericViewSet):
    queryset = Wallet.objects.none()
    serializer_class = PointSerializer
    permission_classes = permissions.IsAuthenticated,

    @list_route(methods=['post'])
    def unsafe_use_1(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.unsafe_use_1(request.user, serializer.validated_data['point'])
        return Response()

    @list_route(methods=['post'])
    def unsafe_use_2(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.unsafe_use_2(request.user.wallet, serializer.validated_data['point'])
        return Response()

    @list_route(methods=['post'])
    def safe_use_1(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.safe_use_1(request.user.wallet, serializer.validated_data['point'])
        return Response()

    @list_route(methods=['post'])
    def safe_use_2(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.safe_use_2(request.user.wallet, serializer.validated_data['point'])
        return Response()


class CoolWalletViewSet(GenericViewSet):
    queryset = Wallet.objects.none()
    serializer_class = PointSerializer
    permission_classes = permissions.IsAuthenticated,

    @list_route(methods=['post'])
    @apply_unsafe_cooldown(seconds=1.0)
    def unsafe_use(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.safe_use_1(request.user.wallet, serializer.validated_data['point'])
        return Response()

    @list_route(methods=['post'])
    @apply_safe_cooldown(seconds=1.0)
    def safe_use(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            Wallet.safe_use_1(request.user.wallet, serializer.validated_data['point'])
        return Response()
