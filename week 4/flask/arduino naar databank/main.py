from flask import Flask, request
import mysql.connector
from werkzeug.security import generate_password_hash
import smtplib
from email.message import EmailMessage
import uuid
import random
import string
from credentials import DB_CONFIG, EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT  # Import configurations

app = Flask(__name__)

def send_email(username, password):
    msg = EmailMessage()
    msg['Subject'] = 'New Account Credentials'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
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
    conn = mysql.connector.connect(**DB_CONFIG)  # Use imported DB config
    cursor = conn.cursor()

    # Check if NFC tag is already linked to a user
    cursor.execute('SELECT user_id FROM nfc_tags WHERE tag_data = %s', (nfc_tag,))
    user_result = cursor.fetchone()

    if user_result:
        user_id = user_result[0]

        # Check if the user has an existing streak
        cursor.execute('SELECT id, current_streak, longest_streak FROM streaks WHERE user_id = %s', (user_id,))
        streak_result = cursor.fetchone()

        if streak_result:
            streak_id, current_streak, longest_streak = streak_result
            current_streak += 1

            # Update the current streak
            cursor.execute('UPDATE streaks SET current_streak = %s WHERE id = %s', (current_streak, streak_id))

            # Check if the current streak is greater than the longest streak
            if current_streak > longest_streak:
                cursor.execute('UPDATE streaks SET longest_streak = %s WHERE id = %s', (current_streak, streak_id))
        else:
            # If no streak record exists, create a new one with a streak of 1
            new_streak_id = str(uuid.uuid4())
            cursor.execute('INSERT INTO streaks (id, user_id, current_streak, longest_streak) VALUES (%s, %s, 1, 1)',
                           (new_streak_id, user_id))

    else:
        # NFC tag not linked to any user, create new user and set streak to 1
        new_username, new_password, hashed_password, new_user_id = create_new_user(cursor)
        cursor.execute('INSERT INTO nfc_tags (id, tag_data, user_id) VALUES (%s, %s, %s)',
                       (str(uuid.uuid4()), nfc_tag, new_user_id))
        new_streak_id = str(uuid.uuid4())
        cursor.execute('INSERT INTO streaks (id, user_id, current_streak, longest_streak) VALUES (%s, %s, 1, 1)',
                       (new_streak_id, new_user_id))
        send_email(new_username, new_password)

    conn.commit()
    cursor.close()
    conn.close()
    return 'NFC tag processed'

def create_new_user(cursor):
    new_username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    new_password = generate_password()
    hashed_password = generate_password_hash(new_password)
    new_user_id = str(uuid.uuid4())

    cursor.execute('INSERT INTO users (id, username, password, role) VALUES (%s, %s, %s, %s)',
                   (new_user_id, new_username, hashed_password, 'STUDENT'))
    return new_username, new_password, hashed_password, new_user_id

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
