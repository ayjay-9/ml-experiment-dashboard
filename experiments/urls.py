from rest_framework.routers import DefaultRouter

from .views import DatasetViewSet, ExperimentViewSet

app_name = "experiments"

router = DefaultRouter()
router.register("datasets", DatasetViewSet, basename="dataset")
router.register("experiments", ExperimentViewSet, basename="experiment")

urlpatterns = router.urls
