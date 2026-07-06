import csv
import io

from rest_framework import serializers

from .models import Dataset


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
