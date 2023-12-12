from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import Station
from train.serializers import StationSerializer

STATION_URL = reverse("train:station-list")


def sample_station(**params):
    defaults = {
        "name": "Sample station",
        "latitude": 1.8,
        "longitude": 11.2
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(STATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_station_list(self):
        response = self.client.get(STATION_URL)

        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_station_list_create_forbidden(self):
        payload = {
            "name": "station",
            "latitude": 11.8,
            "longitude": 11.2
        }
        response = self.client.post(STATION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_station_list_admin_create(self):
        self.user = get_user_model().objects.create_user(
                        email="ttestuser@test.com",
                        password="testpass1",
                        is_staff=True
                    )
        self.client.force_authenticate(self.user)
        payload = {
            "name": "station",
            "latitude": 11.8,
            "longitude": 11.2
        }
        response = self.client.post(STATION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
