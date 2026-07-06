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
