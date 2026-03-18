from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from billing.models import Provider, Invoice, Barrel, InvoiceLine

User = get_user_model()

class InvoiceBarrelTests(APITestCase):
    def setUp(self):
        self.provider_a = Provider.objects.create(name="Provider A")
        self.provider_b = Provider.objects.create(name="Provider B")
        
        self.invoice_a = Invoice.objects.create(
            provider=self.provider_a, 
            issued_on="2024-01-01",
            invoice_no="INV-001"
        )
        self.barrel_b = Barrel.objects.create(
            provider=self.provider_b, 
            billed=False, 
            number="B001", 
            oil_type="Olive", 
            liters=100
        )
        
        self.user_a = User.objects.create_user(username="usera", password="password123", provider=self.provider_a)
        self.client.force_authenticate(user=self.user_a)

    def test_add_barrel_from_different_provider_returns_400(self):
        payload = {"barrel": self.barrel_b.id}
        url = f"/api/invoices/{self.invoice_a.id}/add-line/"
        
        response = self.client.post(url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(InvoiceLine.objects.count(), 0)
        
        self.barrel_b.refresh_from_db()
        self.assertFalse(self.barrel_b.billed)


class InvoiceScopingTests(APITestCase):
    def setUp(self):
        self.provider_a = Provider.objects.create(name="Provider A")
        self.provider_b = Provider.objects.create(name="Provider B")
        
        self.user_a = User.objects.create_user(
            username="usera", 
            password="password123", 
            provider=self.provider_a
        )
        self.client.force_authenticate(user=self.user_a)
        
        self.invoice_a = Invoice.objects.create(
            provider=self.provider_a, 
            issued_on="2024-01-01",
            invoice_no="INV-A1"
        )
        self.invoice_b = Invoice.objects.create(
            provider=self.provider_b, 
            issued_on="2024-01-01",
            invoice_no="INV-B1"
        )

    def test_list_invoices_returns_only_provider_a_invoices(self):
        response = self.client.get("/api/invoices/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.invoice_a.id)

    def test_retrieve_other_provider_invoice_returns_404(self):
        url = f"/api/invoices/{self.invoice_b.id}/"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)