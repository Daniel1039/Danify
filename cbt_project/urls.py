from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from cbtapp.admin import admin_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('cbtapp.urls')),
    path('admin/', admin_site.urls),

]






if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
