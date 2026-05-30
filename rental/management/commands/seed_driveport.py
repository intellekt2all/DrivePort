from django.core.management.base import BaseCommand

from rental.models import Airport, Car
from rental.sample_data import AIRPORTS, CARS


class Command(BaseCommand):
    help = "Seed DrivePort demo airports and cars."

    def handle(self, *args, **options):
        airport_count = 0
        car_count = 0

        for payload in AIRPORTS:
            _, created = Airport.objects.update_or_create(
                code=payload["code"],
                defaults=payload,
            )
            airport_count += int(created)

        for payload in CARS:
            _, created = Car.objects.update_or_create(
                slug=payload["slug"],
                defaults=payload,
            )
            car_count += int(created)

        self.stdout.write(self.style.SUCCESS(f"Seed complete: {airport_count} airports, {car_count} cars created."))
