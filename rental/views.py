from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm, ContactForm, RegisterForm
from .models import Airport, Booking, Car
from .sample_data import REVIEWS


def home(request):
    cars = Car.objects.filter(is_available=True)[:6]
    airports = Airport.objects.filter(is_active=True)[:14]
    return render(
        request,
        "rental/home.html",
        {
            "cars": cars,
            "airports": airports,
            "reviews": REVIEWS,
            "categories": Car.Category.choices,
        },
    )


def car_list(request):
    cars = Car.objects.filter(is_available=True)
    selected_category = request.GET.get("type") or ""
    query = request.GET.get("q", "").strip()
    selected_airport_id = request.GET.get("airport", "")
    arrival = request.GET.get("arrival", "")
    departure = request.GET.get("departure", "")

    if selected_category:
        cars = cars.filter(category=selected_category)
    if query:
        cars = cars.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(fuel__icontains=query))

    return render(
        request,
        "rental/cars.html",
        {
            "cars": cars,
            "airports": Airport.objects.filter(is_active=True),
            "categories": Car.Category.choices,
            "selected_category": selected_category,
            "selected_airport_id": selected_airport_id,
            "arrival": arrival,
            "departure": departure,
            "query": query,
        },
    )


def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug, is_available=True)
    similar_cars = Car.objects.filter(is_available=True, category=car.category).exclude(pk=car.pk)[:3]
    return render(
        request,
        "rental/car_detail.html",
        {
            "car": car,
            "similar_cars": similar_cars,
            "airport": request.GET.get("airport", ""),
            "arrival": request.GET.get("arrival", ""),
            "departure": request.GET.get("departure", ""),
        },
    )


def booking_create(request):
    initial = _booking_initial_from_request(request)

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            messages.success(request, f"Bron tasdiqlandi: {booking.booking_code}")
            return redirect("booking_success", code=booking.booking_code)
    else:
        form = BookingForm(user=request.user, initial=initial)

    return render(request, "rental/booking.html", {"form": form})


def booking_success(request, code):
    bookings = Booking.objects.select_related("car", "airport", "user")
    if request.user.is_authenticated:
        bookings = bookings.filter(Q(user=request.user) | Q(user__isnull=True, email__iexact=request.user.email))

    booking = get_object_or_404(bookings, booking_code=code)
    return render(request, "rental/booking_success.html", {"booking": booking})


@login_required
def profile(request):
    bookings = Booking.objects.select_related("car", "airport").filter(
        Q(user=request.user) | Q(user__isnull=True, email__iexact=request.user.email)
    )
    return render(request, "rental/profile.html", {"bookings": bookings})


def about(request):
    return render(
        request,
        "rental/about.html",
        {
            "airports_count": Airport.objects.filter(is_active=True).count(),
            "cars_count": Car.objects.filter(is_available=True).count(),
            "reviews": REVIEWS,
        },
    )


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Xabaringiz qabul qilindi. Operator tez orada bog'lanadi.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "rental/contact.html", {"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Akkaunt yaratildi. Endi bronlaringiz profil sahifasida saqlanadi.")
            return redirect("profile")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def _booking_initial_from_request(request):
    initial = {}
    mapping = {
        "car": "car",
        "airport": "airport",
        "arrival": "arrival_date",
        "departure": "departure_date",
    }
    for query_key, form_key in mapping.items():
        value = request.GET.get(query_key)
        if value:
            initial[form_key] = value
    return initial
