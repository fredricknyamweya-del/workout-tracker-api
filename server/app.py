from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    ExerciseSchema,
    WorkoutSchema,
    exercise_schema,
    workout_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)

# Lightweight schemas for list views, so GET /workouts and GET /exercises
# don't have to serialize every nested relationship.
workouts_list_schema = WorkoutSchema(many=True, exclude=("workout_exercises",))
exercises_list_schema = ExerciseSchema(many=True, exclude=("workouts",))


def error_response(message, status=400):
    errors = [message] if isinstance(message, str) else message
    return make_response(jsonify({"errors": errors}), status)


# ---------- Workout Routes ----------

@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_list_schema.dump(workouts)), 200)


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return error_response(f"Workout {id} not found.", 404)
    # Full detail view includes reps/sets/duration via workout_exercises
    return make_response(workout_schema.dump(workout), 200)


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.get_json() or {}
    try:
        validated = workout_schema.load(data)
    except ValidationError as err:
        return error_response(err.messages, 422)

    try:
        workout = Workout(
            date=validated["date"],
            duration_minutes=validated["duration_minutes"],
            notes=validated.get("notes"),
        )
        db.session.add(workout)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return error_response(str(err), 422)

    return make_response(workout_schema.dump(workout), 201)


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return error_response(f"Workout {id} not found.", 404)

    # cascade="all, delete-orphan" on the relationship removes
    # any associated WorkoutExercises automatically.
    db.session.delete(workout)
    db.session.commit()
    return make_response("", 204)


# ---------- Exercise Routes ----------

@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_list_schema.dump(exercises)), 200)


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return error_response(f"Exercise {id} not found.", 404)
    # Full detail view includes associated workouts
    return make_response(exercise_schema.dump(exercise), 200)


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json() or {}
    try:
        validated = exercise_schema.load(data)
    except ValidationError as err:
        return error_response(err.messages, 422)

    try:
        exercise = Exercise(
            name=validated["name"],
            category=validated["category"],
            equipment_needed=validated.get("equipment_needed", False),
        )
        db.session.add(exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return error_response(str(err), 422)

    return make_response(exercise_schema.dump(exercise), 201)


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return error_response(f"Exercise {id} not found.", 404)

    # cascade="all, delete-orphan" removes any associated WorkoutExercises.
    db.session.delete(exercise)
    db.session.commit()
    return make_response("", 204)


# ---------- WorkoutExercise Route ----------

@app.route("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises", methods=["POST"])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)

    if not workout:
        return error_response(f"Workout {workout_id} not found.", 404)
    if not exercise:
        return error_response(f"Exercise {exercise_id} not found.", 404)

    data = request.get_json() or {}
    try:
        validated = workout_exercise_schema.load(data, partial=True)
    except ValidationError as err:
        return error_response(err.messages, 422)

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise.id,
            reps=validated.get("reps"),
            sets=validated.get("sets"),
            duration_seconds=validated.get("duration_seconds"),
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return error_response(str(err), 422)

    return make_response(workout_exercise_schema.dump(workout_exercise), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)