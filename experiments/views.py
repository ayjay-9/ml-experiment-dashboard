from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Dataset
from .serializers import DatasetSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user).order_by("-uploaded_at")
