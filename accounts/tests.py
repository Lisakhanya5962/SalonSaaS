from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from businesses.models import Business, BusinessMembership


User = get_user_model()


class UserModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!"
        )

    def test_user_is_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, "testuser")

    def test_user_email_is_saved(self):
        self.assertEqual(self.user.email, "test@example.com")

    def test_user_has_default_role(self):
        self.assertEqual(self.user.role, "USER")

    def test_user_password_is_hashed(self):
        self.assertNotEqual(
            self.user.password,
            "TestPassword123!"
        )
        self.assertTrue(
            self.user.check_password("TestPassword123!")
        )

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "testuser")

    def test_email_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="anotheruser",
                    email="test@example.com",
                    password="AnotherPassword123!"
                )



class StaffAccessControlTests(TestCase):

    def setUp(self):
        self.owner_a = User.objects.create_user(
            username="owner_a",
            email="owner_a@example.com",
            password="TestPassword123!"
        )

        self.owner_b = User.objects.create_user(
            username="owner_b",
            email="owner_b@example.com",
            password="TestPassword123!"
        )

        self.staff_b = User.objects.create_user(
            username="staff_b",
            email="staff_b@example.com",
            password="TestPassword123!"
        )

        self.business_a = Business.objects.create(
            name="Business A",
            owner=self.owner_a
        )

        self.business_b = Business.objects.create(
            name="Business B",
            owner=self.owner_b
        )

        BusinessMembership.objects.create(
            business=self.business_a,
            user=self.owner_a,
            role=BusinessMembership.Role.OWNER
        )

        self.membership_b = BusinessMembership.objects.create(
            business=self.business_b,
            user=self.staff_b,
            role=BusinessMembership.Role.BARBER
        )

        self.client.force_login(self.owner_a)

    def test_cannot_edit_staff_from_another_business(self):
        response = self.client.get(
            reverse("edit_staff", args=[self.membership_b.id])
        )

        self.assertRedirects(
            response,
            reverse("staff_list"),
            fetch_redirect_response=False
        )

    def test_cannot_toggle_staff_from_another_business(self):
        response = self.client.post(
            reverse("toggle_staff_status", args=[self.membership_b.id])
        )

        self.assertRedirects(
            response,
            reverse("staff_list"),
            fetch_redirect_response=False
        )

        self.membership_b.refresh_from_db()
        self.assertTrue(self.membership_b.is_active)

    def test_cannot_remove_staff_from_another_business(self):
        response = self.client.post(
            reverse("remove_staff", args=[self.membership_b.id])
        )

        self.assertRedirects(
            response,
            reverse("staff_list"),
            fetch_redirect_response=False
        )

        self.membership_b.refresh_from_db()
        self.assertTrue(self.membership_b.is_active)

    def test_blocked_actions_do_not_change_other_business_membership(self):
        self.client.post(
            reverse("remove_staff", args=[self.membership_b.id])
        )

        self.membership_b.refresh_from_db()

        self.assertTrue(self.membership_b.is_active)
        self.assertEqual(
            self.membership_b.business,
            self.business_b
        )
