# Workout Tracker API

## Project Description

A Flask + SQLAlchemy backend API for a workout tracking application used by
personal trainers. The API lets a trainer create, view, and delete
**Workouts** and **Exercises**, and attach exercises to a workout with
specific reps, sets, and/or duration through a `WorkoutExercise` join table.
Data is validated at the model, table, and schema (Marshmallow) level to
keep the data clean and consistent.

### Entities

- **Exercise** — `id`, `name`, `category`, `equipment_needed`
- **Workout** — `id`, `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table) — `id`, `workout_id`, `exercise_id`,
  `reps`, `sets`, `duration_seconds`

### Relationships

- A `WorkoutExercise` belongs to a `Workout` and belongs to an `Exercise`.
- A `Workout` has many `WorkoutExercises`, and many `Exercises` through them.
- An `Exercise` has many `WorkoutExercises`, and many `Workouts` through them.

## Installation Instructions

> **Python version:** This project pins Flask 2.2.2 / Werkzeug 2.2.2, which
> are incompatible with Python 3.12+. Use Python 3.11 (or 3.9–3.11) via
> `pyenv` before installing dependencies, or `flask run` / `flask db migrate`
> will fail with errors like `AttributeError: module 'ast' has no attribute
> 'Str'`.

1. Clone the repo and move into the project folder:
   ```bash
   git clone <your-repo-url>
   cd workout-tracker-api
   ```
2. Pin Python 3.11 for this project (skip if already set up):
   ```bash
   pyenv install 3.11.9   # only needed once per machine
   pyenv local 3.11.9
   ```
3. Install dependencies with Pipenv:
   ```bash
   pipenv install
   pipenv shell
   python --version   # confirm this prints Python 3.11.x
   ```
4. Move into the `server/` directory (all commands below run from here):
   ```bash
   cd server
   ```
5. Set up the database with Flask-Migrate:
   ```bash
   export FLASK_APP=app.py
   flask db init      # only needed the first time
   flask db migrate -m "initial migration"
   flask db upgrade head
   ```
6. Seed the database with example data:
   ```bash
   python seed.py
   ```

## Run Instructions

From the `server/` directory:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5555`.

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET    | `/workouts` | List all workouts. |
| GET    | `/workouts/<id>` | Show a single workout, including its exercises with reps/sets/duration. |
| POST   | `/workouts` | Create a workout. Body: `date`, `duration_minutes`, `notes` (optional). |
| DELETE | `/workouts/<id>` | Delete a workout and its associated `WorkoutExercises`. |
| GET    | `/exercises` | List all exercises. |
| GET    | `/exercises/<id>` | Show a single exercise and the workouts it's used in. |
| POST   | `/exercises` | Create an exercise. Body: `name`, `category`, `equipment_needed` (optional). |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated `WorkoutExercises`. |
| POST   | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout. Body: `reps`, `sets`, `duration_seconds` (any combination). |

### Validations

- **Table constraints:** `duration_minutes` on `Workout` must be greater
  than 0; `reps` and `sets` on `WorkoutExercise` must be greater than 0 when
  provided.
- **Model validations:** `Exercise.name` can't be blank, `Exercise.category`
  must be one of `cardio`, `strength`, `flexibility`, `balance`;
  `Workout.duration_minutes` must be a positive integer;
  `WorkoutExercise.reps`/`sets`/`duration_seconds` must be positive when
  provided.
- **Schema validations:** Marshmallow mirrors the above (required fields,
  `OneOf` for category, `Range(min=1)` for reps/sets/duration_seconds) and
  returns a `422` response with clear error messages when data is invalid.

### Serialization notes

Schemas are written with plain `marshmallow.Schema` (not
`flask_marshmallow`'s `SQLAlchemyAutoSchema`), so fields and relationships
are declared explicitly in `schemas.py`. Routes call `.dump()` (not
`.dumps()`) since it returns a Python dict that `jsonify()` can serialize —
`.dumps()` would return an already-encoded JSON string. List endpoints use
schema instances built with `many=True` and `exclude=(...)` so a full list
of workouts or exercises doesn't also serialize every nested relationship.

## Folder Structure

```
workout-tracker-api/
├── .gitignore
├── Pipfile
├── README.md
└── server/
    ├── app.py                     # Flask app instance + all routes
    ├── models.py                  # Exercise, Workout, WorkoutExercise models
    ├── schemas.py                 # Marshmallow schemas + validations
    ├── seed.py                    # Example data script
    └── migrations/
        ├── README
        ├── alembic.ini
        ├── env.py
        ├── script.py.mako
        └── versions/
            └── <hash>_initial_migration.py
```

`app.db` is not tracked in git (see `.gitignore`) — it's generated locally
by running `flask db upgrade head` followed by `python seed.py`.