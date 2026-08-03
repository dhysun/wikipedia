import os
import pickle
from array import array

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

with open(os.path.join(DATA_DIR, "titles.bin"), "rb") as f:
    titles = pickle.load(f)

print(f"Loaded {len(titles):,} titles")


revOff = array("I")

with open(os.path.join(DATA_DIR, "reverse_offsets.bin"), "rb") as f:
    revOff.fromfile(f, os.path.getsize(f.name) // revOff.itemsize)

autocomplete = []

for node, title in enumerate(titles):
    indegree = revOff[node + 1] - revOff[node]
    autocomplete.append((node, indegree))

autocomplete.sort(key=lambda x: titles[x[0]].lower())

out_path = os.path.join(DATA_DIR, "autocomplete.bin")

with open(out_path, "wb") as f:
    pickle.dump(autocomplete, f, protocol=pickle.HIGHEST_PROTOCOL,)

print(f"Stored {len(autocomplete):,} autocomplete entries.")