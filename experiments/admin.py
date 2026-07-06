from django.contrib import admin

from .models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file", "uploaded_at")
    list_filter = ("uploaded_at",)
