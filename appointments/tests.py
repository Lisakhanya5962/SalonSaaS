
from datetime import datetime, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from appointments.models import Appointment
from businesses.models import Business, BusinessMembership
from customers.models import Customer
from notifications.models import Notification
from scheduling.models import StaffAvailability
from services.models import Service


class CustomerAppointmentSecurityTests(TestCase):

    def setUp(self):
        self.owner_a = User.objects.create_user(
            username="owner_a",
            email="owner_a@example.com",
            password="TestPassword123!",
        )

        self.owner_b = User.objects.create_user(
            username="owner_b",
            email="owner_b@example.com",
            password="TestPassword123!",
        )

        self.business_a = Business.objects.create(
            name="Business A",
            owner=self.owner_a,
        )

        self.business_b = Business.objects.create(
            name="Business B",
            owner=self.owner_b,
        )

        self.customer_user_a = User.objects.create_user(
            username="customer_a",
            email="customer_a@example.com",
            password="TestPassword123!",
        )

        self.customer_user_b = User.objects.create_user(
            username="customer_b",
            email="customer_b@example.com",
            password="TestPassword123!",
        )

        self.customer_a = Customer.objects.create(
            business=self.business_a,
            user=self.customer_user_a,
            first_name="Customer",
            last_name="One",
            phone="0711111111",
        )

        self.customer_b = Customer.objects.create(
            business=self.business_b,
            user=self.customer_user_b,
            first_name="Customer",
            last_name="Two",
            phone="0722222222",
        )

        self.service_a = Service.objects.create(
            business=self.business_a,
            name="Haircut",
            category=Service.Category.HAIRCUT,
            price=150.00,
            duration_minutes=30,
        )

        self.service_b = Service.objects.create(
            business=self.business_b,
            name="Hair Styling",
            category=Service.Category.HAIR,
            price=200.00,
            duration_minutes=45,
        )

        BusinessMembership.objects.create(
            business=self.business_a,
            user=self.owner_a,
            role=BusinessMembership.Role.OWNER,
            is_active=True,
        )

        BusinessMembership.objects.create(
            business=self.business_b,
            user=self.owner_b,
            role=BusinessMembership.Role.OWNER,
            is_active=True,
        )

        self.appointment_a = Appointment.objects.create(
            business=self.business_a,
            customer=self.customer_a,
            service=self.service_a,
            staff=self.owner_a,
            appointment_date=timezone.localdate(),
            start_time=time(10, 0),
            end_time=time(10, 30),
            price=150.00,
            status=Appointment.Status.CONFIRMED,
            created_by=self.owner_a,
        )

        self.appointment_b = Appointment.objects.create(
            business=self.business_b,
            customer=self.customer_b,
            service=self.service_b,
            staff=self.owner_b,
            appointment_date=timezone.localdate(),
            start_time=time(11, 0),
            end_time=time(11, 45),
            price=200.00,
            status=Appointment.Status.CONFIRMED,
            created_by=self.owner_b,
        )

        self.client.force_login(self.customer_user_a)

    def test_customer_can_view_own_appointment(self):
        response = self.client.get(
            reverse(
                "customer_appointment_detail",
                args=[self.appointment_a.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_view_another_customers_appointment(self):
        response = self.client.get(
            reverse(
                "customer_appointment_detail",
                args=[self.appointment_b.id],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_cancel_another_customers_appointment(self):
        response = self.client.post(
            reverse(
                "customer_appointment_cancel",
                args=[self.appointment_b.id],
            )
        )

        self.assertEqual(response.status_code, 404)

        self.appointment_b.refresh_from_db()

        self.assertEqual(
            self.appointment_b.status,
            Appointment.Status.CONFIRMED,
        )

    def test_customer_cannot_cancel_completed_appointment(self):
        self.appointment_a.status = Appointment.Status.COMPLETED
        self.appointment_a.save(update_fields=["status"])

        response = self.client.post(
            reverse(
                "customer_appointment_cancel",
                args=[self.appointment_a.id],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.appointment_a.refresh_from_db()

        self.assertEqual(
            self.appointment_a.status,
            Appointment.Status.COMPLETED,
        )


class CustomerBookingTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="salon_owner",
            email="owner@example.com",
            password="TestPassword123!",
        )

        self.staff = User.objects.create_user(
            username="salon_staff",
            email="staff@example.com",
            password="TestPassword123!",
        )

        self.other_owner = User.objects.create_user(
            username="other_owner",
            email="other@example.com",
            password="TestPassword123!",
        )

        self.other_staff = User.objects.create_user(
            username="other_staff",
            email="other_staff@example.com",
            password="TestPassword123!",
        )

        self.customer_user = User.objects.create_user(
            username="booking_customer",
            email="customer@example.com",
            password="TestPassword123!",
        )

        self.other_customer_user = User.objects.create_user(
            username="other_customer",
            email="other_customer@example.com",
            password="TestPassword123!",
        )

        self.business = Business.objects.create(
            name="Khanya Salon",
            owner=self.owner,
        )

        self.other_business = Business.objects.create(
            name="Other Salon",
            owner=self.other_owner,
        )

        self.customer = Customer.objects.create(
            business=self.business,
            user=self.customer_user,
            first_name="Booking",
            last_name="Customer",
            phone="0733333333",
        )

        self.other_customer = Customer.objects.create(
            business=self.other_business,
            user=self.other_customer_user,
            first_name="Other",
            last_name="Customer",
            phone="0744444444",
        )

        BusinessMembership.objects.create(
            business=self.business,
            user=self.owner,
            role=BusinessMembership.Role.OWNER,
            is_active=True,
        )

        BusinessMembership.objects.create(
            business=self.business,
            user=self.staff,
            role=BusinessMembership.Role.BARBER,
            is_active=True,
        )

        BusinessMembership.objects.create(
            business=self.other_business,
            user=self.other_owner,
            role=BusinessMembership.Role.OWNER,
            is_active=True,
        )

        BusinessMembership.objects.create(
            business=self.other_business,
            user=self.other_staff,
            role=BusinessMembership.Role.BARBER,
            is_active=True,
        )

        self.service = Service.objects.create(
            business=self.business,
            name="Premium Haircut",
            category=Service.Category.HAIRCUT,
            price=180.00,
            duration_minutes=45,
        )

        self.other_service = Service.objects.create(
            business=self.other_business,
            name="Other Haircut",
            category=Service.Category.HAIRCUT,
            price=250.00,
            duration_minutes=60,
        )

        self.booking_date = (
            timezone.localdate() + timedelta(days=7)
        )

        self.booking_time = time(10, 0)

        StaffAvailability.objects.create(
            business=self.business,
            staff=self.staff,
            day_of_week=self.booking_date.weekday(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            is_working=True,
        )

        StaffAvailability.objects.create(
            business=self.other_business,
            staff=self.other_staff,
            day_of_week=self.booking_date.weekday(),
            start_time=time(8, 0),
            end_time=time(17, 0),
            is_working=True,
        )

        self.booking_url = reverse("customer_booking")

        self.client.force_login(self.customer_user)

    def valid_booking_data(self):
        return {
            "service": str(self.service.id),
            "staff": str(self.staff.id),
            "appointment_date": self.booking_date.isoformat(),
            "start_time": self.booking_time.strftime("%H:%M"),
            "notes": "Booking test",
        }

    def test_customer_can_successfully_book_appointment(self):
        response = self.client.post(
            self.booking_url,
            self.valid_booking_data(),
        )

        self.assertRedirects(
            response,
            reverse("customer_dashboard"),
            fetch_redirect_response=False,
        )

        appointment = Appointment.objects.get(
            customer=self.customer,
            business=self.business,
        )

        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.staff, self.staff)
        self.assertEqual(appointment.price, self.service.price)
        self.assertEqual(appointment.created_by, self.customer_user)

        expected_end = (
            datetime.combine(
                self.booking_date,
                self.booking_time,
            )
            + timedelta(minutes=self.service.duration_minutes)
        ).time()

        self.assertEqual(appointment.end_time, expected_end)

    def test_customer_cannot_submit_another_customers_identity(self):
        data = self.valid_booking_data()
        data["customer"] = str(self.other_customer.id)

        response = self.client.post(
            self.booking_url,
            data,
        )

        # The submitted customer is outside the restricted
        # customer queryset, so the form rejects the request.
        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Appointment.objects.filter(
                business=self.business,
            ).exists()
        )

    def test_customer_cannot_book_service_from_another_business(self):
        data = self.valid_booking_data()
        data["service"] = str(self.other_service.id)

        response = self.client.post(
            self.booking_url,
            data,
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Appointment.objects.filter(
                business=self.business,
            ).exists()
        )

    def test_customer_cannot_select_staff_from_another_business(self):
        data = self.valid_booking_data()
        data["staff"] = str(self.other_staff.id)

        response = self.client.post(
            self.booking_url,
            data,
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Appointment.objects.filter(
                business=self.business,
            ).exists()
        )

    def test_booking_notifies_staff_and_owner_but_not_customer(self):
        response = self.client.post(
            self.booking_url,
            self.valid_booking_data(),
        )

        self.assertEqual(response.status_code, 302)

        appointment = Appointment.objects.get(
            customer=self.customer,
            business=self.business,
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.staff,
                appointment=appointment,
                notification_type=Notification.NotificationType.APPOINTMENT_BOOKED,
            ).exists()
        )

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.owner,
                appointment=appointment,
                notification_type=Notification.NotificationType.APPOINTMENT_BOOKED,
            ).exists()
        )

        self.assertFalse(
            Notification.objects.filter(
                recipient=self.customer_user,
                appointment=appointment,
            ).exists()
        )

    def test_inactive_staff_cannot_be_selected_for_booking(self):
        membership = BusinessMembership.objects.get(
            business=self.business,
            user=self.staff,
        )

        membership.is_active = False
        membership.save(update_fields=["is_active"])

        response = self.client.post(
            self.booking_url,
            self.valid_booking_data(),
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Appointment.objects.filter(
                business=self.business,
            ).exists()
        )
