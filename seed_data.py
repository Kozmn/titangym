from app import app
from models import db, Exercise

def seed_exercises():
    exercises_data = [
        # Chest (Push)
        {"name": "Barbell Bench Press", "type": "compound", "muscle_group": "chest", "mechanics": "push", "equipment": "barbell"},
        {"name": "Dumbbell Bench Press", "type": "compound", "muscle_group": "chest", "mechanics": "push", "equipment": "dumbbell"},
        {"name": "Incline Dumbbell Press", "type": "compound", "muscle_group": "chest", "mechanics": "push", "equipment": "dumbbell"},
        {"name": "Push-Up", "type": "compound", "muscle_group": "chest", "mechanics": "push", "equipment": "bodyweight"},
        {"name": "Chest Fly (Machine)", "type": "isolation", "muscle_group": "chest", "mechanics": "push", "equipment": "machine"},
        
        # Back (Pull)
        {"name": "Pull-Up", "type": "compound", "muscle_group": "back", "mechanics": "pull", "equipment": "bodyweight"},
        {"name": "Barbell Row", "type": "compound", "muscle_group": "back", "mechanics": "pull", "equipment": "barbell"},
        {"name": "Lat Pulldown", "type": "compound", "muscle_group": "back", "mechanics": "pull", "equipment": "machine"},
        {"name": "Seated Cable Row", "type": "compound", "muscle_group": "back", "mechanics": "pull", "equipment": "machine"},
        {"name": "Dumbbell Row", "type": "compound", "muscle_group": "back", "mechanics": "pull", "equipment": "dumbbell"},

        # Legs - Quad (Squat/Lunge)
        {"name": "Barbell Squat", "type": "compound", "muscle_group": "legs_quad", "mechanics": "squat", "equipment": "barbell"},
        {"name": "Goblet Squat", "type": "compound", "muscle_group": "legs_quad", "mechanics": "squat", "equipment": "dumbbell"},
        {"name": "Leg Press", "type": "compound", "muscle_group": "legs_quad", "mechanics": "squat", "equipment": "machine"},
        {"name": "Walking Lunge", "type": "compound", "muscle_group": "legs_quad", "mechanics": "lunge", "equipment": "dumbbell"},
        {"name": "Bulgarian Split Squat", "type": "compound", "muscle_group": "legs_quad", "mechanics": "lunge", "equipment": "dumbbell"},
        {"name": "Leg Extension", "type": "isolation", "muscle_group": "legs_quad", "mechanics": "push", "equipment": "machine"},

        # Legs - Ham (Hinge)
        {"name": "Deadlift", "type": "compound", "muscle_group": "legs_ham", "mechanics": "hinge", "equipment": "barbell"},
        {"name": "Romanian Deadlift", "type": "compound", "muscle_group": "legs_ham", "mechanics": "hinge", "equipment": "barbell"},
        {"name": "Leg Curl", "type": "isolation", "muscle_group": "legs_ham", "mechanics": "pull", "equipment": "machine"},
        
        # Shoulders (Push)
        {"name": "Overhead Press", "type": "compound", "muscle_group": "shoulders", "mechanics": "push", "equipment": "barbell"},
        {"name": "Dumbbell Shoulder Press", "type": "compound", "muscle_group": "shoulders", "mechanics": "push", "equipment": "dumbbell"},
        {"name": "Lateral Raise", "type": "isolation", "muscle_group": "shoulders", "mechanics": "push", "equipment": "dumbbell"},
        {"name": "Face Pull", "type": "isolation", "muscle_group": "shoulders", "mechanics": "pull", "equipment": "machine"},

        # Arms
        {"name": "Barbell Curl", "type": "isolation", "muscle_group": "arms", "mechanics": "pull", "equipment": "barbell"},
        {"name": "Dumbbell Curl", "type": "isolation", "muscle_group": "arms", "mechanics": "pull", "equipment": "dumbbell"},
        {"name": "Tricep Pushdown", "type": "isolation", "muscle_group": "arms", "mechanics": "push", "equipment": "machine"},
        {"name": "Skullcrusher", "type": "isolation", "muscle_group": "arms", "mechanics": "push", "equipment": "barbell"},

        # Core
        {"name": "Plank", "type": "isolation", "muscle_group": "core", "mechanics": "static", "equipment": "bodyweight"},
        {"name": "Hanging Leg Raise", "type": "compound", "muscle_group": "core", "mechanics": "pull", "equipment": "bodyweight"},
        {"name": "Cable Woodchop", "type": "compound", "muscle_group": "core", "mechanics": "pull", "equipment": "machine"},
        
        # Carry
        {"name": "Farmer's Walk", "type": "compound", "muscle_group": "core", "mechanics": "carry", "equipment": "dumbbell"}
    ]

    with app.app_context():
        # Check if exercises already exist to avoid duplicates
        if Exercise.query.first() is None:
            for data in exercises_data:
                ex = Exercise(**data)
                db.session.add(ex)
            db.session.commit()
            print("Exercises seeded successfully!")
        else:
            print("Exercises already exist.")

if __name__ == "__main__":
    seed_exercises()
