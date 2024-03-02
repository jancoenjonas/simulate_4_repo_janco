from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
import mysql.connector
from credentials import (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB,
                         MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER)

app = Flask(__name__)
app.secret_key = 'janco_very_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def get_db_connection():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    return conn


# Assuming you have a User class that has properties for id, username, role, major, nfc_tags, streak, longest_streak, and classes_enrolled
class User(UserMixin):
    def __init__(self, id, username, role, major, nfc_tags=None, streak=0, longest_streak=0, classes_enrolled=None):
        self.id = id
        self.username = username
        self.role = role
        self.major = major
        self.nfc_tags = nfc_tags
        self.streak = streak
        self.longest_streak = longest_streak
        self.classes_enrolled = classes_enrolled or []


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch user details
    cursor.execute("SELECT id, username, role, major FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        return None

    # Initialize the user
    user = User(
        id=user_data['id'],
        username=user_data['username'],
        role=user_data['role'],
        major=user_data['major']
    )

    # Fetch NFC tag data if exists
    cursor.execute("SELECT tag_data FROM nfc_tags WHERE user_id = %s", (user_id,))
    nfc_data = cursor.fetchall()  # You might have multiple NFC tags for one user
    if nfc_data:
        user.nfc_tags = [tag['tag_data'] for tag in nfc_data]

    # Fetch streak data if exists
    cursor.execute("SELECT current_streak, longest_streak FROM streaks WHERE user_id = %s", (user_id,))
    streak_data = cursor.fetchone()
    if streak_data:
        user.streak = streak_data['current_streak']
        user.longest_streak = streak_data['longest_streak']

    # Fetch classes enrolled
    cursor.execute("""
        SELECT lessons.name 
        FROM lessons 
        JOIN student_lessons ON lessons.id = student_lessons.lesson_id 
        WHERE student_lessons.student_id = %s
    """, (user_id,))
    classes = cursor.fetchall()
    user.classes_enrolled = [lesson['name'] for lesson in classes]

    cursor.close()
    conn.close()

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        plaintext_password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data and check_password_hash(user_data['password'], plaintext_password):
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                role=user_data['role'],
                major=user_data['major']
            )
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    if current_user.role == 'STUDENT':
        return redirect(url_for('student_schedule'))
    elif current_user.role == 'TEACHER':
        return redirect(url_for('teacher_attendance'))
    # Additional role handling as needed
    return "Welcome, " + current_user.id  # Default landing page for other roles or unspecified conditions


@app.template_filter('get_class_for_hour')
def get_class_for_hour(lessons, hour):
    for lesson in lessons:
        lesson_hour = int(lesson['time'].split(':')[0])
        if lesson_hour == hour:
            if lesson['attendance'] == 'ATTENDED':
                return 'attended'
            elif lesson['attendance'] == 'ABSENT':
                return 'missed'
            elif lesson['attendance'] == 'UPCOMING':
                return 'future'
    return 'no-class'


@app.template_filter('get_lesson_name_for_hour')
def get_lesson_name_for_hour(lessons, hour):
    for lesson in lessons:
        lesson_hour = int(lesson['time'].split(':')[0])
        if lesson_hour == hour:
            return lesson['name']
    return ''


@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.id,))
    user_details = cursor.fetchone()
    if not user_details:
        cursor.close()
        conn.close()
        flash('User not found.')
        return redirect(url_for('index'))  # Or handle as needed

    # Fetch user's NFC hex if exists
    cursor.execute("SELECT tag_data FROM nfc_tags WHERE user_id = %s", (current_user.id,))
    nfc_data = cursor.fetchone()
    nfc_hex = nfc_data['tag_data'] if nfc_data else 'No NFC Tag Registered'

    # Fetch user's streaks
    cursor.execute("SELECT * FROM streaks WHERE user_id = %s", (current_user.id,))
    streaks = cursor.fetchone()
    current_streak = streaks['current_streak'] if streaks else 0
    longest_streak = streaks['longest_streak'] if streaks else 0

    # Fetch user's enrolled classes
    cursor.execute(
        "SELECT DISTINCT lessons.name FROM lessons "
        "JOIN student_lessons ON lessons.id = student_lessons.lesson_id "
        "WHERE student_id = %s",
        (current_user.id,))
    classes = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert the classes to a list of unique names
    classes_enrolled = [cls['name'] for cls in classes] if classes else []

    return render_template('profile.html',
                           username=user_details['username'],
                           uuid=current_user.id,
                           nfc_hex=nfc_hex,
                           current_streak=current_streak,
                           longest_streak=longest_streak,
                           classes_enrolled=classes_enrolled)


@app.route('/student/schedule')
@login_required
def student_schedule():
    if current_user.role != 'STUDENT':
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Updated query to join with student_lessons table
    cursor.execute("""
        SELECT l.* FROM lessons l
        JOIN student_lessons sl ON l.id = sl.lesson_id
        WHERE sl.student_id = %s
        ORDER BY FIELD(l.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), l.time
    """, (current_user.id,))
    lessons = cursor.fetchall()
    cursor.close()
    conn.close()

    schedule = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
    for lesson in lessons:
        schedule[lesson['day']].append(lesson)

    return render_template('student_schedule.html', schedule=schedule)


@app.route('/teacher/attendance')
@login_required
def teacher_attendance():
    if current_user.role != 'TEACHER':
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch the lessons taught by the teacher and attendance ordered by student
    cursor.execute("""
        SELECT u.username, u.id as student_id, l.day, l.time, l.name as lesson_name, 
               l.attendance, l.id as lesson_id
        FROM student_lessons sl
        JOIN lessons l ON sl.lesson_id = l.id
        JOIN users u ON sl.student_id = u.id
        WHERE l.teacher_id = %s
        ORDER BY u.username, l.day, l.time
    """, (current_user.id,))
    lessons = cursor.fetchall()

    # Organize the data by student for the template
    attendance_data = {}
    for lesson in lessons:
        student_name = lesson['username']
        student_id = lesson['student_id']  # This should now be correctly fetched from the query
        if student_name not in attendance_data:
            attendance_data[student_name] = []
        attendance_data[student_name].append({
            'student_id': student_id,
            'lesson_id': lesson['lesson_id'],
            'day': lesson['day'],
            'time': lesson['time'],
            'lesson_name': lesson['lesson_name'],
            'attendance': lesson['attendance']
        })

    cursor.close()
    conn.close()

    return render_template('teacher_attendance.html', attendance_data=attendance_data)



@app.route('/teacher/student_performance/<student_id>')
@login_required
def student_performance(student_id):
    if current_user.role != 'TEACHER':
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Make sure your query is correct here
    cursor.execute("""
        SELECT l.day, l.time, l.name AS lesson_name, l.attendance
        FROM lessons l
        JOIN student_lessons sl ON l.id = sl.lesson_id
        WHERE sl.student_id = %s
        ORDER BY FIELD(l.day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'), l.time
    """, (student_id,))

    lessons = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student_performance.html', lessons=lessons, student_id=student_id)


@app.route('/select_student')
@login_required
def select_student():
    if current_user.role != 'TEACHER':
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Ophalen van alle studenten
    cursor.execute("SELECT id, username FROM users WHERE role = 'STUDENT'")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('select_student.html', students=students)


@app.route('/feedback', methods=['GET'])
@login_required
def feedback_form():
    return render_template('feedback_form.html')


@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Send email with feedback content
        msg = Message(subject='Feedback from {}'.format(name),
                      recipients=['janco.sambaer@student.kdg.be'],  # Email where you want to receive feedback
                      sender=app.config['MAIL_DEFAULT_SENDER'],  # Sender's email
                      body=message)
        mail.send(msg)

        flash('Thank you for your feedback! It has been sent to the administrator.')
        return redirect(url_for('feedback_form'))


@app.route('/update_attendance', methods=['POST'])
@login_required
def update_attendance():
    # Check if the user is a teacher
    if current_user.role != 'TEACHER':
        return {"message": "Access Denied"}, 403

    # Receive and print the JSON data for debugging
    data = request.json
    print("Received data:", data)

    # Extract student_id, lesson_id, and new_status from the received data
    student_id = data.get('studentId')
    lesson_id = data.get('lessonId')
    new_status = data.get('newStatus')

    # Check if the necessary data is present
    if not student_id or not lesson_id or not new_status:
        return {"message": "Missing data"}, 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Execute the SQL query to update the attendance
        # Assuming there is an attendance column in the student_lessons join table
        cursor.execute("""
            UPDATE student_lessons 
            SET attendance = %s 
            WHERE student_id = %s AND lesson_id = %s
        """, (new_status, student_id, lesson_id))
        conn.commit()

        # Check if the update was successful
        if cursor.rowcount == 0:
            return {"message": "No record updated, check the student ID and lesson ID"}, 404

        message = f"Attendance updated successfully for student ID: {student_id} and lesson ID: {lesson_id}"
    except Exception as e:
        # Rollback in case of error and print the error message
        conn.rollback()
        print(f"Error updating attendance: {e}")  # Debug print
        message = f"Error updating attendance: {str(e)}"
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    # Return a success message
    return {"message": message}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
