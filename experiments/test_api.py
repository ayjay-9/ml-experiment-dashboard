from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from .models import Dataset, Experiment

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


class ExperimentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.client.force_login(self.user)
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=SimpleUploadedFile("iris.csv", b"a,b,label\n1,2,0\n"),
            column_names=["a", "b", "label"],
        )

    @patch("experiments.views.train_experiment.delay")
    def test_create_experiment_queues_training_task(self, mock_delay):
        payload = {
            "dataset": self.dataset.id,
            "target_column": "label",
            "task_type": "classification",
            "algorithm": "random_forest_classifier",
            "hyperparameters": {"n_estimators": 10},
        }

        response = self.client.post("/api/experiments/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
        experiment = Experiment.objects.get(id=response.data["id"])
        mock_delay.assert_called_once_with(experiment.id)

    def test_cannot_create_experiment_on_another_users_dataset(self):
        other_user = User.objects.create_user(username="bob", password="testpass123")
        other_dataset = Dataset.objects.create(
            user=other_user,
            file=SimpleUploadedFile("other.csv", b"a,b\n1,2\n"),
            column_names=["a", "b"],
        )

        payload = {
            "dataset": other_dataset.id,
            "target_column": "a",
            "task_type": "classification",
            "algorithm": "random_forest_classifier",
            "hyperparameters": {},
        }

        response = self.client.post("/api/experiments/", payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_invalid_algorithm_for_task_type_rejected(self):
        payload = {
            "dataset": self.dataset.id,
            "target_column": "label",
            "task_type": "classification",
            "algorithm": "linear_regression",
            "hyperparameters": {},
        }

        response = self.client.post("/api/experiments/", payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_target_column_not_in_dataset_rejected(self):
        payload = {
            "dataset": self.dataset.id,
            "target_column": "not_a_real_column",
            "task_type": "classification",
            "algorithm": "random_forest_classifier",
            "hyperparameters": {},
        }

        response = self.client.post("/api/experiments/", payload, format="json")

        self.assertEqual(response.status_code, 400)
