from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Airport, Booking, Car
from .sample_data import AIRPORTS, CARS


class RentalFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airport = Airport.objects.create(**AIRPORTS[0])
        cls.car = Car.objects.create(**CARS[0])
        cls.base_arrival = timezone.localdate() + timedelta(days=7)

    def test_booking_total_is_calculated(self):
        booking = Booking.objects.create(
            car=self.car,
            airport=self.airport,
            full_name="Test User",
            email="test@example.com",
            phone="+998901234567",
            passport_id="AA1234567",
            arrival_date=self.base_arrival,
            departure_date=self.base_arrival + timedelta(days=4),
        )

        self.assertEqual(booking.days, 4)
        self.assertEqual(booking.service_fee, Decimal("18.00"))
        self.assertEqual(booking.total_price, Decimal("198.00"))
        self.assertTrue(booking.booking_code.startswith("DP-"))

    def test_public_pages_render(self):
        client = Client()
        for name in ["home", "car_list", "booking_create", "about", "contact", "login", "register"]:
            response = client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_booking_form_creates_booking(self):
        response = self.client.post(
            reverse("booking_create"),
            {
                "car": self.car.pk,
                "airport": self.airport.pk,
                "full_name": "Jasur Abdullayev",
                "email": "jasur@example.com",
                "phone": "+998901234567",
                "passport_id": "AA1234567",
                "flight_number": "HY501",
                "arrival_date": (self.base_arrival + timedelta(days=1)).isoformat(),
                "departure_date": (self.base_arrival + timedelta(days=4)).isoformat(),
                "note": "",
            },
        )

        booking = Booking.objects.get()
        self.assertRedirects(response, reverse("booking_success", kwargs={"code": booking.booking_code}))
        self.assertEqual(booking.total_price, Decimal("148.50"))

    def test_booking_rejects_past_arrival_date(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        tomorrow = timezone.localdate() + timedelta(days=1)

        response = self.client.post(
            reverse("booking_create"),
            {
                "car": self.car.pk,
                "airport": self.airport.pk,
                "full_name": "Jasur Abdullayev",
                "email": "jasur@example.com",
                "phone": "+998901234567",
                "passport_id": "AA1234567",
                "flight_number": "HY501",
                "arrival_date": yesterday.isoformat(),
                "departure_date": tomorrow.isoformat(),
                "note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "arrival_date",
            "Kelish sanasi bugundan oldin bo'lishi mumkin emas.",
        )
        self.assertEqual(Booking.objects.count(), 0)

    def test_booking_model_rejects_reversed_dates_on_save(self):
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                car=self.car,
                airport=self.airport,
                full_name="Test User",
                email="test@example.com",
                phone="+998901234567",
                passport_id="AA1234567",
                arrival_date=timezone.localdate() + timedelta(days=5),
                departure_date=timezone.localdate() + timedelta(days=4),
            )

    def test_car_accepts_long_photo_url(self):
        long_photo_url = "https://example.com/" + ("very-long-path/" * 20) + "car-image.jpg"

        car = Car.objects.create(
            name="Long URL Car",
            slug="long-url-car",
            category=Car.Category.SEDAN,
            price_per_day=Decimal("50.00"),
            seats=5,
            transmission="Avtomat",
            fuel="Benzin",
            description="Long image URL should be stored without the old 200-char limit.",
            photo_url=long_photo_url,
        )

        self.assertGreater(len(long_photo_url), 200)
        self.assertEqual(car.photo_url, long_photo_url)

    def test_admin_car_add_page_renders(self):
        User = get_user_model()
        User.objects.create_superuser(
            username="admin_test",
            email="admin_test@example.com",
            password="DrivePort2026!",
        )

        client = Client()
        self.assertTrue(client.login(username="admin_test", password="DrivePort2026!"))

        response = client.get(reverse("admin:rental_car_add"))
        self.assertEqual(response.status_code, 200)
