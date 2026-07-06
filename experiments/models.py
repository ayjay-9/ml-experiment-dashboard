from django.conf import settings
from django.db import models


class Dataset(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="datasets"
    )
    file = models.FileField(upload_to="datasets/%Y/%m/%d/")
    column_names = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dataset({self.file.name})"


class Experiment(models.Model):
    TASK_TYPE_CHOICES = [
        ("classification", "Classification"),
        ("regression", "Regression"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="experiments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiments"
    )
    target_column = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    algorithm = models.CharField(max_length=100)
    hyperparameters = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    metrics = models.JSONField(default=dict)
    llm_commentary = models.TextField(blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Experiment({self.algorithm} on {self.dataset_id})"
