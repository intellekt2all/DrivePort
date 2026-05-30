from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from rental import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("rental.urls")),
    path("kirish/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("chiqish/", auth_views.LogoutView.as_view(), name="logout"),
    path("royxatdan-otish/", views.register, name="register"),
]
