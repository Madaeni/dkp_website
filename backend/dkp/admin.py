from django.contrib import admin

from dkp.models import (
    Guild,
    Character,
    EventType,
    Event,
    EventCharacter,
    Auction,
    Bet,
    Dkp,
)


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_filter = ['name']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'guild', 'user', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['guild', 'user__username']


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'description']
    search_fields = ['name']
    list_filter = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'created_at', 'is_active']
    search_fields = ['event_type__name', 'created_at', 'is_active']
    list_filter = ['event_type__name', 'created_at', 'is_active']


@admin.register(EventCharacter)
class EventCharacterAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'character']
    search_fields = ['event_id', 'character__name']
    list_filter = ['event_id', 'character__name']


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'created_at', 'close_date', 'is_active'
    ]
    search_fields = ['close_date', 'created_at']
    list_filter = ['close_date', 'created_at', 'is_active']


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['auction_id', 'character', 'bet']
    search_fields = ['auction_id__id', 'character__name',]
    list_filter = ['auction_id__id', 'character__name', 'created_at',]


@admin.register(Dkp)
class DkpAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'character', 'points', 'last_activity', 'is_active'
    ]
    search_fields = ['user__username', 'character__name']
    list_filter = [
        'user__username', 'character__name', 'is_active', 'last_activity'
    ]
