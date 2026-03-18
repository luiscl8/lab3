from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class SignupEndpointTests(APITestCase):
    def test_signup_create_successfully(self):
        payload = {
            "username": "newuser",
            "password": "strongpass123",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertEqual(response.data["last_name"], payload["last_name"])
        
        self.assertNotIn("password", response.data)

        created_user = User.objects.get(username=payload["username"])
        self.assertTrue(created_user.check_password(payload["password"]))

    def test_signup_fails_when_first_and_last_names_are_missing(self):
       
        payload = {
            "username": "incompleteuser",
            "password": "strongpass123",
            "email": "missing@example.com",
        }

        response = self.client.post(reverse("user-signup"), payload, format="json")

       
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        
        self.assertFalse(User.objects.filter(email=payload["email"]).exists())