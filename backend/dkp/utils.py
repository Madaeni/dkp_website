import datetime
import pytz

from django.contrib import messages
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.db.models import Prefetch, OuterRef, Subquery, Case, When, Q
from django.db.models.functions import Lower
from django.shortcuts import redirect

from core.constants import HOME_URL, AUCTION_URL
from dkp.models import (
    Dkp,
    EventType,
    Event,
    EventCharacter,
    Auction,
    Bet,
)
from website import settings


def get_dkp_points(user):
    try:
        dkp_object = Dkp.objects.get(user=user)
        dkp_points = dkp_object.points
    except Dkp.DoesNotExist:
        dkp_points = 0
    return dkp_points


def get_dkp_table():
    user_timezone = pytz.timezone('Europe/Moscow')
    table = []
    dkp = Dkp.objects.filter(is_active=True).order_by(Lower('character__name'))
    if dkp:
        for el in dkp:
            last_activity_utc = el.last_activity.replace(tzinfo=pytz.UTC)
            last_activity_local = last_activity_utc.astimezone(user_timezone)
            table.append(
                {
                    'character': el.character if el.character else el.user,
                    'points': el.points,
                    'last_activity': last_activity_local.strftime(
                        '%H:%M %d.%m.%Y'
                    )
                }
            )
    return table


def get_event_types():
    return EventType.objects.all().order_by('name')


def get_user_events(character):
    return Event.objects.filter(
        Q(events__character=character),
        Q(is_active=Event.Status.CLOSED)
    ).distinct()


def get_event_and_players():
    event = (
        Event.objects
        .filter(is_active='active')
        .prefetch_related(Prefetch('events'))
        .first()
    )
    event_players = event.events.all() if event else []
    return event, event_players


def create_new_event(request):
    event_type_id = int(request.POST.get('event_type'))
    event_type = EventType.objects.get(id=event_type_id)
    new_event = Event(event_type=event_type)
    new_event.save()
    return redirect(HOME_URL)


def register_for_event(request):
    event, _ = get_event_and_players()
    characters = request.user.characters.first()
    if not EventCharacter.objects.filter(
        event_id=event, character=characters
    ).exists():
        current_event = EventCharacter(event_id=event, character=characters)
        current_event.save()
    return redirect(HOME_URL)


def close_event(request):
    event, _ = get_event_and_players()
    event.is_active = 'closed'
    event.save()
    event_cost = event.event_type.cost
    participants = EventCharacter.objects.filter(event_id=event)
    for participant in participants:
        dkp_record, _ = Dkp.objects.get_or_create(
            user=participant.character.user,
            character=participant.character,
            defaults={'points': 0, 'last_activity': event.created_at}
        )
        dkp_record.points += event_cost
        dkp_record.last_activity = event.created_at
        dkp_record.save(update_fields=['points', 'last_activity'])
    return redirect(HOME_URL)


def delete_player_from_event(request):
    player_id = request.POST.get("player_id")
    try:
        player_to_remove = EventCharacter.objects.get(pk=player_id)
        player_to_remove.delete()
    except EventCharacter.DoesNotExist:
        pass
    return redirect(HOME_URL)


def get_lots():
    max_bet = Bet.objects.filter(auction_id=OuterRef('pk')).order_by('-bet')
    return Auction.objects.filter(
        is_active='active'
    ).annotate(
        character=Case(
            When(
                auctions__bet__isnull=False,
                then=Subquery(max_bet.values('character__name')[:1])
            ),
            default=None
        ),
        bet=Case(
            When(
                auctions__bet__isnull=False,
                then=Subquery(max_bet.values('bet')[:1])
            ),
            default=None
        )
    ).distinct()


def get_closed_lots():
    max_bet = Bet.objects.filter(auction_id=OuterRef('pk')).order_by('-bet')
    return Auction.objects.filter(
        is_active='closed'
    ).annotate(
        character=Case(
            When(
                auctions__bet__isnull=False,
                then=Subquery(max_bet.values('character__name')[:1])
            ),
            default=None
        ),
        bet=Case(
            When(
                auctions__bet__isnull=False,
                then=Subquery(max_bet.values('bet')[:1])
            ),
            default=None
        )
    ).order_by('-close_date').distinct()


def create_new_lot(request):
    try:
        file = request.FILES['file']
    except KeyError:
        return redirect(AUCTION_URL)
    time_str = request.POST.get('time')
    time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
    moscow_tz = pytz.timezone('Europe/Moscow')
    local_time = datetime.datetime.combine(datetime.date.today(), time_obj)
    local_time_with_tz = moscow_tz.localize(local_time)
    utc_time = local_time_with_tz.astimezone(pytz.utc)
    my_model = Auction()
    my_model.lot_image = file
    my_model.close_date = utc_time
    my_model.save()
    return redirect(AUCTION_URL)


def create_new_bet(request):
    new_bet = request.POST.get('new_bet')
    lot_id = int(request.POST.get('lot_id'))
    if not new_bet:
        messages.error(request, 'Не введено значение ставки.')
        return redirect(AUCTION_URL)
    dkp = request.user.dkp_users.first()
    character = dkp.character
    points = dkp.points
    active_lots = get_lots()
    for active_lot in active_lots:
        if active_lot.id != lot_id:
            if active_lot.character == character.name:
                points -= active_lot.bet
        else:
            if active_lot.character == character.name:
                messages.warning(request, 'Вы уже сделали ставку на этот лот.')
                return redirect(AUCTION_URL)
    try:
        if (points - int(new_bet)) < 0:
            messages.error(request, 'Недостаточно очков DKP для этой ставки.')
            return redirect(AUCTION_URL)
    except ValueError:
        messages.error(request, 'Ошибка ввода значения ставки.')
        return redirect(AUCTION_URL)
    lot = Auction.objects.get(id=lot_id)
    bet = Bet(character=character, bet=new_bet, auction_id=lot)
    bet.save()
    return redirect(AUCTION_URL)


def get_paginate(paginator, page_number):
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def get_base_context(request):
    """Добавляет к контексту словарь с ключами:

    - username: Имя пользователя.
    - dkp_points: Текущее количество DKP.
    - avatar: Аватар пользователя.
    - MEDIA_URL: Ссылка для медиа-файлов.

    Аргументы:
    - request: Объект HttpRequest, содержащий информацию о текущем запросе.

    Возвращает:
    - Словарь с указанными выше ключами.
    """
    based_contaxt = {
        'username': request.user.username,
        'dkp_points': get_dkp_points(request.user),
        'avatar': request.user.avatar,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return based_contaxt


def require_character(view_func):
    def wrapper(request, *args, **kwargs):
        character = request.user.characters.first()
        if not character:
            return redirect('dkp:profile')
        return view_func(request, *args, **kwargs)
    return wrapper