from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Dataset

User = get_user_model()


class ExperimentsAppConfigTests(TestCase):
    def test_app_is_installed(self):
        self.assertTrue(apps.is_installed("experiments"))


class DatasetModelTests(TestCase):
    def test_create_dataset_for_user(self):
        user = User.objects.create_user(username="alice", password="testpass123")
        upload = SimpleUploadedFile("iris.csv", b"a,b,c\n1,2,3\n", content_type="text/csv")

        dataset = Dataset.objects.create(
            user=user,
            file=upload,
            column_names=["a", "b", "c"],
        )

        self.assertEqual(dataset.user, user)
        self.assertEqual(dataset.column_names, ["a", "b", "c"])
        self.assertTrue(dataset.file.name.startswith("datasets/"))
        self.assertIsNotNone(dataset.uploaded_at)
