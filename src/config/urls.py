from django.contrib import admin
from django.urls import path, include

from . import settings
from .yasg import urlpaatterns as doc_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("survey.urls")),
]

# Documentation
urlpatterns += doc_urls

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns