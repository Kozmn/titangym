from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Physical stats
    weight = db.Column(db.Float) # kg
    height = db.Column(db.Float) # cm
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10)) # male, female
    
    # Training Preferences
    goal = db.Column(db.String(20)) # strength, hypertrophy, endurance, weight_loss
    experience_level = db.Column(db.String(20)) # beginner, intermediate
    days_available = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    plans = db.relationship('WorkoutPlan', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20)) # compound, isolation
    muscle_group = db.Column(db.String(20)) # chest, back, legs_quad, legs_ham, shoulders, core, arms
    mechanics = db.Column(db.String(20)) # push, pull, squat, hinge, lunge, carry
    equipment = db.Column(db.String(20)) # barbell, dumbbell, machine, bodyweight

class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50)) # e.g., "FBW A", "Upper Body"
    schedule_day = db.Column(db.Integer) # 1-7 (1=Monday, etc.)
    
    exercises = db.relationship('WorkoutExercise', backref='plan', lazy=True, order_by='WorkoutExercise.order')

class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    
    sets = db.Column(db.Integer)
    reps_range = db.Column(db.String(10)) # e.g., "8-12"
    rest_time = db.Column(db.Integer) # seconds
    order = db.Column(db.Integer)

    exercise = db.relationship('Exercise')

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_exercise_id = db.Column(db.Integer, db.ForeignKey('workout_exercise.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    weight = db.Column(db.Float)
    reps_performed = db.Column(db.String(50)) # e.g., "10,10,10"
    
    workout_exercise = db.relationship('WorkoutExercise')
    user = db.relationship('User')

    @property
    def sets_performed(self):
        if self.reps_performed:
            return [int(x) for x in self.reps_performed.split(',')]
        return []

class DietLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)

    user = db.relationship('User')
