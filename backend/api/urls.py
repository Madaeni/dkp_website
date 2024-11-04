from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    AvatarViewSet,
    DkpViewSet,
    AuctionViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('avatars', AvatarViewSet, basename='avatars')
router.register('dkp', DkpViewSet, basename='dkp')
router.register('auctions', AuctionViewSet, basename='auctions')

api_urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]
