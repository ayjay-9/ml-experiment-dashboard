import csv
import io

from rest_framework import serializers

from .algorithms import ALGORITHM_REGISTRY
from .models import Dataset, Experiment


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["id", "file", "column_names", "uploaded_at"]
        read_only_fields = ["column_names", "uploaded_at"]

    def create(self, validated_data):
        uploaded_file = validated_data["file"]
        uploaded_file.seek(0)
        raw = uploaded_file.read()
        header = next(csv.reader(io.StringIO(raw.decode("utf-8"))))
        uploaded_file.seek(0)

        return Dataset.objects.create(
            user=self.context["request"].user,
            file=uploaded_file,
            column_names=header,
        )


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = [
            "id",
            "dataset",
            "target_column",
            "task_type",
            "algorithm",
            "hyperparameters",
            "status",
            "metrics",
            "llm_commentary",
            "error_message",
            "created_at",
            "completed_at",
        ]
        read_only_fields = [
            "status",
            "metrics",
            "llm_commentary",
            "error_message",
            "created_at",
            "completed_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["dataset"].queryset = Dataset.objects.filter(user=request.user)

    def validate(self, attrs):
        task_type = attrs["task_type"]
        algorithm = attrs["algorithm"]
        if algorithm not in ALGORITHM_REGISTRY.get(task_type, {}):
            raise serializers.ValidationError(
                f"'{algorithm}' is not a valid algorithm for task type '{task_type}'"
            )

        dataset = attrs["dataset"]
        if attrs["target_column"] not in dataset.column_names:
            raise serializers.ValidationError(
                f"'{attrs['target_column']}' is not a column in the selected dataset"
            )

        return attrs

    def create(self, validated_data):
        return Experiment.objects.create(user=self.context["request"].user, **validated_data)
