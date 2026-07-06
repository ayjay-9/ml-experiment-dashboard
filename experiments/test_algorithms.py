import pytest

from experiments.algorithms import build_estimator


def test_build_known_classification_estimator():
    estimator = build_estimator(
        "classification", "random_forest_classifier", {"n_estimators": 10}
    )
    assert estimator.n_estimators == 10


def test_build_known_regression_estimator():
    estimator = build_estimator("regression", "linear_regression", {})
    assert estimator.__class__.__name__ == "LinearRegression"


def test_unknown_algorithm_raises():
    with pytest.raises(ValueError):
        build_estimator("classification", "not_a_real_algorithm", {})


def test_unknown_hyperparameter_raises():
    with pytest.raises(ValueError):
        build_estimator("classification", "random_forest_classifier", {"not_a_real_param": 1})
