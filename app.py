from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from bfs import WikiSearch
from flask import jsonify

import time

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace

wiki = WikiSearch()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    start_time = time.perf_counter()

    data = request.get_json()
    start = (data["start"]).replace(" ", "_")
    end = (data["end"]).replace(" ", "_")

    n = int(data.get("n", 6))
    n = max(1, min(n, 99))

    path = wiki.k_shortest_paths(start, end, n, 10)

    if path[0] is not None:
        path[0] = [
            [node.replace("_", " ") for node in single_path]
            for single_path in path[0]
        ]

    num_paths = len(path[0]) if path[0] is not None else 0

    elapsed_time = (time.perf_counter() - start_time) * 1000

    if elapsed_time >= 999:
        time_str = f"{elapsed_time / 1000:.2f} seconds"
    elif elapsed_time >= 100:
        time_str = f"{elapsed_time:.0f} ms"
    elif elapsed_time >= 10:
        time_str = f"{elapsed_time:.1f} ms"
    else:
        time_str = f"{elapsed_time:.2f} ms"

    return jsonify({"path": path,
                    "num_paths": num_paths,
                    "time_str": time_str})

@app.route("/autocomplete")
def autocomplete():
    prefix = request.args.get("q", "").replace(" ", "_")

    if len(prefix) == 0:
        return jsonify([])

    results = wiki.prefix_search(prefix)

    return jsonify([
        title.replace("_", " ")
        for _, title in results
    ])

@app.route("/random")
def random_article():
    return jsonify({"title": wiki.random_title()})

if __name__ == "__main__":
    # print(app.url_map)
    app.run(debug = True, use_reloader = False)
