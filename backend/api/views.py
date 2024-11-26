from django.db.models import OuterRef, Subquery, IntegerField
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from api.permissions import DkpPermission, CharacterPermission
from api.serializers import (
    UserSerializer,
    AvatarSerializer,
    CreateUserSerializer,
    GetDkpListSerializer,
    GetAuctionSerializer,
    GetCharacterSerializer,
    BetSerializer,
    EventSerializer,
    EventCharacterSerializer,
)
from dkp.models import (
    Bet,
    Dkp,
    Auction,
    Character,
    Event,
    EventCharacter
)
from users.models import Avatar


@extend_schema(tags=['Users'])
class UserViewSet(DjoserUserViewSet):
    pagination_class = None
    pk_url_kwarg = 'id'
    search_fields = ['username']
    http_method_names = ['get', 'post', 'put']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(
        methods=['get', 'put'],
        detail=False
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance

        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=['Avatar'])
class AvatarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Avatar.objects.all()
    serializer_class = AvatarSerializer
    pagination_class = None


@extend_schema(tags=['DKP'])
class DkpViewSet(viewsets.ModelViewSet):
    queryset = Dkp.objects.all()
    serializer_class = GetDkpListSerializer
    http_method_names = ['get', 'patch']

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        dkp_data = self.queryset.filter(user=user).first()
        if not dkp_data:
            return Response(
                {'detail': 'Нет данных о DKP для этого пользователя'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(dkp_data)
        return Response(serializer.data)


@extend_schema(tags=['Auction'])
class AuctionViewSet(viewsets.ModelViewSet):
    pagination_class = None
    http_method_names = ['get', 'post']
    permission_classes = [DkpPermission]

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


@extend_schema(tags=['Characters'])
class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = GetCharacterSerializer
    http_method_names = ['get', 'post', 'put']
    permission_classes = [CharacterPermission]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Events'])
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    pagination_class = None
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'character':
            return EventCharacterSerializer
        return EventSerializer

    @action(
        detail=True,
        methods=['GET', 'POST'],
        permission_classes=[IsAuthenticated],
    )
    def character(self, request, *args, **kwargs):
        if request.method == 'GET':
            event_characters = EventCharacter.objects.filter(
                event_id=kwargs.get('pk')
            )
            serializer = self.get_serializer(event_characters, many=True)
            return Response(serializer.data)
        request.data['event_id'] = kwargs.get('pk')
        character = request.user.characters.first()
        if not character:
            return Response(
                {'error': 'У вас нет персонажей'},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.data['character'] = character.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
