from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from .models import Dataset

User = get_user_model()


class DatasetAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.client.force_login(self.user)

    def test_upload_dataset_parses_columns(self):
        upload = SimpleUploadedFile(
            "iris.csv",
            b"sepal_length,sepal_width,species\n5.1,3.5,setosa\n",
            content_type="text/csv",
        )

        response = self.client.post("/api/datasets/", {"file": upload}, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["column_names"], ["sepal_length", "sepal_width", "species"]
        )
        dataset = Dataset.objects.get(id=response.data["id"])
        self.assertEqual(dataset.user, self.user)

    def test_list_only_returns_own_datasets(self):
        other_user = User.objects.create_user(username="bob", password="testpass123")
        Dataset.objects.create(
            user=other_user,
            file=SimpleUploadedFile("other.csv", b"a,b\n1,2\n"),
            column_names=["a", "b"],
        )

        response = self.client.get("/api/datasets/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_anonymous_user_cannot_access(self):
        self.client.logout()

        response = self.client.get("/api/datasets/")

        self.assertEqual(response.status_code, 403)
