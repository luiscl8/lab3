from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel

User = get_user_model()


class BarrelCreationTests(APITestCase):
    def setUp(self):
        self.provider_a = Provider.objects.create(name="Provider A")
        self.provider_b = Provider.objects.create(name="Provider B")
        
        self.user_a = User.objects.create_user(
            username="usera", 
            password="password123", 
            provider=self.provider_a
        )
        self.client.force_authenticate(user=self.user_a)

    def test_create_barrel_forces_logged_in_user_provider(self):
        payload = {
            "number": "B-999",
            "oil_type": "Olive",
            "liters": 50,
            "provider": self.provider_b.id 
        }
        
        response = self.client.post("/api/barrels/", payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_barrel = Barrel.objects.get(number="B-999")
        self.assertEqual(created_barrel.provider_id, self.provider_a.id)


class BarrelDeleteTests(APITestCase):
    def setUp(self):
        self.provider = Provider.objects.create(name="Provider A")
        self.user = User.objects.create_user(
            username="usera", 
            password="password123", 
            provider=self.provider
        )
        self.client.force_authenticate(user=self.user)
        
        self.billed_barrel = Barrel.objects.create(
            provider=self.provider, 
            billed=True, 
            number="B001", 
            oil_type="Olive", 
            liters=100
        )

    def test_cannot_delete_billed_barrel(self):
        url = f"/api/barrels/{self.billed_barrel.id}/"
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Barrel.objects.filter(id=self.billed_barrel.id).exists())