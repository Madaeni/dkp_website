from datetime import datetime
from http import HTTPStatus

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from core.constants import (
    HOME_URL,
    DKP_OBJECTS_ON_PAGE,
    LOT_OBJECTS_ON_PAGE,
)
from dkp.forms import RegistrationForm, AuthorizationForm
from dkp.models import Character, Dkp
from dkp.utils import (
    get_dkp_table,
    get_event_types,
    get_event_and_players,
    create_new_event,
    register_for_event,
    close_event,
    delete_player_from_event,
    get_lots,
    get_closed_lots,
    create_new_lot,
    create_new_bet,
    get_paginate,
    get_user_events,
    get_base_context,
    require_character,
)
from website import settings

POST_HANDLERS = {
    'create_event_submit': create_new_event,
    'event_registration_submit': register_for_event,
    'event_close_submit': close_event,
    'event_delete_user_submit': delete_player_from_event,
    'create_lot': create_new_lot,
    'create_bet_submit': create_new_bet,
}


def login_page(request):
    """Генерация страницы логина."""
    template = 'dkp/index.html'
    reg_form = None
    auth_form = None

    if request.method == 'POST':
        if 'reg_submit' in request.POST:
            reg_form = RegistrationForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save()
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        elif 'auth_submit' in request.POST:
            auth_form = AuthorizationForm(request.POST)
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if user is not None and user.is_active:
                login(request, user)
                return redirect(HOME_URL)
    else:
        reg_form = RegistrationForm()
        auth_form = AuthorizationForm()

    context = {
        'reg_form': reg_form,
        'auth_form': auth_form
    }
    return render(request, template, context)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def profile(request):
    """Генерация страницы профиля."""
    template = 'dkp/profile.html'
    character = request.user.characters.first()
    if request.method == 'POST':
        if character:
            character.name = request.POST['character_name']
            character.save()
        else:
            character = Character(
                name=request.POST['character_name'],
                user=request.user
            )
            character.save()
            dkp = Dkp(
                user=request.user,
                character=character,
                last_activity=datetime.now()
            )
            dkp.save()
        return redirect('dkp:profile')
    events = get_user_events(character)[:10] if character else None
    context = {
        'character': character,
        'events': events,
    }
    context.update(get_base_context(request))
    return render(request, template, context)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@require_character
def dkp_table(request):
    """Генерация домашней страницы."""
    template = 'dkp/dkp.html'
    if request.method == 'POST':
        handler = next(
            (
                POST_HANDLERS[key]
                for key in POST_HANDLERS
                if key in request.POST
            ),
            None
        )
        if handler:
            return handler(request)
    dkp_table = get_dkp_table()
    event, event_players = get_event_and_players()
    page_number = request.GET.get('page', 1)
    dkp_paginator = Paginator(dkp_table, DKP_OBJECTS_ON_PAGE)
    dkp_page_obj = get_paginate(dkp_paginator, page_number)
    context = {
        'paginator': dkp_paginator,
        'event_players': event_players,
        'dkp_table': dkp_page_obj,
        'event_types': get_event_types(),
        'event': event,
    }
    context.update(get_base_context(request))
    return render(request, template, context)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@require_character
def auction(request):
    """Генерация домашней страницы."""
    template = 'dkp/dkp.html'
    if request.method == 'POST':
        handler = next(
            (
                POST_HANDLERS[key]
                for key in POST_HANDLERS
                if key in request.POST
            ),
            None
        )
        if handler:
            return handler(request)
    lots = get_lots()
    page_number = request.GET.get('page', 1)
    lot_paginator = Paginator(lots, LOT_OBJECTS_ON_PAGE)
    lot_page_obj = get_paginate(lot_paginator, page_number)
    context = {
        'paginator': lot_paginator,
        'lots': lot_page_obj,
    }
    context.update(get_base_context(request))
    return render(request, template, context)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
@require_character
def closed_auction(request):
    """Генерация домашней страницы."""
    template = 'dkp/dkp.html'
    lots = get_closed_lots()
    page_number = request.GET.get('page', 1)
    lot_paginator = Paginator(lots, LOT_OBJECTS_ON_PAGE)
    lot_page_obj = get_paginate(lot_paginator, page_number)
    context = {
        'paginator': lot_paginator,
        'lots': lot_page_obj,
    }
    context.update(get_base_context(request))
    return render(request, template, context)


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=HTTPStatus.NOT_FOUND)


def csrf_failure(request, reason=''):
    return render(request, 'errors/403csrf.html', status=HTTPStatus.FORBIDDEN)


def internal_server_error(request):
    return render(
        request, 'errors/500.html', status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
