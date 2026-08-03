from collections import deque
from array import array
import bisect #for prefix search
import mmap #use later for memory mapping
import pickle

#some stuff to work on:
#check extend function, may not be correct for bidirectional bfs (2)
#need to implement prefix search (1)
#should the pickle imports below be global objects or instances?
#memory mapping

#loads in csr
num_nodes = 19101118
num_edges = 717960658

forward_offsets = array('I')
with open("data/forward_offsets.bin", "rb") as f:
    forward_offsets.fromfile(f, num_nodes + 1)

forward_neighbors = array('I')
with open("data/forward_neighbors.bin", "rb") as f:
    forward_neighbors.fromfile(f, num_edges)

reverse_offsets = array('I')
with open("data/reverse_offsets.bin", "rb") as f:
    reverse_offsets.fromfile(f, num_nodes + 1)

reverse_neighbors = array('I')
with open("data/reverse_neighbors.bin", "rb") as f:
    reverse_neighbors.fromfile(f, num_edges)

#titles
with open("data/title_to_node.bin","rb") as f:
    title_to_node = pickle.load(f) #before BFS title->node

with open("data/titles.bin","rb") as f:
    titles = pickle.load(f) #after BFS node->title

#titles.bin,titles_offset,id_map

#for prefix search
#with open("titles_sorted.bin","rb") as f:
#    titles_sorted = pickle.load(f)
#with open("nodes_sorted.bin","rb") as f:
#    nodes_sorted = pickle.load(f)


class WikiSearch:

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

        if start_title in title_to_node:
            start = title_to_node[start_title]
        else:
            return None
        
        if end_title in title_to_node:
            end = title_to_node[end_title]
        else:
            return None

        if(start is None or end is None):
            return None
        
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
                                      forward_neighbors, forward_offsets)
                if meeting is not None:
                    break
            else:
                meeting = self.extend(backward_queue, backward_path, backward_visited, forward_visited,
                                      reverse_neighbors, reverse_offsets)
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
            page_path = [titles[node] for node in node_path]

            return page_path

        return None

    def prefix_search(prefix: str, limit: int): #WIP
        return
