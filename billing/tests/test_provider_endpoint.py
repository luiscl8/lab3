from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Barrel

User = get_user_model()


class ProviderEndpointTests(APITestCase):
    def test_provider_list_returns_name_and_tax_id(self):
        provider = Provider.objects.create(
            name="Acme Oils",
            address="Main St 1",
            tax_id="TAX-12345",
        )
        user = User.objects.create_user(
            username="provider_user",
            password="strongpass123",
            provider=provider,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse("provider-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("name", response.data[0])
        self.assertIn("tax_id", response.data[0])
        self.assertEqual(response.data[0]["name"], provider.name)
        self.assertEqual(response.data[0]["tax_id"], provider.tax_id)

class ProviderGetTests(APITestCase):
    def setUp(self):
        self.provider_a = Provider.objects.create(name="Provider A")
        self.provider_b = Provider.objects.create(name="Provider B")
        
        self.barrel_1 = Barrel.objects.create(
            provider=self.provider_a, billed=True, number="B001", oil_type="Olive", liters=100
        )
        self.barrel_2 = Barrel.objects.create(
            provider=self.provider_a, billed=False, number="B002", oil_type="Olive", liters=50
        )
        
        self.user_a = User.objects.create_user(
            username="usera", 
            password="password123", 
            provider=self.provider_a
        )
        
        self.superuser = User.objects.create_superuser(
            username="admin", 
            password="adminpassword123",
            email="admin@test.com"
        )

    def test_superuser_sees_all_providers(self):
        self.client.force_authenticate(user=self.superuser)
        
        response = self.client.get(reverse("provider-list"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Provider.objects.count()) 

    def test_regular_user_sees_only_own_provider_and_liters(self):
        self.client.force_authenticate(user=self.user_a)
        
        response = self.client.get(reverse("provider-list"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        provider_data = response.data[0]
        self.assertEqual(provider_data["name"], self.provider_a.name)
        
        
        self.assertIn("billed_liters", provider_data)
        self.assertIn("liters_to_bill", provider_data)
        
       
        self.assertEqual(provider_data["billed_liters"], 100)
        self.assertEqual(provider_data["liters_to_bill"], 50)