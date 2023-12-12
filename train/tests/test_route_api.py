from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train.models import Route, Station
from train.serializers import (
    RouteSerializer,
    RouteDetailSerializer,
    RouteListSerializer
)

ROUTE_URL = reverse("train:route-list")


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


def detail_url(route_id):
    return reverse("train:route-detail", args=[route_id])


class UnauthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_route_list(self):
        response = self.client.get(ROUTE_URL)

        stations = Station.objects.all()
        serializer = RouteSerializer(stations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_list_with_filter_by_source(self):
        source = sample_station(name="filter")
        route1 = sample_route(source=source)
        route2 = sample_route()

        response = self.client.get(ROUTE_URL, {"source": "filt"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_route_list_with_filter_by_destination(self):
        destination = sample_station(name="destination")
        route1 = sample_route(destination=destination)
        route2 = sample_route()

        response = self.client.get(ROUTE_URL, {"destination": "destination"})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_route_detail(self):
        route1 = sample_route()
        url = detail_url(route1.id)
        response = self.client.get(url)

        serializer = RouteDetailSerializer(route1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_route_create_update_delete_forbidden(self):
        station1 = sample_station(name="1")
        station2 = sample_station(name="2")
        payload = {
            "source": station1,
            "destination": station2,
            "distance": 24,
        }
        route1 = sample_route()
        url = detail_url(route1.id)

        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response2 = self.client.put(url, payload)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

        response3 = self.client.patch(url, payload)
        self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)

        response4 = self.client.delete(url, payload)
        self.assertEqual(response4.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.station1 = sample_station(name="1")
        self.station2 = sample_station(name="2")
        self.payload = {
            "source": self.station1,
            "destination": self.station2,
            "distance": 24,
        }

    def test_list_create_route(self):
        response = self.client.post(ROUTE_URL, self.payload)
        route = Route.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in self.payload:
            self.assertEqual(self.payload[key], getattr(route, key))

        self.assertEqual(self.station1, route.source)
        self.assertEqual(self.station2, route.destination)

    def test_source_destination_validation(self):
        payload = {
            "source": self.station1,
            "destination": self.station1,
            "distance": 1,
        }
        station = sample_station(latitude=200)
        payload2 = {
            "source": self.station1,
            "destination": station,
            "distance": 1,
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response2 = self.client.post(ROUTE_URL, payload2)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_route_create_update_delete(self):
        route1 = sample_route()
        url = detail_url(route1.id)

        response = self.client.post(ROUTE_URL, self.payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response2 = self.client.put(url, self.payload)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        response3 = self.client.patch(url, self.payload)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

        response4 = self.client.delete(url, self.payload)
        self.assertEqual(response4.status_code, status.HTTP_204_NO_CONTENT)
