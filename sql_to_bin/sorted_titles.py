import os
import pickle

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

# Retrieves the list of titles from titles.bin
with open(os.path.join(DATA_DIR, "titles.bin"), "rb") as f:
    titles = pickle.load(f)

# Retrieves the list of tuples (node, incomingLinks) from autocomplete.bin
with open(os.path.join(DATA_DIR, "autocomplete.bin"), "rb") as f:
    autocomplete = pickle.load(f)

# Creates a list of lowercase title strings sorted by the titles in autocomplete
sorted_title_strings = [titles[node].lower() for node, _ in autocomplete]

# Writes data to binary files using pickle
out_path = os.path.join(DATA_DIR, "sorted_title_strings.bin")
with open(out_path, "wb") as f:
    pickle.dump(sorted_title_strings, f, protocol=pickle.HIGHEST_PROTOCOL)