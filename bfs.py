from collections import deque
from array import array
import bisect #for prefix search
import pickle
import random
import time

class WikiSearch:

    #loads in csr
    def __init__(self):
        num_nodes = 19101118
        num_edges = 717960658

        self.forward_offsets = array('I')
        with open("data/forward_offsets.bin", "rb") as f:
            self.forward_offsets.fromfile(f, num_nodes + 1)

        self.forward_neighbors = array('I')
        with open("data/forward_neighbors.bin", "rb") as f:
            self.forward_neighbors.fromfile(f, num_edges)

        self.reverse_offsets = array('I')
        with open("data/reverse_offsets.bin", "rb") as f:
            self.reverse_offsets.fromfile(f, num_nodes + 1)

        self.reverse_neighbors = array('I')
        with open("data/reverse_neighbors.bin", "rb") as f:
            self.reverse_neighbors.fromfile(f, num_edges)

        with open("data/title_to_node.bin", "rb") as f:
            self.title_to_node = pickle.load(f)

        with open("data/titles.bin", "rb") as f:
            self.titles = pickle.load(f)

        with open("data/autocomplete.bin", "rb") as f:
            self.autocomplete = pickle.load(f)

        with open("data/sorted_title_strings.bin", "rb") as f:
            self.sorted_title_strings = pickle.load(f)
        
        with open("data/is_redirect_array.bin", "rb") as f:
            self.is_redirect_array = pickle.load(f)

    def extend(self, queue: list, path: dict, visited: dict, reversevisited: dict,
               neighbors, offsets):

        level_size = len(queue)
        for _ in range(level_size):
            current = queue.popleft()
            start = offsets[current]
            end = offsets[current+1]
            
            for i in range(start,end):
                neighbor = neighbors[i]
                if neighbor not in visited:
                    path[neighbor] = current
                    visited.add(neighbor)
                    if(neighbor in reversevisited):
                        return neighbor
                    queue.append(neighbor)
        return None

    def BiBFS(self, start_title: str, end_title: str):

        if start_title in self.title_to_node:
            start = self.title_to_node[start_title]
        else:
            return None
        
        if end_title in self.title_to_node:
            end = self.title_to_node[end_title]
        else:
            return None

        if(start is None or end is None):
            return None

        if self.is_redirect_array[start] == 1:
            start = self.forward_neighbors[self.forward_offsets[start]]

        if self.is_redirect_array[end] == 1:
            end = self.reverse_neighbors[self.reverse_offsets[end]]
        
        if(start == end):
            return [start]
        

        meeting = None
        forward_queue = deque([start])
        backward_queue = deque([end])

        forward_path = {start: None}
        backward_path = {end: None}

        forward_visited = {start}
        backward_visited = {end}

        while forward_queue and backward_queue:
            if len(forward_queue) <= len(backward_queue):
                meeting = self.extend(forward_queue, forward_path, forward_visited, backward_visited,
                                      self.forward_neighbors, self.forward_offsets)
                if meeting is not None:
                    break
            else:
                meeting = self.extend(backward_queue, backward_path, backward_visited, forward_visited,
                                      self.reverse_neighbors, self.reverse_offsets)
                if meeting is not None:
                    break

        if meeting is not None:
            left_half = []
            tmp = meeting
            while tmp is not None:
                left_half.append(tmp)
                tmp = forward_path[tmp]
            left_half.reverse()

            right_half = []
            tmp = backward_path[meeting]
            while tmp is not None:
                right_half.append(tmp)
                tmp = backward_path[tmp]

            node_path = left_half + right_half
            page_path = [self.titles[node] for node in node_path]

            return page_path

        return None

    def prefix_search(self, prefix, max_candidates=250000, limit=5):
        # start = time.perf_counter()
        prefix = prefix.lower()

        left = bisect.bisect_left(
            self.sorted_title_strings,
            prefix
        )

        right = bisect.bisect_left(
            self.sorted_title_strings,
            prefix + chr(255)
        )

        if right - left > max_candidates:
            right = left + max_candidates

        candidates = self.autocomplete[left:right]

        candidates = sorted(
            candidates,
            key=lambda x: x[1],
            reverse=True
        )

        results = [
            (node, self.titles[node])
            for node, _ in candidates[:limit]
        ]

        # Put the title of the prefix at the top if it exists
        if left < len(self.sorted_title_strings) and self.sorted_title_strings[left] == prefix:
            exact_node = self.autocomplete[left][0]
            exact_result = (exact_node, self.titles[exact_node])

            for i, (node, _) in enumerate(results):
                if node == exact_node:
                    del results[i]
                    break

            results.insert(0, exact_result)
            results = results[:limit]

            for node, title in results:
                if self.is_redirect_array[node] == 1:
                    node = self.forward_neighbors[self.forward_offsets[node]]
                    node = self.forward_neighbors[self.forward_offsets[node]]
                    title = self.titles[node]

        # elapsed = time.perf_counter() - start
        return results

    def random_title(self):
        random_node = random.randint(0,19101117)
        
        if self.is_redirect_array[random_node] == 1:
            random_node = self.forward_neighbors[self.forward_offsets[random_node]]
            random_node = self.forward_neighbors[self.forward_offsets[random_node]]
            
        return self.titles[random_node].replace("_"," ")
