"""
Schemas for serialization (Python objects -> JSON) and
deserialization (JSON -> validated Python data).
"""

from marshmallow import Schema, fields, validate

from models import VALID_CATEGORIES


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)

    reps = fields.Integer(validate=validate.Range(min=1, error="reps must be at least 1."))
    sets = fields.Integer(validate=validate.Range(min=1, error="sets must be at least 1."))
    duration_seconds = fields.Integer(
        validate=validate.Range(min=1, error="duration_seconds must be at least 1.")
    )

    exercise = fields.Nested("ExerciseSchema", only=("id", "name", "category"), dump_only=True)


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, error="name cannot be empty.")
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(VALID_CATEGORIES, error="category must be one of {choices}.")
    )
    equipment_needed = fields.Boolean(load_default=False)

    workouts = fields.Nested(
        "WorkoutSchema", many=True, only=("id", "date", "duration_minutes"), dump_only=True
    )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="duration_minutes must be a positive number.")
    )
    notes = fields.String(required=False, allow_none=True)

    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)