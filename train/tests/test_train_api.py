from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import TrainType, Train
from train.serializers import TrainDetailSerializer, TrainSerializer

TRAIN_URL = reverse("train:train-list")


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


def detail_url(train_id):
    return reverse("train:train-detail", args=[train_id])


class UnauthenticatedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_train_list(self):
        response = self.client.get(TRAIN_URL)

        types = TrainType.objects.all()
        serializer = TrainSerializer(types, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_train_detail(self):
        train = sample_train()
        url = detail_url(train.id)
        response = self.client.get(url)

        serializer = TrainDetailSerializer(train)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_train_create_update_delete_forbidden(self):
        type1 = sample_type()
        payload = {
            "name": "Train A",
            "cargo_num": 5,
            "places_in_cargo": 20,
            "train_type": type1,
        }
        train = sample_train()
        url = detail_url(train.id)

        response = self.client.post(TRAIN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response2 = self.client.put(url, payload)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        response3 = self.client.patch(url, payload)
        self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)

        response4 = self.client.delete(url, payload)
        self.assertEqual(response4.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.type1 = sample_type()
        self.payload = {
            "name": "Train A",
            "cargo_num": 5,
            "places_in_cargo": 20,
            "train_type": self.type1.id,
        }

    def test_list_create_train(self):
        response = self.client.post(TRAIN_URL, self.payload)
        train = Train.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.type1, train.train_type)

    def test_train_unique_seats_validation(self):
        response = self.client.post(TRAIN_URL, self.payload)
        response2 = self.client.post(TRAIN_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
