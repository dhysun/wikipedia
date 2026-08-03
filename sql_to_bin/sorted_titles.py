import os
import pickle

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

with open(os.path.join(DATA_DIR, "titles.bin"), "rb") as f:
    titles = pickle.load(f)

print(f"Loaded {len(titles):,} titles")

with open(os.path.join(DATA_DIR, "autocomplete.bin"), "rb") as f:
    autocomplete = pickle.load(f)

print(f"Loaded {len(autocomplete):,} autocomplete entries")

sorted_title_strings = [
    titles[node].lower()
    for node, _ in autocomplete
]

out_path = os.path.join(DATA_DIR, "sorted_title_strings.bin")

with open(out_path, "wb") as f:
    pickle.dump(
        sorted_title_strings,
        f,
        protocol=pickle.HIGHEST_PROTOCOL,
    )

print(f"Stored {len(sorted_title_strings):,} sorted title strings.")