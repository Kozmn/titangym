from models import db, Exercise, WorkoutPlan, WorkoutExercise
import random

def get_volume_settings(goal):
    if goal == 'strength':
        return {'sets': 5, 'reps': '3-5', 'rest': 180}
    elif goal == 'hypertrophy':
        return {'sets': 3, 'reps': '8-12', 'rest': 90}
    else: # endurance / weight_loss
        return {'sets': 3, 'reps': '15-20', 'rest': 60}

def select_exercise(muscle_group=None, mechanics=None, type=None, exclude_ids=[], logic_type="any"):
    query = Exercise.query
    if muscle_group:
        query = query.filter_by(muscle_group=muscle_group)
    if mechanics:
        query = query.filter_by(mechanics=mechanics)
    if type:
        query = query.filter_by(type=type)
    
    if exclude_ids:
        query = query.filter(Exercise.id.notin_(exclude_ids))
        
    candidates = query.all()
    if not candidates:
        return None
        
    return random.choice(candidates)

def create_fbw_session(user, name, day_num):
    plan = WorkoutPlan(user_id=user.id, name=name, schedule_day=day_num)
    db.session.add(plan)
    db.session.flush() # get ID
    
    settings = get_volume_settings(user.goal)
    selected_ids = []
    
    exercises_to_add = []
    
    # 1. Squat OR Lunge (Legs Quad) - Compound
    ex1 = select_exercise(muscle_group='legs_quad', type='compound', exclude_ids=selected_ids)
    if ex1: 
        exercises_to_add.append(ex1)
        selected_ids.append(ex1.id)
        
    # 2. Hinge (Legs Ham) - Compound
    ex2 = select_exercise(mechanics='hinge', type='compound', exclude_ids=selected_ids)
    if ex2:
        exercises_to_add.append(ex2)
        selected_ids.append(ex2.id)
        
    # 3. Push (Chest/Shoulders) - Compound
    mech = 'push'
    ex3 = select_exercise(mechanics=mech, type='compound', exclude_ids=selected_ids)
    if ex3:
        exercises_to_add.append(ex3)
        selected_ids.append(ex3.id)
    
    # 4. Pull (Back) - Compound
    ex4 = select_exercise(mechanics='pull', type='compound', exclude_ids=selected_ids)
    if ex4:
        exercises_to_add.append(ex4)
        selected_ids.append(ex4.id)
        
    # 5. Core
    ex5 = select_exercise(muscle_group='core', exclude_ids=selected_ids)
    if ex5:
        exercises_to_add.append(ex5)
        selected_ids.append(ex5.id)

    # 6. Extra Accessory (Arms or another isolation)
    ex6 = select_exercise(muscle_group='arms', exclude_ids=selected_ids)
    if not ex6:
         ex6 = select_exercise(type='isolation', exclude_ids=selected_ids)
    if ex6:
        exercises_to_add.append(ex6)
        selected_ids.append(ex6.id)

    # Add to DB
    for idx, ex in enumerate(exercises_to_add):
        we = WorkoutExercise(
            plan_id=plan.id,
            exercise_id=ex.id,
            sets=settings['sets'],
            reps_range=settings['reps'],
            rest_time=settings['rest'],
            order=idx+1
        )
        db.session.add(we)
        
    return plan

def create_upper_session(user, name, day_num):
    plan = WorkoutPlan(user_id=user.id, name=name, schedule_day=day_num)
    db.session.add(plan)
    db.session.flush()
    
    settings = get_volume_settings(user.goal)
    selected_ids = []
    exercises_to_add = []

    # 1. Horizontal Push (Compound)
    ex1 = select_exercise(muscle_group='chest', mechanics='push', type='compound', exclude_ids=selected_ids)
    if ex1: exercises_to_add.append(ex1); selected_ids.append(ex1.id)

    # 2. Horizontal Pull (Compound)
    ex2 = select_exercise(muscle_group='back', mechanics='pull', type='compound', exclude_ids=selected_ids)
    if ex2: exercises_to_add.append(ex2); selected_ids.append(ex2.id)
    
    # 3. Vertical Push (Compound)
    ex3 = select_exercise(muscle_group='shoulders', mechanics='push', type='compound', exclude_ids=selected_ids)
    if ex3: exercises_to_add.append(ex3); selected_ids.append(ex3.id)

    # 4. Vertical Pull (Compound)
    ex4 = select_exercise(muscle_group='back', mechanics='pull', exclude_ids=selected_ids)
    if ex4: exercises_to_add.append(ex4); selected_ids.append(ex4.id)
    
    # 5. Isolation Chest or Shoulder (Fly or Lat Raise)
    ex5 = select_exercise(mechanics='push', type='isolation', exclude_ids=selected_ids)
    if ex5: exercises_to_add.append(ex5); selected_ids.append(ex5.id)

    # 6. Arms (Bicep or Tricep)
    ex6 = select_exercise(muscle_group='arms', exclude_ids=selected_ids)
    if ex6: exercises_to_add.append(ex6); selected_ids.append(ex6.id)
    
    # Add to DB
    for idx, ex in enumerate(exercises_to_add):
        we = WorkoutExercise(
            plan_id=plan.id,
            exercise_id=ex.id,
            sets=settings['sets'],
            reps_range=settings['reps'],
            rest_time=settings['rest'],
            order=idx+1
        )
        db.session.add(we)
    return plan

def create_lower_session(user, name, day_num):
    plan = WorkoutPlan(user_id=user.id, name=name, schedule_day=day_num)
    db.session.add(plan)
    db.session.flush()
    
    settings = get_volume_settings(user.goal)
    selected_ids = []
    exercises_to_add = []

    # 1. Squat pattern
    ex1 = select_exercise(muscle_group='legs_quad', mechanics='squat', type='compound', exclude_ids=selected_ids)
    if ex1: exercises_to_add.append(ex1); selected_ids.append(ex1.id)

    # 2. Hinge pattern
    ex2 = select_exercise(mechanics='hinge', type='compound', exclude_ids=selected_ids)
    if ex2: exercises_to_add.append(ex2); selected_ids.append(ex2.id)
    
    # 3. Lunge pattern / Single Leg
    ex3 = select_exercise(mechanics='lunge', exclude_ids=selected_ids)
    if ex3: exercises_to_add.append(ex3); selected_ids.append(ex3.id)
    
    # 4. Leg Isolation (Extension)
    ex4 = select_exercise(muscle_group='legs_quad', type='isolation', exclude_ids=selected_ids)
    if ex4: exercises_to_add.append(ex4); selected_ids.append(ex4.id)

    # 5. Leg Isolation (Curl)
    ex5 = select_exercise(muscle_group='legs_ham', type='isolation', exclude_ids=selected_ids)
    if ex5: exercises_to_add.append(ex5); selected_ids.append(ex5.id)
    
    # 6. Core
    ex6 = select_exercise(muscle_group='core', exclude_ids=selected_ids)
    if ex6: exercises_to_add.append(ex6); selected_ids.append(ex6.id)
    
    # Add to DB
    for idx, ex in enumerate(exercises_to_add):
        we = WorkoutExercise(
            plan_id=plan.id,
            exercise_id=ex.id,
            sets=settings['sets'],
            reps_range=settings['reps'],
            rest_time=settings['rest'],
            order=idx+1
        )
        db.session.add(we)
    return plan

def create_ppl_session(user, type_name, day_num):
    plan = WorkoutPlan(user_id=user.id, name=f"{type_name} {day_num}", schedule_day=day_num)
    db.session.add(plan)
    db.session.flush()
    
    settings = get_volume_settings(user.goal)
    selected_ids = []
    exercises_to_add = []
    
    if type_name == "Push":
        # 1. Compound Chest
        ex1 = select_exercise(muscle_group='chest', type='compound', exclude_ids=selected_ids)
        if ex1: exercises_to_add.append(ex1); selected_ids.append(ex1.id)
        # 2. Compound Shoulder
        ex2 = select_exercise(muscle_group='shoulders', type='compound', exclude_ids=selected_ids)
        if ex2: exercises_to_add.append(ex2); selected_ids.append(ex2.id)
        # 3. Isolation Chest
        ex3 = select_exercise(muscle_group='chest', type='isolation', exclude_ids=selected_ids)
        if ex3: exercises_to_add.append(ex3); selected_ids.append(ex3.id)
        # 4. Isolation Shoulder
        ex4 = select_exercise(muscle_group='shoulders', type='isolation', exclude_ids=selected_ids)
        if ex4: exercises_to_add.append(ex4); selected_ids.append(ex4.id)
        # 5. Tricep
        ex5 = select_exercise(muscle_group='arms', mechanics='push', exclude_ids=selected_ids)
        if ex5: exercises_to_add.append(ex5); selected_ids.append(ex5.id)
        # 6. Tricep or Chest
        ex6 = select_exercise(muscle_group='arms', mechanics='push', exclude_ids=selected_ids)
        if not ex6: ex6 = select_exercise(mechanics='push', exclude_ids=selected_ids)
        if ex6: exercises_to_add.append(ex6); selected_ids.append(ex6.id)

    elif type_name == "Pull":
        # 1. Vertical Pull
        ex1 = select_exercise(muscle_group='back', mechanics='pull', type='compound', exclude_ids=selected_ids)
        if ex1: exercises_to_add.append(ex1); selected_ids.append(ex1.id)
        # 2. Horizontal Pull
        ex2 = select_exercise(muscle_group='back', mechanics='pull', type='compound', exclude_ids=selected_ids) 
        if ex2: exercises_to_add.append(ex2); selected_ids.append(ex2.id)
        # 3. Back Isolation (or another compound)
        ex3 = select_exercise(muscle_group='back', exclude_ids=selected_ids)
        if ex3: exercises_to_add.append(ex3); selected_ids.append(ex3.id)
        # 4. Bicep
        ex4 = select_exercise(muscle_group='arms', mechanics='pull', exclude_ids=selected_ids)
        if ex4: exercises_to_add.append(ex4); selected_ids.append(ex4.id)
        # 5. Bicep
        ex5 = select_exercise(muscle_group='arms', mechanics='pull', exclude_ids=selected_ids)
        if ex5: exercises_to_add.append(ex5); selected_ids.append(ex5.id)
        # 6. Core or Rear Delt
        ex6 = select_exercise(muscle_group='core', exclude_ids=selected_ids)
        if ex6: exercises_to_add.append(ex6); selected_ids.append(ex6.id)

    elif type_name == "Legs":
        # 1. Squat
        ex1 = select_exercise(muscle_group='legs_quad', mechanics='squat', type='compound', exclude_ids=selected_ids)
        if ex1: exercises_to_add.append(ex1); selected_ids.append(ex1.id)
        # 2. Hinge
        ex2 = select_exercise(mechanics='hinge', exclude_ids=selected_ids)
        if ex2: exercises_to_add.append(ex2); selected_ids.append(ex2.id)
        # 3. Lunge
        ex3 = select_exercise(mechanics='lunge', exclude_ids=selected_ids)
        if ex3: exercises_to_add.append(ex3); selected_ids.append(ex3.id)
        # 4. Quad Isolation
        ex4 = select_exercise(muscle_group='legs_quad', type='isolation', exclude_ids=selected_ids)
        if ex4: exercises_to_add.append(ex4); selected_ids.append(ex4.id)
        # 5. Ham Isolation
        ex5 = select_exercise(muscle_group='legs_ham', type='isolation', exclude_ids=selected_ids)
        if ex5: exercises_to_add.append(ex5); selected_ids.append(ex5.id)
        # 6. Core
        ex6 = select_exercise(muscle_group='core', exclude_ids=selected_ids)
        if ex6: exercises_to_add.append(ex6); selected_ids.append(ex6.id)

    for idx, ex in enumerate(exercises_to_add):
        we = WorkoutExercise(
            plan_id=plan.id,
            exercise_id=ex.id,
            sets=settings['sets'],
            reps_range=settings['reps'],
            rest_time=settings['rest'],
            order=idx+1
        )
        db.session.add(we)
    return plan

def generate_routine(user):
    """
    Generates a workout routine based on user profile.
    Returns a list of WorkoutPlan objects (unsaved).
    """
    
    # 1. Determine Structure
    structure = "FBW"
    days = user.days_available
    
    if user.experience_level == 'beginner':
        structure = "FBW"
        num_plans = min(days, 3) 
    elif user.experience_level == 'intermediate':
        if days == 4:
            structure = "UpperLower"
            num_plans = 4
        elif 3 <= days <= 6:
            structure = "PPL"
            num_plans = days 
        else:
            structure = "FBW"
            num_plans = days

    plans = []
    
    if structure == "FBW":
        # Generate A, B, C routines
        # Spacing logic: 1, 3, 5 for 3 days.
        schedule = []
        if num_plans == 1: schedule = [1]
        elif num_plans == 2: schedule = [1, 4]
        elif num_plans == 3: schedule = [1, 3, 5]
        else: schedule = list(range(1, num_plans + 1)) # Fallback if someone wants 4+ FBW

        for i, day in enumerate(schedule):
            plan_name = f"FBW {chr(65+i)}" # FBW A, FBW B...
            plan = create_fbw_session(user, plan_name, day)
            plans.append(plan)
            
    elif structure == "UpperLower":
        # Upper A, Lower A, Upper B, Lower B
        # Mon, Tue, Thu, Fri -> 1, 2, 4, 5
        plans.append(create_upper_session(user, "Upper A", 1))
        plans.append(create_lower_session(user, "Lower A", 2))
        plans.append(create_upper_session(user, "Upper B", 4))
        plans.append(create_lower_session(user, "Lower B", 5))
        
    elif structure == "PPL":
        # Push, Pull, Legs...
        cycle = ["Push", "Pull", "Legs"]
        for i in range(1, num_plans + 1):
            type_name = cycle[(i-1) % 3]
            plan = create_ppl_session(user, type_name, i)
            plans.append(plan)
            
    return plans

def calculate_diet(user):
    if user.gender == 'male':
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
        
    activity_factor = 1.375
    if user.days_available >= 5:
        activity_factor = 1.55
    elif user.days_available >= 3:
        activity_factor = 1.375
    else:
        activity_factor = 1.2
        
    tdee = bmr * activity_factor
    
    if user.goal == 'weight_loss':
        target_calories = tdee - 500
        protein_per_kg = 2.2
        fat_per_kg = 0.8
    elif user.goal == 'hypertrophy' or user.goal == 'strength':
        target_calories = tdee + 300
        protein_per_kg = 2.0
        fat_per_kg = 1.0
    else:
        target_calories = tdee
        protein_per_kg = 1.6
        fat_per_kg = 1.0
        
    protein_g = user.weight * protein_per_kg
    fat_g = user.weight * fat_per_kg
    
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    rem_cal = target_calories - (protein_cal + fat_cal)
    carbs_g = max(0, rem_cal / 4)
    
    return {
        "bmr": int(bmr),
        "tdee": int(tdee),
        "target_calories": int(target_calories),
        "protein": int(protein_g),
        "fat": int(fat_g),
        "carbs": int(carbs_g)
    }
