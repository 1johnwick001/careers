from django.contrib import admin
from django.conf import settings
from django.urls import path,include, re_path
from django.conf.urls.static import static

from accounts.views import ErrorTemplateView

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path("", include("accounts.urls")),
    # re_path(r'^(?!dj-admin/).*$', ErrorTemplateView.as_view(), name='404'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)