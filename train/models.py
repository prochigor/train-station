import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/trains/",
        f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    )


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(unique=True)
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains",
    )
    image = models.ImageField(null=True, upload_to=train_image_file_path)

    @property
    def seats_in_train(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
    )
    distance = models.IntegerField()

    @property
    def route(self):
        return f"{self.source.name}-{self.destination.name}"

    @staticmethod
    def validate_route(source, destination, distance, error_to_raise):
        if source == destination:
            raise error_to_raise(
                "Source and destination must be difference"
            )
        distance_x = (source.latitude - destination.latitude) ** 2
        distance_y = (source.longitude - destination.longitude) ** 2
        straight_distance = (distance_x + distance_y) ** 0.5

        if straight_distance > distance:
            raise error_to_raise(
                f"Distance can't be less than {straight_distance}"
            )

    def clean(self):
        Route.validate_route(
            self.source,
            self.destination,
            self.distance,
            ValidationError,
        )

    def __str__(self):
        return (f"{self.source.name}-{self.destination.name},"
                f" distance: {self.distance}")


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        blank=True,
        related_name="journeys"
    )

    @staticmethod
    def validate_journey(departure_time, arrival_time, error_to_raise):
        if departure_time >= arrival_time:
            raise error_to_raise(
                "Departure time must be greater than arrival time"
            )

    def clean(self):
        Journey.validate_journey(
            self.departure_time,
            self.arrival_time,
            ValidationError,
        )

    def __str__(self):
        return (
            f"Route: {self.route}, train: {self.train.name},"
            f" departure time: {self.departure_time},"
            f" arrival_time: {self.arrival_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user} {self.created_at}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return (
            f"Cargo: {self.cargo}, seat: {self.seat}, "
            f"journey: {self.journey.route}, "
            f"order № {self.order.id}, {self.order.created_at}"
        )

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: (
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {train_attr_name}): (1, {count_attrs})"
                        )
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("cargo", "seat", "journey")
        ordering = ["cargo", "seat"]
