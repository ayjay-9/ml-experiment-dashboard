from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Dataset, Experiment
from .tasks import train_experiment

User = get_user_model()


def make_classification_csv():
    rows = ["a,b,label"]
    for i in range(30):
        rows.append(f"{i},{i * 2},{i % 2}")
    return "\n".join(rows).encode("utf-8")


class TrainExperimentClassificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=SimpleUploadedFile("data.csv", make_classification_csv()),
            column_names=["a", "b", "label"],
        )

    def test_classification_run_completes_with_metrics(self):
        experiment = Experiment.objects.create(
            dataset=self.dataset,
            user=self.user,
            target_column="label",
            task_type="classification",
            algorithm="random_forest_classifier",
            hyperparameters={"n_estimators": 10},
        )

        train_experiment(experiment.id)

        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "completed")
        self.assertIn("accuracy", experiment.metrics)
        self.assertIn("confusion_matrix", experiment.metrics)
        self.assertIsNotNone(experiment.completed_at)


def make_regression_csv():
    rows = ["a,b,target"]
    for i in range(30):
        rows.append(f"{i},{i * 2},{i * 3.0}")
    return "\n".join(rows).encode("utf-8")


class TrainExperimentRegressionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=SimpleUploadedFile("data.csv", make_regression_csv()),
            column_names=["a", "b", "target"],
        )

    def test_regression_run_completes_with_metrics(self):
        experiment = Experiment.objects.create(
            dataset=self.dataset,
            user=self.user,
            target_column="target",
            task_type="regression",
            algorithm="linear_regression",
            hyperparameters={},
        )

        train_experiment(experiment.id)

        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "completed")
        self.assertIn("rmse", experiment.metrics)
        self.assertIn("mae", experiment.metrics)
        self.assertIn("r2", experiment.metrics)


def make_categorical_feature_csv():
    brands = ["HP", "Dell", "Lenovo"]
    rows = ["brand,ram_gb,label"]
    for i in range(30):
        rows.append(f"{brands[i % 3]},{8 + (i % 3) * 8},{i % 2}")
    return "\n".join(rows).encode("utf-8")


class TrainExperimentCategoricalFeaturesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=SimpleUploadedFile("data.csv", make_categorical_feature_csv()),
            column_names=["brand", "ram_gb", "label"],
        )

    def test_non_numeric_feature_column_is_encoded_not_rejected(self):
        experiment = Experiment.objects.create(
            dataset=self.dataset,
            user=self.user,
            target_column="label",
            task_type="classification",
            algorithm="random_forest_classifier",
            hyperparameters={"n_estimators": 10},
        )

        train_experiment(experiment.id)

        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "completed")
        self.assertIn("accuracy", experiment.metrics)


class TrainExperimentFailureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")
        self.dataset = Dataset.objects.create(
            user=self.user,
            file=SimpleUploadedFile("data.csv", make_classification_csv()),
            column_names=["a", "b", "label"],
        )

    def test_bad_target_column_marks_experiment_failed(self):
        experiment = Experiment.objects.create(
            dataset=self.dataset,
            user=self.user,
            target_column="does_not_exist",
            task_type="classification",
            algorithm="random_forest_classifier",
            hyperparameters={},
        )

        with self.assertRaises(KeyError):
            train_experiment(experiment.id)

        experiment.refresh_from_db()
        self.assertEqual(experiment.status, "failed")
        self.assertTrue(experiment.error_message)
