from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from api.views import (
    UserViewSet,
    AvatarViewSet,
    DkpViewSet,
    AuctionViewSet,
    CharacterViewSet,
    EventViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('avatars', AvatarViewSet, basename='avatars')
router.register('dkp', DkpViewSet, basename='dkp')
router.register('auctions', AuctionViewSet, basename='auctions')
router.register('characters', CharacterViewSet, basename='characters')
router.register('events', EventViewSet, basename='events')

api_urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

docs_urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path(
        'redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('api/', include(docs_urlpatterns)),
]
