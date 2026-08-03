import pickle
import bisect

with open("data/autocomplete.bin","rb") as f:
    autocomplete = pickle.load(f)

with open("data/titles.bin","rb") as f:
    titles = pickle.load(f)

sorted_title_strings = [
    titles[node].lower()
    for node, _ in autocomplete
]

def prefix_search(prefix, max_candidates=250000, limit=10):
    prefix = prefix.lower()

    left = bisect.bisect_left(
        sorted_title_strings,
        prefix
    )

    right = bisect.bisect_left(
        sorted_title_strings,
        prefix + chr(255)
    )

    if right - left > max_candidates:
        right = left + max_candidates

    candidates = autocomplete[left:right]

    candidates = sorted(
        candidates,
        key=lambda x: x[1],
        reverse=True
    )

    return [
        (node, titles[node])
        for node, _ in candidates[:limit]
    ]