from django.urls import path
from django.contrib.auth.views import LogoutView

from dkp.views import (
    login_page,
    closed_auction,
    dkp_table,
    auction,
    profile,
)
from website import settings

app_name = 'dkp'

urlpatterns = [
    path('login/', login_page, name='web_login'),
    path('profile/', profile, name='profile'),
    path('', dkp_table, name='home'),
    path('auction/', auction, name='auction'),
    path('closed-auctions/', closed_auction, name='closed_auction'),
    path(
        'logout/',
        LogoutView.as_view(template_name=settings.LOGIN_REDIRECT_URL),
        name='web_logout'
    ),
]
