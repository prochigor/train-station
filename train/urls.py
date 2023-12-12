from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from train.views import (
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "train"
