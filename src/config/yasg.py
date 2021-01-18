from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

DESCRIPTION = """
API для системы опросов пользователей.

- получение списка активных опросов
- прохождение опроса: опросы можно проходить анонимно, в качестве идентификатора пользователя в API передаётся числовой ID, по которому сохраняются ответы пользователя на вопросы; один пользователь может участвовать в любом количестве опросов
- получение пройденных пользователем опросов с детализацией по ответам (что выбрано) по ID уникальному пользователя
"""

schema_view = get_schema_view(
    openapi.Info(
        title="Система опросов",
        default_version="v1",
        desctiprion=DESCRIPTION,
        license=openapi.License(name="YM License"),
        contact=openapi.Contact(name="Yuri", email="yurmezence@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpaatterns = [
    path("swagger/",
         schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui"),
    re_path('swagger(?P<format>\.json|\.yaml)',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'),
    path("redoc/",
         schema_view.with_ui("redoc", cache_timeout=0),
         name="schema-redok"),
]
