from collections import deque
import bisect
import pickle #to unpack .bin files, non-csr related files specifically
import random
import heapq
import numpy as np
import time #to track time-outs
from pathlib import Path

class WikiSearch:

    def __init__(self):

        DATA_DIR = Path(__file__).resolve().parent / "data"

        #loads in csr, num_nodes = 19101118, num_edges = 717960658
        self.forward_offsets = np.memmap(
            DATA_DIR / "forward_offsets.bin",
            dtype = np.uint32,
            mode="r"
        )

        self.reverse_offsets = np.memmap(
            DATA_DIR / "reverse_offsets.bin",
            dtype = np.uint32,
            mode="r"
        )

        self.forward_neighbors = np.memmap(
            DATA_DIR / "forward_neighbors.bin",
            dtype = np.uint32,
            mode="r"
        )

        self.reverse_neighbors = np.memmap(
            DATA_DIR / "reverse_neighbors.bin",
            dtype = np.uint32,
            mode="r"
        )

        #loads in titles and autocomplete related objects
        with open(DATA_DIR / "title_to_node.bin", "rb") as f:
            self.title_to_node = pickle.load(f)

        with open(DATA_DIR / "titles.bin", "rb") as f:
            self.titles = pickle.load(f)

        with open(DATA_DIR / "autocomplete.bin", "rb") as f:
            self.autocomplete = pickle.load(f)

        with open(DATA_DIR / "sorted_title_strings.bin", "rb") as f:
            self.sorted_title_strings = pickle.load(f)
        
        with open(DATA_DIR / "is_redirect_array.bin", "rb") as f:
            self.is_redirect_array = pickle.load(f)
        
        self.TIMEOUT = object() #TIMEOUT Object to track TIMEOUTS

    def extend(self, queue: list, path: dict, visited: dict, reversevisited: dict,
               neighbors, offsets, forbidden_edges, forbidden_nodes, reversed: bool, deadline = None):

        #checks entire level before switching frontiers
        level_size = len(queue)
        for _ in range(level_size):

            #timeout check
            if deadline is not None and time.monotonic() >= deadline:
                return self.TIMEOUT

            #Finds the bounds of the neighbors of current in the corresponding neighbors array
            current = queue.popleft()
            start = offsets[current]
            end = offsets[current+1]
            
            for i in range(start,end):
                neighbor = neighbors[i]

                #important as the orientation of forbidden edge is flipped if checking the reverse edges
                #continues if the current edge/node being checked is forbidden
                if not reversed:
                    if (current, neighbor) in forbidden_edges:
                        continue
                else:
                    if(neighbor,current) in forbidden_edges:
                        continue
                if neighbor in forbidden_nodes:
                    continue

                #add neighbor to queue
                if neighbor not in visited:
                    path[neighbor] = current
                    visited.add(neighbor)
                    if(neighbor in reversevisited):
                        return neighbor
                    queue.append(neighbor)
    
        return None

    def BiBFS(self, start: int, end: int, forbidden_edges: set, forbidden_nodes: set, deadline = None):

        #bidirectional BFS maintains both a forward and backward frontier 
        meeting = None
        forward_queue = deque([start])
        backward_queue = deque([end])

        #will keep track of the paths each frontier takes
        forward_path = {start: None}
        backward_path = {end: None}

        forward_visited = {start}
        backward_visited = {end}

        while forward_queue and backward_queue:

            #alternates exploring the frontier with the shorter queue
            if len(forward_queue) <= len(backward_queue):
                meeting = self.extend(forward_queue, forward_path, forward_visited, backward_visited,
                                      self.forward_neighbors, self.forward_offsets, forbidden_edges,
                                      forbidden_nodes, False, deadline)

                if meeting is self.TIMEOUT:
                    return self.TIMEOUT
                
                if meeting is not None:
                    break
                    
            else:
                meeting = self.extend(backward_queue, backward_path, backward_visited, forward_visited,
                                      self.reverse_neighbors, self.reverse_offsets, forbidden_edges,
                                      forbidden_nodes, True, deadline)
                
                if meeting is self.TIMEOUT:
                    return self.TIMEOUT
                
                if meeting is not None:
                    break

        #after Bidirectional BFS has finished
        if meeting is not None:
            left_half = []
            tmp = meeting

            #"Follows" the edges starting from the final appended edge
            while tmp is not None:
                left_half.append(tmp)
                tmp = forward_path[tmp]
            left_half.reverse()

            right_half = []
            tmp = backward_path[meeting]
            while tmp is not None:
                right_half.append(tmp)
                tmp = backward_path[tmp]

            node_path = left_half + right_half #right_half is already correctly oriented

            return node_path

        return None

    #modified version of Yen's Algorithm
    def k_shortest_paths(self, start_title: str, end_title: str, num_paths = 6, timeout = None):

        timeout_flag = False #checks if an early termination is due to a timeout
        confirmed_paths = []
        candidate_paths = []
        candidate_set = set()

        if timeout is not None:
            deadline = timeout + time.monotonic()
        else:
            deadline = None

        if start_title in self.title_to_node:
            start = self.title_to_node[start_title]
        else:
            return None, False
        
        if end_title in self.title_to_node:
            end = self.title_to_node[end_title]
        else:
            return None, False

        if(start is None or end is None):
            return None, False
        
        if(start == end):
            return [start]

        #checks if the entered string is a redirect article, if so follow the redirect
        if(self.is_redirect_array[start] == 1):
            start = self.forward_neighbors[self.offsets[start]]

        if(self.is_redirect_array[end] == 1):
            end = self.reverse_neighbors[self.offsets[end]]

        first = self.BiBFS(start,end,set(),set(), deadline)

        if first is self.TIMEOUT: #extremely rare
            return [], True
        
        if first is None: 
            return [], False #Due to the existence of orphaned articles (no incoming links)
        else:
            confirmed_paths.append(first)

        for i in range(1,num_paths):

            if deadline is not None and time.monotonic() >= deadline:
                timeout_flag = True
                break

            #starts checking spur nodes
            for node in range(len(confirmed_paths[-1])-1):
                spur_node = confirmed_paths[-1][node]
                root_path = confirmed_paths[-1][:node + 1]
                #due to using a CSR representation of the graph, removing parts of the graph is too expensive
                #a set of forbidden edges and nodes is used instead
                forbidden_edges = set()
                forbidden_nodes = set()

                for path in confirmed_paths:
                    if (path[:node + 1] == root_path) and (len(path) > node + 1):
                        forbidden_edges.add((path[node],path[node + 1]))

                for root_node in root_path[:-1]:
                    forbidden_nodes.add(root_node)

                spur_path = self.BiBFS(spur_node, end, forbidden_edges, forbidden_nodes, deadline)

                if spur_path is self.TIMEOUT:
                    timeout_flag = True
                    break

                if spur_path is None:
                    continue

                #combines root path (nodes before spur node) with spur path
                total_path = root_path[:-1] + spur_path
                tuple_tpath = tuple(total_path)

                #checks for duplicate paths that may have been refound
                if tuple_tpath not in candidate_set:
                    candidate_set.add(tuple_tpath)
                    heapq.heappush(candidate_paths,(len(total_path),tuple_tpath))

            if timeout_flag: #to avoid an incomplete canditate_paths if a timeout occurs
                break

            #min heap ensures shortest paths first
            if candidate_paths:
                _, new_path = heapq.heappop(candidate_paths)
                confirmed_paths.append(list(new_path))

            else:
                break

        title_paths = []
        
        #title_paths is an array of CSR nodes, convert back to titles
        for path in confirmed_paths:
            title_paths.append([self.titles[node] for node in path])

        return [title_paths, timeout_flag]

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
        #simple random title generator
        random_node = random.randint(0,19101117)
        
        if self.is_redirect_array[random_node] == 1:
            random_node = self.forward_neighbors[self.forward_offsets[random_node]]
            
        return self.titles[random_node].replace("_"," ")
