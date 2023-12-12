from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import Crew
from train.serializers import CrewSerializer, CrewListSerializer

CREW_URL = reverse("train:crew-list")


def sample_crew(**params):
    defaults = {
        "first_name": "Row",
        "last_name": "Colin"
    }

    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_crew_list(self):
        response = self.client.get(CREW_URL)

        stations = Crew.objects.all()
        serializer = CrewListSerializer(stations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_crew_list_create_forbidden(self):
        payload = {
            "first_name": "Row",
            "last_name": "Colin"
        }
        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_list_admin_create(self):
        self.user = get_user_model().objects.create_user(
            email="ttestuser@test.com",
            password="testpass1",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        payload = {
            "first_name": "Row",
            "last_name": "Colin"
        }
        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
