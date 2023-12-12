import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import (
    TrainType,
    Train,
    Station,
    Route,
    Journey,
)
from train.serializers import (
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
)

JOURNEY_URL = reverse("train:journey-list")


def sample_type(**params):
    defaults = {
        "name": "Sample type",
    }
    defaults.update(params)
    return TrainType.objects.create(**defaults)


def sample_train(**params):
    type1 = sample_type(name="1")
    defaults = {
        "name": "Train A",
        "cargo_num": 5,
        "places_in_cargo": 20,
        "train_type": type1,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 1.8,
        "longitude": 11.2
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_route(**params):
    station1 = sample_station(name="1")
    station2 = sample_station(name="2")
    defaults = {
        "source": station1,
        "destination": station2,
        "distance": 24,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_journey(**params):
    route = sample_route()
    train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": "2028-11-11",
        "arrival_time": "2028-11-12"
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


def detail_url(journey_id):
    return reverse("train:journey-detail", args=[journey_id])


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(JOURNEY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_journey_list(self):
        sample_journey()
        response = self.client.get(JOURNEY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_journey_detail(self):
        journey = sample_journey()
        url = detail_url(journey.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_journey_create_update_delete_forbidden(self):
        route = sample_route()
        train = sample_train()
        payload = {
            "route": route,
            "train": train,
            "departure_time": "2028-11-11",
            "arrival_time": "2028-11-12"
        }

        response = self.client.post(JOURNEY_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
