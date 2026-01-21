from models import db, WorkoutExercise

def suggest_next_load(exercise_history):
    """
    Suggests the next load based on the most recent workout history for an exercise.
    exercise_history: list of WorkoutLog objects (or dicts) sorted by date (most recent first).
    
    Rule:
    If user completed all sets with max reps in range -> Increase weight by 2.5kg (Upper) or 5kg (Lower) for next session.
    """
    if not exercise_history:
        return None # No history, can't suggest

    last_session = exercise_history[0]
    
    # Check if we hit the top of the rep range
    # reps_range format: "8-12"
    try:
        min_reps, max_reps = map(int, last_session.reps_range.split('-'))
    except:
        return last_session.weight # Fallback
        
    # Check if all sets met the max_reps condition
    # 'sets_performed' is a property on WorkoutLog that returns a list of ints.
    sets_performed = last_session.sets_performed
    
    if not sets_performed:
        return last_session.weight

    all_maxed = all(r >= max_reps for r in sets_performed)
    
    if all_maxed:
        # Determine increment based on muscle group
        # We need the exercise object.
        # last_session.workout_exercise is the association object, which has .exercise
        exercise = last_session.workout_exercise.exercise
        if 'legs' in exercise.muscle_group:
            increment = 5.0
        else:
            increment = 2.5
        
        return last_session.weight + increment
    else:
        return last_session.weight
