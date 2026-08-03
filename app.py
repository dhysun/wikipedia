from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import bfs
import autocomplete

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)