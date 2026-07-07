import pandas as pd
from django.utils import timezone
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split

from core.celery import app

from .algorithms import build_estimator
from .llm import generate_commentary
from .models import Experiment


@app.task
def train_experiment(experiment_id):
    experiment = Experiment.objects.get(id=experiment_id)
    experiment.status = "running"
    experiment.save(update_fields=["status"])

    try:
        df = pd.read_csv(experiment.dataset.file.path)
        X = pd.get_dummies(df.drop(columns=[experiment.target_column]))
        y = df[experiment.target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        estimator = build_estimator(
            experiment.task_type, experiment.algorithm, experiment.hyperparameters
        )
        estimator.fit(X_train, y_train)
        predictions = estimator.predict(X_test)

        if experiment.task_type == "classification":
            metrics = {
                "accuracy": accuracy_score(y_test, predictions),
                "precision": precision_score(
                    y_test, predictions, average="weighted", zero_division=0
                ),
                "recall": recall_score(
                    y_test, predictions, average="weighted", zero_division=0
                ),
                "f1": f1_score(y_test, predictions, average="weighted", zero_division=0),
                "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
            }
        else:
            metrics = {
                "rmse": root_mean_squared_error(y_test, predictions),
                "mae": mean_absolute_error(y_test, predictions),
                "r2": r2_score(y_test, predictions),
            }
        experiment.metrics = metrics

        past_experiments = list(
            Experiment.objects.filter(
                dataset=experiment.dataset, user=experiment.user, status="completed"
            )
            .exclude(id=experiment.id)
            .order_by("-created_at")[:5]
        )
        experiment.llm_commentary = generate_commentary(experiment, past_experiments)

        experiment.status = "completed"
        experiment.completed_at = timezone.now()
        experiment.save()
    except Exception as exc:
        experiment.status = "failed"
        experiment.error_message = str(exc)
        experiment.save(update_fields=["status", "error_message"])
        raise
