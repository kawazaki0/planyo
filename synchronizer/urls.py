from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# import synchronizer.synchronizer.views


urlpatterns = [
    # path('', include(router.urls)),
    # path('', synchronizer.synchronizer.views.view),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
