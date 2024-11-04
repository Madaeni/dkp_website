from django.db.models import OuterRef, Subquery, IntegerField
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from api.serializers import (
    UserSerializer,
    AvatarSerializer,
    CreateUserSerializer,
    GetDkpListSerializer,
    GetAuctionSerializer,
    BetSerializer
)
from dkp.models import (
    Bet,
    Dkp,
    Auction,
)
from users.models import Avatar


class UserViewSet(DjoserUserViewSet):
    pagination_class = None
    pk_url_kwarg = 'id'
    search_fields = ['username']
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class AvatarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    pagination_class = None


class DkpViewSet(viewsets.ModelViewSet):
    queryset = Dkp.objects.all()
    serializer_class = GetDkpListSerializer


class AuctionViewSet(viewsets.ModelViewSet):
    pagination_class = None

    def get_queryset(self):
        bet_subquery = Bet.objects.filter(
            auction_id=OuterRef('pk')
        ).order_by('-bet').values(
            'bet', 'character__name', 'character__id'
        )[:1]

        queryset = Auction.objects.annotate(
            max_bet=Subquery(
                bet_subquery.values('bet'), output_field=IntegerField()
            ),
            max_bet_character=Subquery(bet_subquery.values('character__name')),
            max_bet_character_id=Subquery(
                bet_subquery.values('character__id')
            ),
        ).prefetch_related('auctions__character')
        return queryset

    def get_serializer_class(self):
        if self.action == 'bet':
            return BetSerializer
        return GetAuctionSerializer

    @action(
        detail=True,
        methods=['GET', 'POST'],
        permission_classes=[IsAuthenticated],
    )
    def bet(self, request, *args, **kwargs):
        auction = get_object_or_404(Auction, pk=kwargs.get('pk'))
        if request.method == 'GET':
            bets = Bet.objects.filter(auction_id=auction).select_related(
                'character__user'
            )
            serializer = self.get_serializer(bets, many=True)
            return Response(serializer.data)
        serializer = self.get_serializer(data=request.data)
        character = request.user.characters.first()
        serializer.is_valid(raise_exception=True)
        serializer.save(auction_id=auction, character=character)
        return Response(serializer.data)
