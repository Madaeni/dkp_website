from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from dkp.models import (
    User,
    Character,
    Dkp,
    Auction,
    Bet,
)
from users.models import Avatar


class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Avatar
        fields = '__all__'


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password'
        ]
        required_fields = ['username', 'email']


class UserSerializer(UserCreateSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        avatar = AvatarSerializer(obj.avatar).data
        avatar = self.context['request'].build_absolute_uri(avatar['avatar'])
        return avatar

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'avatar'
        ]
        required_fields = ['username']


class GetCharacterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = ['id', 'name']


class CreateCharacterSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Character
        fields = ['user', 'name']


class GetDkpListSerializer(serializers.ModelSerializer):
    character = GetCharacterSerializer()

    class Meta:
        model = Dkp
        fields = ['character', 'points', 'last_activity']


class GetAuctionSerializer(serializers.ModelSerializer):
    max_bet = serializers.SerializerMethodField()

    def get_max_bet(self, obj):
        if hasattr(obj, 'max_bet'):
            return {
                'character_id': str(obj.max_bet_character_id),
                'character': obj.max_bet_character,
                'bet': obj.max_bet,
            }
        return None

    class Meta:
        model = Auction
        fields = ['id', 'lot_image', 'close_date', 'max_bet', 'is_active']


class BetSerializer(serializers.ModelSerializer):
    auction_id = GetAuctionSerializer(read_only=True)
    character = GetCharacterSerializer(read_only=True)
    bet = serializers.IntegerField()

    def _get_user_character(self):
        """Получение персонажа текущего пользователя."""
        user = self.context['request'].user
        return user.characters.first()

    def _get_current_max_bid(self, auction_pk):
        """Получение максимальной текущей ставки для аукциона."""
        active_auctions = Auction.objects.filter(is_active=True)
        max_bets = Bet.max_bets(active_auctions)
        return max_bets.get(auction_pk)

    def _validate_dkp_points(self, bet_amount):
        """
        Проверка наличия достаточного
        количества DKP очков у пользователя.
        """
        user = self.context['request'].user
        dkp = user.dkp_users.first()
        current_max_bet = self._get_current_max_bid(
            self.context['view'].kwargs.get('pk')
        )
        user_bets = [bet_amount]
        if (
            current_max_bet and
            current_max_bet['character'] == self._get_user_character()
        ):
            user_bets.append(current_max_bet['bet'])

        if not dkp or sum(user_bets) > dkp.points:
            raise serializers.ValidationError({
                'bet': ['Insufficient points to place this bet!']
            })

    def validate_bet(self, data):
        if not data:
            raise serializers.ValidationError(
                {'bet': ['Required field!']}
            )
        if data < 0:
            raise serializers.ValidationError(
                {'bet': ['The rate cannot be negative!']}
            )
        current_max_bid = self._get_current_max_bid(
            self.context['view'].kwargs.get('pk')
        )
        if current_max_bid:
            if data <= current_max_bid['bet']:
                raise serializers.ValidationError({
                    'bet': [
                        'The bid cannot be less than or '
                        'equal to the previous one!'
                    ]
                })
            if current_max_bid['character'] == self._get_user_character():
                raise serializers.ValidationError({
                    'bet': ['It is forbidden to place two bets in a row!']
                })
        self._validate_dkp_points(data)
        return data

    class Meta:
        model = Bet
        fields = '__all__'
