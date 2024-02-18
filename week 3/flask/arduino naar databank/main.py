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
    result = cursor.fetchone()

    if result is None:
        # Generate new user credentials
        new_username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        new_password = generate_password()
        hashed_password = generate_password_hash(new_password)

        # Insert new user
        new_user_id = str(uuid.uuid4())
        cursor.execute('INSERT INTO users (id, username, password, role) VALUES (%s, %s, %s, %s)',
                       (new_user_id, new_username, hashed_password, 'STUDENT'))

        # Link NFC tag to new user
        cursor.execute('INSERT INTO nfc_tags (id, tag_data, user_id) VALUES (%s, %s, %s)',
                       (str(uuid.uuid4()), nfc_tag, new_user_id))

        conn.commit()

        # Send email with credentials
        send_email(new_username, new_password)

    cursor.close()
    conn.close()
    return 'NFC tag processed'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
