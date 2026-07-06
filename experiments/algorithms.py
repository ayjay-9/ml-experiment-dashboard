from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC, SVR

ALGORITHM_REGISTRY = {
    "classification": {
        "logistic_regression": {
            "estimator_class": LogisticRegression,
            "allowed_hyperparameters": {"C", "max_iter", "penalty", "solver"},
        },
        "random_forest_classifier": {
            "estimator_class": RandomForestClassifier,
            "allowed_hyperparameters": {"n_estimators", "max_depth", "min_samples_split"},
        },
        "svc": {
            "estimator_class": SVC,
            "allowed_hyperparameters": {"C", "kernel", "gamma"},
        },
    },
    "regression": {
        "linear_regression": {
            "estimator_class": LinearRegression,
            "allowed_hyperparameters": {"fit_intercept"},
        },
        "random_forest_regressor": {
            "estimator_class": RandomForestRegressor,
            "allowed_hyperparameters": {"n_estimators", "max_depth", "min_samples_split"},
        },
        "svr": {
            "estimator_class": SVR,
            "allowed_hyperparameters": {"C", "kernel", "gamma"},
        },
    },
}


def build_estimator(task_type, algorithm, hyperparameters):
    try:
        entry = ALGORITHM_REGISTRY[task_type][algorithm]
    except KeyError as exc:
        raise ValueError(
            f"Unknown algorithm '{algorithm}' for task type '{task_type}'"
        ) from exc

    allowed = entry["allowed_hyperparameters"]
    unknown_keys = set(hyperparameters) - allowed
    if unknown_keys:
        raise ValueError(
            f"Unsupported hyperparameters for {algorithm}: {sorted(unknown_keys)}"
        )

    return entry["estimator_class"](**hyperparameters)
