from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

handler404 = 'dkp.views.page_not_found'
handler500 = 'dkp.views.internal_server_error'

urlpatterns = [
    path('', include('api.urls')),
    path('', include('dkp.urls', namespace='dkp')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
