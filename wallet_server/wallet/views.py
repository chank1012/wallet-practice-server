from django.db import transaction
from rest_framework import permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common import PointSerializer
from wallet.models import Wallet


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
