from django.urls import path, include
from rest_framework import routers

from train.views import (
    TrainTypeViewSet,
    TrainListViewSet,
)

router = routers.DefaultRouter()
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainListViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

app_name = "train"
