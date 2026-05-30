from decimal import Decimal
import random
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Airport(models.Model):
    code = models.CharField(max_length=8, unique=True)
    city = models.CharField(max_length=80)
    name = models.CharField(max_length=160)
    country = models.CharField(max_length=80, default="O'zbekiston")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "code"]

    def __str__(self):
        return f"{self.city} ({self.code})"


class Car(models.Model):
    class Category(models.TextChoices):
        SEDAN = "Sedan", "Sedan"
        SUV = "SUV", "SUV / Crossover"
        PREMIUM = "Premium", "Premium"
        MINIVAN = "Minivan", "Minivan"
        ELECTRIC = "Elektr", "Elektr"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.PositiveSmallIntegerField(default=5)
    transmission = models.CharField(max_length=40, default="Avtomat")
    fuel = models.CharField(max_length=40, default="Benzin")
    description = models.TextField(blank=True)
    photo_url = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price_per_day", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("car_detail", kwargs={"slug": self.slug})


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        CONFIRMED = "confirmed", "Tasdiqlandi"
        ACTIVE = "active", "Jarayonda"
        COMPLETED = "completed", "Tugallandi"
        CANCELLED = "cancelled", "Bekor qilindi"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name="bookings")
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="bookings")
    booking_code = models.CharField(max_length=16, unique=True, editable=False)

    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    passport_id = models.CharField(max_length=40)
    flight_number = models.CharField(max_length=40, blank=True)

    arrival_date = models.DateField()
    departure_date = models.DateField()
    days = models.PositiveSmallIntegerField(default=1, editable=False)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking_code} - {self.car}"

    def clean(self):
        if self.arrival_date and self.arrival_date < timezone.localdate():
            raise ValidationError({"arrival_date": "Kelish sanasi bugundan oldin bo'lishi mumkin emas."})
        if self.arrival_date and self.departure_date and self.departure_date <= self.arrival_date:
            raise ValidationError({"departure_date": "Ketish sanasi kelish sanasidan keyin bo'lishi kerak."})

    def calculate_days(self):
        if not self.arrival_date or not self.departure_date:
            return 1
        return max((self.departure_date - self.arrival_date).days, 1)

    def recalculate_total(self):
        self.days = self.calculate_days()
        price_per_day = Decimal(str(self.car.price_per_day))
        subtotal = price_per_day * Decimal(self.days)
        self.service_fee = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
        self.total_price = subtotal + self.service_fee

    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = make_booking_code()
        self.full_clean()
        self.recalculate_total()
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {timezone.localtime(self.created_at).strftime('%Y-%m-%d')}"


def make_booking_code():
    alphabet = string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789"
    while True:
        code = "DP-" + "".join(random.choice(alphabet) for _ in range(6))
        if not Booking.objects.filter(booking_code=code).exists():
            return code
