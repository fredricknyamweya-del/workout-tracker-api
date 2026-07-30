from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Categories an Exercise can belong to.
# Used by a model validation below to keep the data consistent.
VALID_CATEGORIES = ["cardio", "strength", "flexibility", "balance"]


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    # An Exercise has many WorkoutExercises, and many Workouts through them.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout", secondary="workout_exercises", back_populates="exercises", viewonly=True
    )

    # --- Model Validations ---
    @validates("name")
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Exercise name cannot be empty.")
        return name.strip()

    @validates("category")
    def validate_category(self, key, category):
        if category not in VALID_CATEGORIES:
            raise ValueError(
                f"category must be one of {VALID_CATEGORIES}, got '{category}'."
            )
        return category

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name} ({self.category})>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    __table_args__ = (
        # --- Table Constraints ---
        CheckConstraint("duration_minutes > 0", name="check_duration_positive"),
    )

    # A Workout has many WorkoutExercises, and many Exercises through them.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", back_populates="workouts", viewonly=True
    )

    # --- Model Validations ---
    @validates("duration_minutes")
    def validate_duration(self, key, duration_minutes):
        if not isinstance(duration_minutes, int) or duration_minutes <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return duration_minutes

    def __repr__(self):
        return f"<Workout {self.id}: {self.date} ({self.duration_minutes} min)>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    __table_args__ = (
        # --- Table Constraints ---
        CheckConstraint("reps IS NULL OR reps > 0", name="check_reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="check_sets_positive"),
    )

    # WorkoutExercise belongs to a Workout and belongs to an Exercise.
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # --- Model Validations ---
    @validates("reps", "sets", "duration_seconds")
    def validate_positive_numbers(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f"{key} must be a positive number when provided.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise {self.id}: workout={self.workout_id} exercise={self.exercise_id}>"