from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Api/', include('Api.urls')),
    path('ekg/', include('symtoms.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)