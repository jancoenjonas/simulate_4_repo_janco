from flask import Flask, request
import mysql.connector
from werkzeug.security import generate_password_hash
import smtplib
from email.message import EmailMessage
import uuid
import random
import string
from datetime import datetime, timedelta
import pytz
from credentials import DB_CONFIG, EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT  # Import configurations

app = Flask(__name__)

TIMEZONE = pytz.timezone('Europe/Brussels')


def send_email(username, password):
    msg = EmailMessage()
    msg['Subject'] = 'New Account Credentials'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS  # Consider updating this to send to the user's actual email address
    msg.set_content(f'Username: {username}\nPassword: {password}')

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


@app.route('/nfc', methods=['POST'])
def handle_nfc_tag():
    nfc_tag = request.form['nfc_tag']
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT user_id FROM nfc_tags WHERE tag_data = %s', (nfc_tag,))
    user_result = cursor.fetchone()

    if user_result:
        user_id = user_result['user_id']
        # New logic to handle attendance updates
        handle_attendance_update(cursor, user_id)
    else:
        # Logic for new user creation and linking NFC tag remains unchanged
        new_username, new_password, hashed_password, new_user_id = create_new_user(cursor)
        cursor.execute('INSERT INTO nfc_tags (tag_data, user_id) VALUES (%s, %s)',
                       (nfc_tag, new_user_id))
        send_email(new_username, new_password)
        # Handle attendance for the newly created user
        handle_attendance_update(cursor, new_user_id)

    conn.commit()
    cursor.close()
    conn.close()
    return 'NFC tag processed'


def create_new_user(cursor):
    new_username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    new_password = generate_password()
    hashed_password = generate_password_hash(new_password)
    new_user_id = str(uuid.uuid4())

    cursor.execute('INSERT INTO users (uuid, username, password_hash, role) VALUES (%s, %s, %s, %s)',
                   (new_user_id, new_username, hashed_password, 'student'))
    return new_username, new_password, hashed_password, new_user_id


def handle_attendance_update(cursor, user_id):
    now = datetime.now(TIMEZONE)
    current_date = now.date()
    current_time = now.time()
    day_of_week = now.isoweekday()

    cursor.execute("""
        SELECT lesson_uuid, start_time, end_time FROM lessons
        JOIN student_lessons ON lessons.lesson_uuid = student_lessons.lesson_uuid
        WHERE student_lessons.student_uuid = %s AND day_of_week = %s
    """, (user_id, day_of_week))

    for lesson in cursor.fetchall():
        lesson_uuid = lesson['lesson_uuid']
        start_time = lesson['start_time']
        end_time = lesson['end_time']
        attendance_status = 'upcoming'  # Default status

        if start_time <= current_time <= (datetime.combine(now, start_time) + timedelta(minutes=15)).time():
            attendance_status = 'attended'
        elif start_time < current_time <= end_time:
            attendance_status = 'late'

        # Insert or update attendance record
        cursor.execute("""
            INSERT INTO attendance_records (user_id, lesson_uuid, status, date) VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """, (user_id, lesson_uuid, attendance_status, current_date))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
