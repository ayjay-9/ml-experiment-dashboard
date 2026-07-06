from django.contrib import admin
from django.urls import include, path

from core.views import dashboard, register

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", register, name="register"),
    path("experiments/", include("experiments.urls")),
    path("", dashboard, name="dashboard"),
]
