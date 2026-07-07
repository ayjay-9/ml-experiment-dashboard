# ML Experiment Dashboard

**CS50's Web Programming with Python and JavaScript — Final Project**

A web app where a logged-in user uploads a tabular dataset (CSV), configures
a machine learning training run against it (target column, task type,
algorithm, hyperparameters), watches it train in the background, and reviews
the resulting metrics — with past runs on the same dataset kept around for
comparison.

## Distinctiveness and Complexity

This project is a machine learning experiment tracker, not a social network,
e-commerce site, or blogging platform — none of the concerns CS50's other
project specs (or the earlier projects in this course) center on apply here:
there is no feed of posts, no cart/checkout flow, no comment threads. Instead
the core problem is orchestrating an asynchronous, potentially slow
computation (training an ML model) safely behind a web request/response
cycle, and giving the user a live view into work that is happening
somewhere else.

That drives real complexity beyond CRUD:

- **A background job pipeline, not just a database write.** Submitting a
  training run doesn't do the work inline in the request — it creates an
  `Experiment` row, hands it to a Celery worker process over a Redis broker,
  and returns immediately. The browser polls for the result. This means the
  app has to model and correctly transition through a state machine
  (`pending` → `running` → `completed`/`failed`), including a real failure
  path: if the CSV, target column, or algorithm choice is bad in a way
  validation didn't catch (e.g. a training-time error from scikit-learn),
  the run is marked `failed` with a captured error message rather than
  hanging forever or crashing a worker silently.
- **Data science, not just data storage.** Uploading a CSV means parsing its
  header row server-side to drive the UI (so the user picks a target column
  from real column names, not free text), then actually training one of six
  scikit-learn estimators (three classification, three regression) against
  it, with categorical feature columns automatically one-hot encoded so the
  app can handle realistic, non-numeric real-world data rather than only
  toy numeric datasets. Metrics are computed per task type (accuracy /
  precision / recall / F1 / confusion matrix for classification; RMSE / MAE
  / R² for regression) rather than being a fixed, generic shape.
- **A real security boundary, not just a login wall.** Every dataset and
  experiment is scoped to the user who owns it at every layer — list views,
  detail/poll views, and even the write path (a user cannot create an
  experiment against another user's dataset; this is enforced by
  restricting the serializer's foreign-key queryset, not just filtering the
  read side, and is covered by a dedicated test).
- **A deliberately decoupled architecture.** Django serves as a pure
  session-authenticated backend + JSON API (Django REST Framework); the
  entire dashboard UI is a single-page app written in plain JavaScript with
  **no build step, no framework, no bundler** — ES modules loaded directly
  by the browser, talking to the API via `fetch`. This was a considered
  trade-off (documented in `docs/superpowers/specs/`), not an oversight: it
  keeps the project within "vanilla JS is enough," while still requiring
  real frontend engineering — CSRF-safe `fetch` wrapping, async polling with
  correct interval teardown, and DOM state management across a multi-step
  form — without hiding that complexity behind a framework.
- **An extensibility seam for an LLM feature.** The design already carves
  out where an LLM-generated, plain-language analysis of results (including
  comparison against a user's past runs) will plug in
  (`experiments/llm.py`), deliberately stubbed to a no-op today so the rest
  of the app doesn't block on choosing a provider — a real architectural
  decision, not a TODO left behind by accident.

## What's Contained in Each File

```
ml-experiment-dashboard/
├── manage.py                     Django's command-line entry point
├── requirements.txt               Python dependencies (Django, DRF, Celery,
│                                  scikit-learn, pandas, pytest, ...)
├── Dockerfile                     Multi-stage build: base → development → production
├── docker-compose.yml             Local dev stack: postgres, redis, web,
│                                  celery_worker, celery_beat
├── pytest.ini                     Points pytest-django at core.settings.development
├── .env / .env.example            Environment variables (DB creds, secret key,
│                                  Redis URL, LLM API key — .env is gitignored)
│
├── core/                          Django project package (config, not a "real" app)
│   ├── settings/
│   │   ├── base.py                Shared settings: installed apps, DRF config,
│   │   │                          Celery config, database (from env vars),
│   │   │                          static/media/templates paths
│   │   ├── development.py         DEBUG=True, permissive CORS/hosts
│   │   └── production.py          DEBUG=False, Whitenoise static file serving
│   ├── celery.py                  Creates the Celery app instance (`app = Celery("core")`)
│   ├── urls.py                    Top-level routing: admin, auth, register,
│   │                              /api/ (→ experiments app), dashboard
│   ├── views.py                   `dashboard` (the SPA shell) and `register` views
│   └── tests.py                   Tests for dashboard access control, login/logout,
│                                  registration, and the SPA shell template
│
├── experiments/                   The one Django app: all ML-tracking domain logic
│   ├── models.py                  `Dataset` (uploaded file + parsed column names)
│   │                              and `Experiment` (a training run's config,
│   │                              status, metrics, and results)
│   ├── algorithms.py               Registry mapping (task_type, algorithm) →
│   │                              scikit-learn estimator class + allowed
│   │                              hyperparameter keys; `build_estimator()`
│   ├── llm.py                     `generate_commentary()` — the LLM extension
│   │                              point, currently a no-op stub
│   ├── tasks.py                   `train_experiment` — the Celery task that
│   │                              loads the CSV, one-hot encodes categorical
│   │                              features, trains the model, computes
│   │                              metrics, and records success/failure
│   ├── serializers.py             DRF serializers: CSV upload + header
│   │                              parsing (`DatasetSerializer`), experiment
│   │                              creation + validation (`ExperimentSerializer`)
│   ├── views.py                   DRF viewsets: `DatasetViewSet`,
│   │                              `ExperimentViewSet` (both scoped to the
│   │                              requesting user; creating an experiment
│   │                              queues the Celery task)
│   ├── urls.py                    DRF router: `/api/datasets/`, `/api/experiments/`
│   ├── admin.py                   Django admin registration for both models
│   ├── migrations/                Auto-generated schema migrations
│   └── test_*.py, tests.py        Model tests, API tests, algorithm-registry
│                                  tests, LLM-stub test, and Celery task tests
│                                  (classification, regression, categorical
│                                  features, and failure-path coverage)
│
├── templates/
│   ├── index.html                 The SPA shell: three sections (upload,
│   │                              configure, results) plus the JS/CSS includes
│   └── registration/
│       ├── login.html             Login form (Django's built-in LoginView)
│       └── register.html          Registration form (custom view using
│                                  Django's `UserCreationForm`)
│
├── static/
│   ├── css/style.css               Minimal styling for the dashboard shell
│   └── js/
│       ├── api.js                  `apiFetch()` — CSRF-aware fetch wrapper
│       │                          shared by every API call
│       ├── datasets.js             Dataset upload + list rendering
│       ├── experiments.js          Experiment creation, algorithm-option
│       │                          population, and results polling
│       └── main.js                 Wires all of the above to the DOM: form
│                                  submit handlers, section show/hide, state
│
├── media/                         Runtime storage for uploaded datasets
│                                  (gitignored; created by Docker volume)
│
└── docs/superpowers/               Design spec and the three implementation
    ├── specs/                      plans this project was actually built from
    └── plans/                      (kept for reference — not required reading
                                     to use the app, but documents *why* the
                                     architecture looks the way it does)
```

## How to Run the Application

This project runs entirely through Docker Compose — you do not need a local
Python installation, virtualenv, Postgres, or Redis.

**Prerequisites:** Docker Desktop installed and running.

1. **Clone the repo and enter the project directory.**

2. **Create your `.env` file** from the template and fill in real values:

   ```bash
   cp .env.example .env
   ```

   At minimum, set:
   - `DJANGO_SECRET_KEY` — any long random string
   - `DEBUG` — `True` for local development
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD` — any values; Postgres will
     initialize itself with these on first run
   - `DB_HOST=postgres`, `REDIS_URL=redis://redis:6379/0` — these must match
     the service names in `docker-compose.yml`
   - `LLM_API_KEY` — can be left blank; the app degrades gracefully with no
     LLM commentary if it's unset

3. **Build and start the stack:**

   ```bash
   docker compose up -d --build
   ```

   This starts five containers: `postgres`, `redis`, `web` (the Django dev
   server), `celery_worker` (runs training jobs), and `celery_beat`
   (scheduled task support, unused today but wired for future features).

4. **Apply database migrations:**

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Create an account** by visiting `http://localhost:8000/register/`, or
   create a Django superuser to use `/admin/`:

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Open the dashboard:** `http://localhost:8000/`

7. **Run the test suite** (28+ tests covering models, the API, the training
   pipeline, and auth):

   ```bash
   docker compose exec web pytest -v
   ```

**Important operational note:** `celery_worker` and `celery_beat` do **not**
hot-reload. If you edit `experiments/tasks.py` (or add a new Celery task),
restart them to pick up the change:

```bash
docker compose restart celery_worker celery_beat
```

The Django dev server (`web`) does auto-reload on file changes, as usual.

## Using the App

1. **Register / log in.**
2. **Upload a dataset** — pick any CSV file. The server parses its header
   row and returns the real column names.
3. **Configure a run** — pick the target column (what you're predicting),
   the task type (classification or regression), and an algorithm:
   - Classification: Logistic Regression, Random Forest, SVM (SVC)
   - Regression: Linear Regression, Random Forest, SVM (SVR)
4. **Train** — the run is queued to a background worker immediately; the
   page polls every 3 seconds until it's done.
5. **View results** — once complete, you'll see the relevant metrics
   (accuracy/precision/recall/F1/confusion matrix, or RMSE/MAE/R²) and an
   LLM commentary field (currently empty — see Limitations below).

Feature columns that aren't numeric (e.g. a text category like a brand or
model name) are automatically one-hot encoded before training, so you can
upload realistic datasets, not just pre-cleaned numeric ones.

## Architecture at a Glance

- **Backend:** Django 4.2 + Django REST Framework, PostgreSQL, session-based
  auth (no tokens/JWT — the frontend is same-origin, so cookies work).
- **Background jobs:** Celery 5.4 with Redis as the broker; `django-celery-results`
  stores task results, `django-celery-beat` is installed for future scheduled
  tasks.
- **ML:** scikit-learn + pandas, wrapped behind a small algorithm registry so
  new algorithms can be added in one file (`experiments/algorithms.py`)
  without touching the training task itself.
- **Frontend:** one server-rendered shell page + plain ES-module JavaScript,
  no build tooling. All dynamic behavior (upload, form population, polling,
  rendering) happens via `fetch()` calls to the DRF API.
- **Testing:** pytest + pytest-django, run inside the same Docker image the
  app runs in, so there's no "works on my machine" drift between test and
  runtime environments.

## Known Limitations / Future Work

- **LLM commentary is not yet wired to a real provider.** `experiments/llm.py`
  always returns an empty string. The design intentionally isolated this
  behind one function so plugging in a provider (Anthropic, OpenAI, etc.)
  later is a one-file change, but it hasn't been done yet.
- **No client-side validation/error display on failed uploads or runs.** If
  an upload or training-run request fails, the UI currently doesn't surface
  a visible error message to the user (this is tracked as a known follow-up,
  not a design goal).
- **No cancellation of an in-flight results poll** if a second dataset/run
  is started before the first finishes — a narrow edge case for this
  single-session dashboard.
- **Train/test split ratio is fixed** at 80/20 and isn't user-configurable.
- **No downloadable artifacts** (trained model files, exported plots) — only
  numeric metrics are shown.
