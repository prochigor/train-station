from django.urls import path, include
from rest_framework import routers

from train.views import (
    TrainTypeViewSet,
    TrainListViewSet,
    StationViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainListViewSet)
router.register("stations", StationViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "train"
