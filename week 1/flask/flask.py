from flask import Flask, render_template
import mysql.connector
import os
from dotenv import load_dotenv

# Laad omgevingsvariabelen uit .env bestand
load_dotenv()

app = Flask(__name__)

# Database configuratie uit omgevingsvariabelen halen
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE'),
    'raise_on_warnings': True
}

@app.route('/')
def index():
    # Maak verbinding met de database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Voer een query uit om aanwezigheidsgegevens op te halen
    cursor.execute("SELECT * FROM attendance")
    records = cursor.fetchall()

    # Sluit de cursor en verbinding
    cursor.close()
    conn.close()

    # Render de index template en geef de opgehaalde gegevens door
    return render_template('index.html', records=records)

if __name__ == '__main__':
    # Run de app in debug modus op de lokale server
    app.run(debug=True)
