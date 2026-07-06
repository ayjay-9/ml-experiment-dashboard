from core.celery import app


@app.task
def train_experiment(experiment_id):
    raise NotImplementedError("Implemented in Task 5")
