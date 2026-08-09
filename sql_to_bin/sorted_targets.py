import os
import pickle
from array import array

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

# Retrieves the list of titles from titles.bin
with open(os.path.join(DATA_DIR, "titles.bin"), "rb") as f:
    titles = pickle.load(f)

# Retrieves the reverse offsets from reverse_offsets.bin 
# as an array of unsigned integers
revOff = array("I")
with open(os.path.join(DATA_DIR, "reverse_offsets.bin"), "rb") as f:
    revOff.fromfile(f, os.path.getsize(f.name) // revOff.itemsize)

# Creates a list of tuples (node, incomingLinks) for each title
autocomplete = []
for node, title in enumerate(titles):
    incomingLinks = revOff[node + 1] - revOff[node]
    autocomplete.append((node, incomingLinks))

# Sorts the autocomplete list based on the lowercase title strings
autocomplete.sort(key=lambda x: titles[x[0]].lower())

# Writes data to binary files using pickle
out_path = os.path.join(DATA_DIR, "autocomplete.bin")
with open(out_path, "wb") as f:
    pickle.dump(autocomplete, f, protocol=pickle.HIGHEST_PROTOCOL)