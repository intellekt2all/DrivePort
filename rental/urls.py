from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("mashinalar/", views.car_list, name="car_list"),
    path("mashinalar/<slug:slug>/", views.car_detail, name="car_detail"),
    path("bron/", views.booking_create, name="booking_create"),
    path("bron/<str:code>/", views.booking_success, name="booking_success"),
    path("profil/", views.profile, name="profile"),
    path("biz-haqimizda/", views.about, name="about"),
    path("aloqa/", views.contact, name="contact"),
]
