from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from BFS import WikiSearch
from flask import jsonify

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace

wiki = WikiSearch()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    start = (data["start"]).replace(" ","_")
    end = (data["end"]).replace(" ","_")

    path = wiki.BiBFS(start,end)
    for node in path:
        node = node.replace("_"," ")
    return jsonify({"path": path})

if __name__ == "__main__":
    app.run(debug=True,use_reloader = False)
