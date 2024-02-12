from flask import Flask, request
import pymysql.cursors
from secret import *

app = Flask(__name__)

# Database connection
connection = pymysql.connect(host=SECRET_MYSQL_HOST,
                             user=SECRET_MYSQL_USER,
                             password=SECRET_MYSQL_PASSWORD,
                             database=SECRET_MYSQL_DATABASE,
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/upload-data', methods=['GET'])
def upload_data():
    data = request.args.get('data')
    if data:
        try:
            with connection.cursor() as cursor:
                # Insert data into MySQL database
                sql = "INSERT INTO EventActivity (title) VALUES (%s)"
                cursor.execute(sql, (data,))
                connection.commit()
                return "Data uploaded successfully"
        except Exception as e:
            print("Error:", e)
            return "Error occurred while uploading data"
    else:
        return "No data received"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SECRET_FLASK_PORT)
