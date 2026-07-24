# WorkoutExerciseSchema
from dataclasses import fields
from wtforms import validators as validate

from server.models import VALID_CATEGORIES

#WorkoutExerciseSchema
reps = fields.Integer(validate=validate.Range(min=1, error="reps must be at least 1."))
sets = fields.Integer(validate=validate.Range(min=1, error="sets must be at least 1."))
duration_seconds = fields.Integer(
    validate=validate.Range(min=1, error="duration_seconds must be at least 1.")
)

#ExerciseSchema
name = fields.String(required=True, validate=validate.Length(min=1, error="name cannot be empty."))
category = fields.String(
        required=True,
        validate=validate.OneOf(VALID_CATEGORIES, error="category must be one of {choices}.")
    )

# WorkoutOutSchema
duration_minutes = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="duration_minutes must be a positive number.")
    )

