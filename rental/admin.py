from django.contrib import admin

from .models import Airport, Booking, Car, ContactMessage


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "city", "name", "country", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("code", "city", "name")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_per_day", "seats", "fuel", "is_available")
    list_filter = ("category", "fuel", "is_available")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_code", "full_name", "car", "airport", "arrival_date", "departure_date", "total_price", "status")
    list_filter = ("status", "airport", "car__category", "created_at")
    search_fields = ("booking_code", "full_name", "email", "phone", "passport_id", "flight_number")
    readonly_fields = ("booking_code", "days", "service_fee", "total_price", "created_at", "updated_at")
    date_hierarchy = "arrival_date"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_reviewed", "created_at")
    list_filter = ("is_reviewed", "created_at")
    search_fields = ("name", "email", "phone", "message")
