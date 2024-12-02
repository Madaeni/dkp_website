from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import (
    GUILD_NAME_MAX_LENGTH,
    CHARACTER_MAX_LENGTH,
    EVENT_NAME_MAX_LENGTH,
    IS_ACTIVE_MAX_LENGTH,
    MOSCOW_TZ,
)
from core.validators import (
    validate_greater_than_zero,
    validate_close_date_greater_than_created_at,
)

User = get_user_model()


class Guild(models.Model):
    name = models.CharField(
        'Название гильдии', unique=True,
        max_length=GUILD_NAME_MAX_LENGTH,
    )
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'гильдия'
        verbose_name_plural = 'Гильдии'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(
        'Имя персонажа', unique=True,
        max_length=CHARACTER_MAX_LENGTH
    )
    guild = models.ForeignKey(
        Guild, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='guild_characters', verbose_name='Гильдия'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='characters', verbose_name='Пользователь'
    )
    created_at = models.DateTimeField('Дата проведения', auto_now_add=True)

    class Meta:
        verbose_name = 'персонаж'
        verbose_name_plural = 'Персонажи'
        ordering = ('name',)

    def __str__(self):
        return self.name


class EventType(models.Model):
    name = models.CharField(
        'Наименование', unique=True,
        max_length=EVENT_NAME_MAX_LENGTH
    )
    cost = models.IntegerField(
        'Стоимость',
        validators=[
            validate_greater_than_zero,
        ]
    )
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'тип события'
        verbose_name_plural = 'Типы событий'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Event(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активный')
        CLOSED = 'closed', _('Завершенный')

    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE,
        related_name='event_types', verbose_name='Тип события'
    )
    created_at = models.DateTimeField('Дата проведения', auto_now_add=True)
    is_active = models.CharField(
        'Статус', max_length=IS_ACTIVE_MAX_LENGTH,
        choices=Status.choices, default=Status.ACTIVE,
    )

    class Meta:
        verbose_name = 'событие'
        verbose_name_plural = 'События'
        ordering = ('-created_at',)

    @property
    def local_created_at(self):
        return self.created_at.astimezone(MOSCOW_TZ)

    def __str__(self):
        formated_date = self.local_created_at.strftime('%H:%M %d.%m.%Y')
        return f'{self.event_type} {formated_date}'


class EventCharacter(models.Model):
    event_id = models.ForeignKey(
        Event, on_delete=models.CASCADE,
        related_name='events', verbose_name='Событие'
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE,
        related_name='event_characters', verbose_name='Персонаж'
    )

    class Meta:
        verbose_name = 'регистация в собитии'
        verbose_name_plural = 'Регистация в собитии'
        ordering = ('event_id',)


class Auction(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активный')
        CLOSED = 'closed', _('Завершенный')

    lot_image = models.ImageField('Изображение лота', upload_to='auctions/',)
    close_date = models.DateTimeField('Дата окончания')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_active = models.CharField(
        'Статус', max_length=IS_ACTIVE_MAX_LENGTH,
        choices=Status.choices, default=Status.ACTIVE,
    )

    class Meta:
        verbose_name = 'аукцион'
        verbose_name_plural = 'Аукционы'
        ordering = ('-created_at',)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        validate_close_date_greater_than_created_at(self.close_date, self)

    def __str__(self):
        formated_date = self.created_at.strftime('%H:%M %Y.%m.%d')
        return f'Аукцион №{self.id} от {formated_date}'


class Bet(models.Model):
    auction_id = models.ForeignKey(
        Auction, on_delete=models.CASCADE,
        related_name='auctions', verbose_name='Аукцион'
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE,
        related_name='bet_characters', verbose_name='Персонаж'
    )
    bet = models.IntegerField('Ставка')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'ставка'
        verbose_name_plural = 'Ставки'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Ставка пользователя {self.character.user.username}'

    @staticmethod
    def max_bets(auctions) -> dict[str, dict]:
        max_bets = {}
        for auction in auctions:
            max_bet = auction.auctions.order_by('-bet').first()
            max_bets['auction_id'] = {
                'character': max_bet.character,
                'bet': max_bet.bet
            }
        return max_bets


class Dkp(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='dkp_users', verbose_name='Имя пользователя'
    )
    character = models.ForeignKey(
        Character, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='dkp_characters', verbose_name='Имя персонажа'
    )
    points = models.IntegerField('Очки дкп', default=0)
    last_activity = models.DateTimeField('Дата последней активности')
    is_active = models.BooleanField('Активный аккаунт', default=True)
    description = models.TextField('Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'DKP'
        verbose_name_plural = 'DKP'
        ordering = ('character__name',)

    def __str__(self):
        return f'DKP пользователя {self.user}'
