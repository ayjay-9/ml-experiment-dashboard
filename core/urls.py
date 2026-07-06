from django.contrib import admin
from django.urls import include, path

from core.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("experiments/", include("experiments.urls")),
    path("", dashboard, name="dashboard"),
]
