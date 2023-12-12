from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Journey,
    Ticket,
    Order,
)


class TrainTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True)

    def create(self, validated_data):
        return TrainType.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class TrainSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "seats_in_train",
            "image",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False, read_only=True)


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image",)


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ("name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs=attrs)
        Route.validate_route(
            attrs["source"],
            attrs["destination"],
            attrs["distance"],
            ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):

    class Meta:
        model = Route
        fields = ("id", "route", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ("id", "full_name")


class JourneySerializer(serializers.ModelSerializer):
    train_image = serializers.ImageField(source="train.image", read_only=True)

    def validate(self, attrs):
        data = super(JourneySerializer, self).validate(attrs=attrs)
        Journey.validate_journey(
            attrs["departure_time"],
            attrs["arrival_time"],
            ValidationError
        )
        return data

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "train_image"
        )


class JourneyListSerializer(JourneySerializer):
    train = serializers.CharField(source="train.name", read_only=True)
    route = serializers.CharField(source="route.route", read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
            "train_image"
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class JourneyDetailSerializer(JourneySerializer):
    train = TrainDetailSerializer(many=False, read_only=True)
    route = RouteDetailSerializer(many=False, read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_places"
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
