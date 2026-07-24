#import a library to access the database
from collections import deque

class search:
    #nodes will be the page_id
    #take user inputted start and end and convert to relevant page_id
    #SQL COMMAND: SELECT page_id FROM page WHERE page_title = user_input_start
    #SELECT page_id FROM page WHERE page_title = user_input_end
    #set start and end to whatever the query returns
    def extend(self, queue: list, path: dict, visited: dict, reversevisited: dict):
        #Bidrectional BFS explores the entire level
        level_size = len(queue)
        for _ in range(level_size):
            current = queue.popleft()
            #SQL COMMAND: SELECT to_page_id FROM edges WHERE from_page_id = current
            #return result of query as a list neighbors
            neighbors = [] #placeholder
            for neighbor in neighbors:
                if neighbor not in visited:
                    path[neighbor] = current
                    visited.add(neighbor)
                    if(neighbor in reversevisited):
                        return neighbor
                    queue.append(neighbor)
        return None

    def BiBFS(self, start: int, end: int):
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
                meeting = self.extend(forward_queue,forward_path,forward_visited,backward_visited)
                if meeting is not None:
                    break
            else:
                meeting = self.extend(backward_queue,backward_path,backward_visited,forward_visited)
                if meeting is not None:
                    break
        if(meeting):
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

            id_path = left_half + right_half
            page_path = []

            for node in id_path:
                #SQL: SELECT page_title FROM page WHERE page_id = node
                #this can be done iteratively in SQL, if done so discard for loop
                #page_title will be in VarBin format will need to convert to string
                #page_path.append(result)
                break #placeholder
            return page_path

        return None
