from datetime import timedelta

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Airport, Booking, Car, ContactMessage


TEXT_CLASS = "form-input"


def add_form_class(field):
    css = field.widget.attrs.get("class", "")
    field.widget.attrs["class"] = f"{css} {TEXT_CLASS}".strip()


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "car",
            "airport",
            "full_name",
            "email",
            "phone",
            "passport_id",
            "flight_number",
            "arrival_date",
            "departure_date",
            "note",
        ]
        labels = {
            "car": "Mashina",
            "airport": "Aeroport",
            "full_name": "To'liq ism",
            "email": "Email",
            "phone": "Telefon",
            "passport_id": "Pasport / ID",
            "flight_number": "Parvoz raqami",
            "arrival_date": "Kelish sanasi",
            "departure_date": "Ketish sanasi",
            "note": "Qo'shimcha izoh",
        }
        widgets = {
            "arrival_date": forms.DateInput(attrs={"type": "date"}),
            "departure_date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 4, "placeholder": "Terminal, bolalar kreslosi yoki boshqa talablar..."}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["car"].queryset = Car.objects.filter(is_available=True).order_by("price_per_day")
        self.fields["airport"].queryset = Airport.objects.filter(is_active=True).order_by("city")
        self.fields["car"].empty_label = "Mashina tanlang..."
        self.fields["airport"].empty_label = "Aeroport tanlang..."

        today = timezone.localdate()
        self.fields["arrival_date"].widget.attrs.setdefault("min", today.isoformat())
        self.fields["departure_date"].widget.attrs.setdefault("min", (today + timedelta(days=1)).isoformat())

        for field in self.fields.values():
            add_form_class(field)

        if not self.is_bound:
            self.fields["arrival_date"].initial = today + timedelta(days=4)
            self.fields["departure_date"].initial = today + timedelta(days=8)

            if user and user.is_authenticated:
                full_name = user.get_full_name() or user.username
                self.fields["full_name"].initial = full_name
                self.fields["email"].initial = user.email

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        labels = {
            "name": "Ismingiz",
            "email": "Email",
            "phone": "Telefon",
            "message": "Xabar",
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "Savolingiz yoki hamkorlik taklifingiz..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            add_form_class(field)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)
    first_name = forms.CharField(label="Ism", max_length=80, required=True)
    last_name = forms.CharField(label="Familiya", max_length=80, required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        labels = {
            "username": "Login",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "jasur1998",
            "first_name": "Jasur",
            "last_name": "Abdullayev",
            "email": "jasur@email.com",
            "password1": "Kamida 8 belgi",
            "password2": "Parolni takrorlang",
        }
        for name, field in self.fields.items():
            add_form_class(field)
            if name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[name]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu email bilan akkaunt bor.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
