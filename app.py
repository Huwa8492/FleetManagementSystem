from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

#Connect to the database
def get_db_connection():
    conn = sqlite3.connect('fleet.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()

    vehicles=conn.execute('SELECT * FROM Vehicles').fetchall()

    conn.close()

    return render_template('index.html',vehicles=vehicles)

if __name__ == '__main__':
    app.run(debug=True)