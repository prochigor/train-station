from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew, Journey, Order,
)
from train.serializers import (
    TrainTypeSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    TrainSerializer,
    StationSerializer,
    RouteListSerializer,
    RouteSerializer,
    RouteDetailSerializer,
    CrewListSerializer,
    CrewSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer, OrderListSerializer,
    # OrderListSerializer,
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):

    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        return TrainSerializer


class StationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):

    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class CrewViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):

    queryset = Crew.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        return CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.all()
    # queryset = Order.objects.prefetch_related(
    #     "tickets__journey__train", "tickets__journey"
    # )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
