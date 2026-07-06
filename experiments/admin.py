from django.contrib import admin

from .models import Dataset, Experiment


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "file", "uploaded_at")
    list_filter = ("uploaded_at",)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dataset", "algorithm", "task_type", "status", "created_at")
    list_filter = ("status", "task_type", "algorithm")
