from rest_framework.routers import SimpleRouter

from survey import views

router = SimpleRouter()
router.register(r'available-surveys', views.AvailableSurveyViewSet,
                basename='available-surveys')
router.register(r'survey', views.SurveyViewSet, basename='survey')

urlpatterns = router.urls
