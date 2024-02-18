from flask import Flask, jsonify
from flask_mysqldb import MySQL
from credentials import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

app = Flask(__name__)

# Configure MySQL connection with imported credentials
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

mysql = MySQL(app)

@app.route('/users', methods=['GET'])
def get_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@app.route('/lessons/<int:user_id>', methods=['GET'])
def get_lessons(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM lessons WHERE user_id = %s", (user_id,))
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)

@app.route('/streaks/<int:user_id>', methods=['GET'])
def get_streaks(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM streaks WHERE user_id = %s", (user_id,))
    streaks = cursor.fetchall()
    cursor.close()
    return jsonify(streaks)

@app.route('/nfc_tags/<int:user_id>', methods=['GET'])
def get_nfc_tags(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM nfc_tags WHERE user_id = %s", (user_id,))
    nfc_tags = cursor.fetchall()
    cursor.close()
    return jsonify(nfc_tags)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')