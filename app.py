from flask import Flask, render_template, request, jsonify
from WikiGraph import WikiSearch

import time

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Replace

# Create an instance of WikiSearch
wiki = WikiSearch()

# Home page goes to index.html
@app.route('/')
def index():
    return render_template('index.html')

# Search for routes
@app.route('/search', methods=['POST'])
def search():
    # Start a timer
    start_time = time.perf_counter()

    # Get the data sent from JS
    data = request.get_json()

    # Get the start and end articles, replacing spaces with underscores
    start = (data["start"]).replace(" ", "_")
    end = (data["end"]).replace(" ", "_")

    # Get requested number of paths
    n = int(data.get("n", 6))
    n = max(1, min(n, 99))

    # Perform the search for n paths, timing out after 10 seconds
    path = wiki.k_shortest_paths(start, end, n, 10)

    # If paths were found, then replace the underscores in the paths with spaces
    if path[0] is not None:
        path[0] = [
            [node.replace("_", " ") for node in single_path]
            for single_path in path[0]
        ]

    # Get the number of paths returned
    num_paths = len(path[0]) if path[0] is not None else 0

    # Stop the timer
    elapsed_time = (time.perf_counter() - start_time) * 1000

    # Format the time
    if elapsed_time >= 999:
        time_str = f"{elapsed_time / 1000:.2f} seconds"
    elif elapsed_time >= 100:
        time_str = f"{elapsed_time:.0f} ms"
    elif elapsed_time >= 10:
        time_str = f"{elapsed_time:.1f} ms"
    else:
        time_str = f"{elapsed_time:.2f} ms"

    # Return
    return jsonify({"path": path,
                    "num_paths": num_paths,
                    "time_str": time_str})

# Autocomplete handling
@app.route("/autocomplete")
def autocomplete():
    # Get the prefix for the search
    prefix = request.args.get("q", "").replace(" ", "_")

    # If the prefix is just the empty string, return nothing
    if len(prefix) == 0:
        return jsonify([])

    # Else, perform prefix_search with the prefix
    results = wiki.prefix_search(prefix)

    # Return the results, replacing underscores with spaces
    return jsonify([
        title.replace("_", " ")
        for _, title in results
    ])

# Random title handling
@app.route("/random")
def random_article():
    # Perform and return a random title
    return jsonify({"title": wiki.random_title()})

if __name__ == "__main__":
    # print(app.url_map)
    app.run(debug = True, use_reloader = False)
