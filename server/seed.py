#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Seeding exercises...")
    push_up = Exercise(name="Push Up", category="strength", equipment_needed=False)
    squat = Exercise(name="Squat", category="strength", equipment_needed=False)
    running = Exercise(name="Running", category="cardio", equipment_needed=False)
    deadlift = Exercise(name="Deadlift", category="strength", equipment_needed=True)
    yoga_stretch = Exercise(name="Yoga Stretch", category="flexibility", equipment_needed=False)
    db.session.add_all([push_up, squat, running, deadlift, yoga_stretch])
    db.session.commit()

    print("Seeding workouts...")
    monday = Workout(date=date(2026, 7, 20), duration_minutes=45, notes="Strength session.")
    wednesday = Workout(date=date(2026, 7, 22), duration_minutes=30, notes="Cardio + stretch.")
    db.session.add_all([monday, wednesday])
    db.session.commit()

    print("Seeding workout_exercises...")
    db.session.add_all([
        WorkoutExercise(workout=monday, exercise=push_up, reps=15, sets=3),
        WorkoutExercise(workout=monday, exercise=squat, reps=12, sets=4),
        WorkoutExercise(workout=monday, exercise=deadlift, reps=8, sets=3),
        WorkoutExercise(workout=wednesday, exercise=running, duration_seconds=1200),
        WorkoutExercise(workout=wednesday, exercise=yoga_stretch, duration_seconds=600),
    ])
    db.session.commit()
    print("Done seeding!")