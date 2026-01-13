from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, WorkoutPlan, Exercise, WorkoutExercise
from logic.workout_generator import generate_routine, calculate_diet
from logic.progression import suggest_next_load
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key' # In production, use env var
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('plan'))
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('plan'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('setup'))
    return render_template('register.html')

@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    if request.method == 'POST':
        current_user.weight = float(request.form.get('weight'))
        current_user.height = float(request.form.get('height'))
        current_user.age = int(request.form.get('age'))
        current_user.gender = request.form.get('gender')
        current_user.goal = request.form.get('goal')
        current_user.experience_level = request.form.get('experience_level')
        current_user.days_available = int(request.form.get('days_available'))
        
        db.session.commit()
        
        # Clear existing plans if any (re-generation)
        WorkoutPlan.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # Generate new plan
        plans = generate_routine(current_user)
        # Plans are already added to session in generate_routine but not committed?
        # Actually in my logic I did db.session.add(plan) and flush.
        # So I just need to commit.
        db.session.commit()
        
        return redirect(url_for('plan'))
        
    return render_template('setup.html')

@app.route('/plan')
@login_required
def plan():
    if not current_user.goal:
        return redirect(url_for('setup'))
        
    plans = WorkoutPlan.query.filter_by(user_id=current_user.id).all()
    diet = calculate_diet(current_user)
    
    return render_template('plan.html', plans=plans, diet=diet)

@app.route('/diet', methods=['GET', 'POST'])
@login_required
def diet():
    from models import DietLog
    from sqlalchemy import func
    from logic.nutrition import search_food
    
    diet_targets = calculate_diet(current_user)
    search_results = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'search':
            query = request.form.get('food_query')
            weight = float(request.form.get('weight') or 0)
            
            if query and weight > 0:
                results = search_food(query)
                if not results:
                    flash(f'No results found for "{query}".')
                else:
                    # Pre-calculate for the given weight
                    for res in results:
                        factor = weight / 100.0
                        res['calc_calories'] = int(res['calories'] * factor)
                        res['calc_protein'] = round(res['protein'] * factor, 1)
                        res['calc_carbs'] = round(res['carbs'] * factor, 1)
                        res['calc_fat'] = round(res['fat'] * factor, 1)
                        res['weight'] = weight
                    search_results = results
            else:
                flash('Invalid search.')

        elif action == 'add':
            name = request.form.get('name')
            weight = float(request.form.get('weight'))
            calories = float(request.form.get('calories'))
            protein = float(request.form.get('protein'))
            carbs = float(request.form.get('carbs'))
            fat = float(request.form.get('fat'))
            
            entry = DietLog(
                user_id=current_user.id,
                food_name=f"{name} ({weight}g)",
                calories=int(calories),
                protein=protein,
                carbs=carbs,
                fat=fat,
                date=datetime.utcnow()
            )
            db.session.add(entry)
            db.session.commit()
            flash(f"Added {name}")
            return redirect(url_for('diet'))
        
    # Get today's logs
    today = datetime.utcnow().date()
    logs = DietLog.query.filter(
        DietLog.user_id == current_user.id,
        func.date(DietLog.date) == today
    ).all()
    
    totals = {
        'calories': sum(l.calories for l in logs),
        'protein': sum(l.protein for l in logs),
        'carbs': sum(l.carbs for l in logs),
        'fat': sum(l.fat for l in logs)
    }
    
    return render_template('diet.html', targets=diet_targets, logs=logs, totals=totals, search_results=search_results)

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    from models import WorkoutLog
    
    if request.method == 'POST':
        # Processing log entry
        workout_exercise_id = int(request.form.get('workout_exercise_id'))
        weight = float(request.form.get('weight'))
        reps_performed = request.form.get('reps_performed') # "10,10,10"
        
        log_entry = WorkoutLog(
            user_id=current_user.id,
            workout_exercise_id=workout_exercise_id,
            weight=weight,
            reps_performed=reps_performed,
            date=datetime.utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
        
        flash('Workout logged successfully!')
        return redirect(url_for('log'))
    
    # Get user's current plans
    plans = WorkoutPlan.query.filter_by(user_id=current_user.id).all()
    
    # Prepare data for logging view
    # We might want to show previous history or suggestion
    logging_data = []
    
    for plan in plans:
        plan_data = {'plan': plan, 'exercises': []}
        for we in plan.exercises:
            # Get last log
            last_log = WorkoutLog.query.filter_by(
                user_id=current_user.id, 
                workout_exercise_id=we.id
            ).order_by(WorkoutLog.date.desc()).first()
            
            # Suggestion
            if last_log:
                suggested_weight = suggest_next_load([last_log])
            else:
                suggested_weight = 20.0 # Start empty bar or dummy
                
            plan_data['exercises'].append({
                'we': we,
                'last_log': last_log,
                'suggested_weight': suggested_weight
            })
        logging_data.append(plan_data)

    return render_template('log.html', logging_data=logging_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Initialize DB when app is loaded (for Gunicorn/Render)
with app.app_context():
    db.create_all()
    # Auto-seed if empty
    try:
        if Exercise.query.first() is None:
            from seed_data import seed_exercises
            seed_exercises()
    except:
        pass # Handle cases where tables might not be fully ready in some contexts

if __name__ == '__main__':
    app.run(debug=True)
