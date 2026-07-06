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
