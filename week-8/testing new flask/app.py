from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
import mysql.connector
from datetime import datetime, timedelta
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'jouw_geheime_sleutel'

# Flask-Login configuratie
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# Database connectie configuratie
db_config = {
    'host': 'localhost',
    'user': 'X',
    'password': 'Y',
    'database': 'flask_local_database_test_2'
}

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


# Gebruiker loader
@login_manager.user_loader
def user_loader(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    record = cursor.fetchone()
    conn.close()
    if record:
        user = User(user_id)  # Pas de user_id toe wanneer je een User instantieert
        return user
    return None


@app.route('/')
def home():
    return render_template('index.html')
@app.route('/secret')
def secret_hunt():
    return render_template('secret_hunt.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Remember, in a real app, ensure password handling is secure
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and user['password'] == password:  # This check should be replaced with a secure password verification
            user_id = user['id']
            login_user(User(user_id))
            # Redirect the user based on their role
            if user['role'] == 'TEACHER':
                return redirect(url_for('teacher_agenda'))
            elif user['role'] == 'STUDENT':
                return redirect(url_for('student_agenda'))
            else:
                flash('Invalid role')
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))  # Redirect back to login for incorrect credentials
    # For a GET request or any other method, just render the login template
    return render_template('login.html')


@app.route('/teacher_agenda')
@login_required
def teacher_agenda():
    # Code om de agenda voor de leraar op te halen en weer te geven
    return "Welkom op de leraar agenda pagina!"





@app.route('/student_agenda')
@login_required
def student_agenda():
    # Assuming the current_user has the 'id' attribute storing the user's ID
    student_id = current_user.id

    query = """
    SELECT l.*, la.attendance_status
    FROM lessons l
    JOIN student_lessons sl ON l.id = sl.lesson_id
    LEFT JOIN lesson_attendance la ON l.id = la.lesson_id AND la.student_id = sl.student_id
    WHERE sl.student_id = %s
    ORDER BY l.date, l.start_time;
    """

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (student_id,))
    lessons = cursor.fetchall()
    conn.close()

    return render_template('student_agenda.html', lessons=lessons)


@app.route('/dashboard')
@login_required
def dashboard():
    return "Je bent ingelogd!"


@app.route('/profile')
@login_required
def profile():
    # Fetch User Info
    user_info = get_user_info(current_user.id)
    # Fetch Upcoming Classes
    upcoming_classes = get_upcoming_classes(current_user.id)
    # Fetch Attendance Records and Calculate Streak
    attendance_records = fetch_attendance_records(current_user.id)
    current_streak = calculate_streak(attendance_records)

    return render_template('profile.html', user_info=user_info, upcoming_classes=upcoming_classes, current_streak=current_streak)

def get_user_info(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, role FROM users WHERE id = %s", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

def get_upcoming_classes(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT l.id, l.name, l.date
    FROM lessons l
    JOIN student_lessons sl ON l.id = sl.lesson_id
    WHERE sl.student_id = %s AND l.date >= CURDATE()
    ORDER BY l.date ASC
    """
    cursor.execute(query, (user_id,))
    upcoming_classes = cursor.fetchall()
    conn.close()
    return upcoming_classes

def fetch_attendance_records(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT la.lesson_id, la.attendance_status, l.date
    FROM lesson_attendance la
    JOIN lessons l ON la.lesson_id = l.id
    WHERE la.student_id = %s AND la.attendance_status = 'ATTENDED'
    ORDER BY l.date DESC
    """
    cursor.execute(query, (user_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def calculate_streak(records):
    if not records:
        return 0
    streak = 0
    today = datetime.now().date()
    for record in records:
        if (today - record['date']).days > 1:
            break
        today -= timedelta(days=1)
        streak += 1
    return streak


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
