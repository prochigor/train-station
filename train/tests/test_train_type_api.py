from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import TrainType
from train.serializers import TrainTypeSerializer

TRAIN_TYPE_URL = reverse("train:traintype-list")


def sample_type(**params):
    defaults = {
        "name": "Sample type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


class UnauthenticatedTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_train_type_list(self):
        response = self.client.get(TRAIN_TYPE_URL)

        train_types = TrainType.objects.all()
        serializer = TrainTypeSerializer(train_types, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_train_type_list_create_forbidden(self):
        payload = {"name": "train_type"}
        response = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_train_type_list_admin_create(self):
        self.user = get_user_model().objects.create_user(
                        email="ttestuser@test.com",
                        password="testpass1",
                        is_staff=True
                    )
        self.client.force_authenticate(self.user)
        payload = {"name": "train_type"}

        response = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
