from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import datetime
from credentials import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB  # Import your credentials

app = Flask(__name__)

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

mysql = MySQL(app)

@app.route('/upload-data', methods=['GET'])
def upload_data():
    # Get data from the request's arguments
    tag_data = request.args.get('data', default='', type=str)
    
    # Establish a cursor to interact with MySQL
    cursor = mysql.connection.cursor()
    
    try:
        # Check if the tag_data already exists
        cursor.execute("SELECT id FROM nfc_tags WHERE tag_data = %s", (tag_data,))
        tag_entry = cursor.fetchone()
        
        if tag_entry:
            # If exists, update the scanned_at timestamp
            cursor.execute("UPDATE nfc_tags SET scanned_at = %s WHERE id = %s", (datetime.datetime.now(), tag_entry[0]))
        else:
            # If not, insert a new record (assuming user_id is known, replace `1` with actual user ID)
            query = "INSERT INTO nfc_tags (tag_data, user_id) VALUES (%s, %s)"
            cursor.execute(query, (tag_data, 1))
        
        # Commit to save changes
        mysql.connection.commit()
        
        # Close the cursor
        cursor.close()
        
        return jsonify({"success": True, "message": "Data uploaded successfully"}), 200
    except Exception as e:
        # In case of any errors, rollback the transaction
        mysql.connection.rollback()
        
        # Close the cursor
        cursor.close()
        
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
