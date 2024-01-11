from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from pagination import OrderPagination
from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Journey,
    Order,
)
from train.permissions import IsAdminOrIfAuthenticatedReadOnly
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
    OrderSerializer,
    OrderListSerializer,
    TrainImageSerializer,
)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        train_type = self.request.query_params.get("train_type")

        if train_type:
            queryset = queryset.filter(train_type__name__icontains=train_type)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("train_type")

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train_type",
                type=str,
                description="Filter by train_type (ex. ?train_type=Train A)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        if self.action == "upload_image":
            return TrainImageSerializer

        return TrainSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser]
    )
    def upload_image(self, request, pk=None):
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__name__icontains=source)

        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )

        if self.action == "list":
            queryset = queryset.select_related("source", "destination")
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=str,
                description="Filter by source (ex. ?source=Bar)",
                required=False,
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description="Filter by destination (ex. ?destination=Bar)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer

        return CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        trains_type = self.request.query_params.get("trains")

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(
                route__destination__name__icontains=destination
            )

        if trains_type:
            trains_ids = [int(str_id) for str_id in trains_type.split(",")]
            queryset = queryset.filter(train__train_type_id__in=trains_ids)

        if self.action == "list" or self.action == "retrieve":
            queryset = (queryset.prefetch_related("crew").select_related(
                "route",
                "train",
                "route__source",
                "route__destination",
                "train__train_type",
            )).annotate(
                tickets_available=(
                        F("train__cargo_num") * F("train__places_in_cargo")
                        - Count("tickets")
                )
            )
        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=str,
                description="Filter by source (ex. ?source=Bar)",
                required=False,
            ),
            OpenApiParameter(
                "destination",
                type=str,
                description="Filter by destination (ex. ?destination=Bar)",
                required=False,
            ),
            OpenApiParameter(
                "trains_type",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by trains_type ids (ex. ?trains_type=1,3)"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__journey__train",
        "tickets__journey",
        "tickets__journey__crew",
    )
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
