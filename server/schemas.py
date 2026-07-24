from marshmallow import Schema, fields, validate

from models import VALID_CATEGORIES


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)
    reps = fields.Integer()
    sets = fields.Integer()
    duration_seconds = fields.Integer()
    exercise = fields.Nested("ExerciseSchema", only=("id", "name", "category"), dump_only=True)


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    category = fields.String(required=True)
    equipment_needed = fields.Boolean(load_default=False)
    workouts = fields.Nested(
        "WorkoutSchema", many=True, only=("id", "date", "duration_minutes"), dump_only=True
    )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    notes = fields.String(required=False, allow_none=True)
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


exercise_schema = ExerciseSchema()
workout_schema = WorkoutSchema()
workout_exercise_schema = WorkoutExerciseSchema()