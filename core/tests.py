from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class DashboardViewTests(TestCase):
    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logged_in_user_sees_dashboard(self):
        user = User.objects.create_user(username="alice", password="testpass123")
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alice")


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "testpass123"}
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("login"), {"username": "alice", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct")

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("login"))


class RegisterViewTests(TestCase):
    def test_get_register_page(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_valid_registration_logs_in_and_redirects(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "a-very-uncommon-pass9",
                "password2": "a-very-uncommon-pass9",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_password_mismatch_does_not_create_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser2",
                "password1": "a-very-uncommon-pass9",
                "password2": "different-pass9",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser2").exists())


class DashboardShellTests(TestCase):
    def test_dashboard_includes_main_script(self):
        user = User.objects.create_user(username="carol", password="testpass123")
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "/static/js/main.js")
        self.assertContains(response, 'id="upload-section"')
        self.assertContains(response, 'id="experiment-section"')
        self.assertContains(response, 'id="results-section"')
