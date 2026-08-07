from collections import deque
from array import array
import bisect #for prefix search
import pickle
import random
import heapq

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
               neighbors, offsets, forbidden_edges, forbidden_nodes, reversed: bool):

        level_size = len(queue)
        for _ in range(level_size):
            current = queue.popleft()
            start = offsets[current]
            end = offsets[current+1]
            
            for i in range(start,end):
                neighbor = neighbors[i]

                if not reversed:
                    if (current, neighbor) in forbidden_edges:
                        continue
                else:
                    if(neighbor,current) in forbidden_edges:
                        continue

                if neighbor in forbidden_nodes:
                    continue

                if neighbor not in visited:
                    path[neighbor] = current
                    visited.add(neighbor)
                    if(neighbor in reversevisited):
                        return neighbor
                    queue.append(neighbor)
        return None

    def BiBFS(self, start: int, end: int, forbidden_edges: set, forbidden_nodes: set):

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
                                      self.forward_neighbors, self.forward_offsets, forbidden_edges,
                                      forbidden_nodes, False)
                if meeting is not None:
                    break
            else:
                meeting = self.extend(backward_queue, backward_path, backward_visited, forward_visited,
                                      self.reverse_neighbors, self.reverse_offsets, forbidden_edges,
                                      forbidden_nodes, True)
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

            return node_path

        return None

    def k_shortest_paths(self, start_title: str, end_title: str, num_paths = 6):

        confirmed_paths = []
        candidate_paths = []
        candidate_set = set()

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
        
        if(start == end):
            return [start]

        if(self.is_redirect_array[start] == 1):
            start = self.forward_neighbors[self.offsets[start]]

        if(self.is_redirect_array[end] == 1):
            end = self.reverse_neighbors[self.offsets[end]]

        first = self.BiBFS(start,end,set(),set())
        if first is None: 
            return [] #Due to the existence of orphaned articles
        else:
            confirmed_paths.append(first)

        for i in range(1,num_paths):
            for node in range(len(confirmed_paths[-1])-1):
                spur_node = confirmed_paths[-1][node]
                root_path = confirmed_paths[-1][:node + 1]
                forbidden_edges = set()
                forbidden_nodes = set()


                for path in confirmed_paths:
                    if (path[:node + 1] == root_path) and (len(path) > node + 1):
                        forbidden_edges.add((path[node],path[node + 1]))

                for root_node in root_path[:-1]:
                    forbidden_nodes.add(root_node)

                spur_path = self.BiBFS(spur_node, end, forbidden_edges, forbidden_nodes)

                if spur_path is None:
                    continue

                total_path = root_path[:-1] + spur_path
                tuple_tpath = tuple(total_path)
                if tuple_tpath not in candidate_set:
                    candidate_set.add(tuple_tpath)
                    heapq.heappush(candidate_paths,(len(total_path),tuple_tpath))

            if candidate_paths:
                _, new_path = heapq.heappop(candidate_paths)
                confirmed_paths.append(list(new_path))
            else:
                break

        title_paths = []
        for path in confirmed_paths:
            title_paths.append([self.titles[node] for node in path])

        return title_paths

    def canonical_node(self, node):
        if self.is_redirect_array[node] == 1:
            node = self.forward_neighbors[self.forward_offsets[node]]
            node = self.forward_neighbors[self.forward_offsets[node]]
        return node


    def prefix_search(self, prefix, max_candidates=250000, limit=5):
        prefix = prefix.lower()

        left = bisect.bisect_left(self.sorted_title_strings, prefix)
        right = bisect.bisect_left(self.sorted_title_strings, prefix + chr(255))

        if right - left > max_candidates:
            right = left + max_candidates

        candidates = sorted(
            self.autocomplete[left:right],
            key=lambda x: x[1],
            reverse=True
        )

        exact_node = None
        if left < len(self.sorted_title_strings) and self.sorted_title_strings[left] == prefix:
            exact_node = self.autocomplete[left][0]

        results = []
        seen = set()

        # Preserve exact match first
        if exact_node is not None:
            canonical = self.canonical_node(exact_node)
            results.append((exact_node, self.titles[exact_node]))
            seen.add(canonical)

        # Fill remaining slots
        for node, _ in candidates:
            if node == exact_node:
                continue

            canonical = self.canonical_node(node)

            if canonical in seen:
                continue

            seen.add(canonical)
            results.append((node, self.titles[node]))

            if len(results) == limit:
                break

        return results

    def random_title(self):
        random_node = random.randint(0,19101117)
        
        if self.is_redirect_array[random_node] == 1:
            random_node = self.forward_neighbors[self.forward_offsets[random_node]]
            
        return self.titles[random_node].replace("_"," ")
