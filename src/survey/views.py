from django.utils import timezone
from rest_framework.decorators import action

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, \
    CreateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from core.decorators import paginate
from survey.models import Survey, SurveyResult
from survey.serializers import AvailableSurveySerializer, \
    SurveyListSerializer, SurveySerializer


class AvailableSurveyViewSet(ListModelMixin, RetrieveModelMixin,
                             GenericViewSet):
    """
    Активные опросы (Доступные для прохождения на данный момент времени)
    Список всех активных опросов
    Получение опроса по id
    """
    now = timezone.now()
    queryset = Survey.objects.filter(start_at__lte=now, finish_at__gte=now).\
        prefetch_related("questions", "questions__choices").\
        order_by("id", "questions__order_num")
    serializer_class = AvailableSurveySerializer
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]


class SurveyViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin,
                    GenericViewSet):
    """
    Опросы
    Получение списка пройденных опросов,
    создание нового опроса,
    просмотр результатов опроса по id,
    просмотр всех опросов пользователя по user_id
    """

    queryset = SurveyResult.objects.all().prefetch_related(
        "answers", "answers__question", "answers__question__choices")
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return SurveySerializer
        else:
            return SurveyListSerializer

    @paginate
    @action(detail=False, methods=["get"], name="Get user surveys",
            serializer_class=SurveyListSerializer,
            permission_classes=[AllowAny],
            url_path="user/(?P<user_id>[^/.]+)")
    def get_user_surveys(self, request, user_id=None):
        """Спиок опросов пройденных пользователем"""
        queryset = SurveyResult.objects.filter(user_id=user_id).\
            prefetch_related("answers", "answers__question",
                             "answers__question__choices")
        return queryset
