from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Dataset, Experiment
from .serializers import DatasetSerializer, ExperimentSerializer
from .tasks import train_experiment


class DatasetViewSet(viewsets.ModelViewSet):
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user).order_by("-uploaded_at")


class ExperimentViewSet(viewsets.ModelViewSet):
    serializer_class = ExperimentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head"]

    def get_queryset(self):
        return Experiment.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        experiment = serializer.save()
        train_experiment.delay(experiment.id)
