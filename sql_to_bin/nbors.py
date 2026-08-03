import mysql.connector
from array import array
import os

HOST = "localhost"
USER = "root"
PASSWORD = "password" # This would be replaced with actual password
DATABASE = "data" # This is the name of the database

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)

conn = mysql.connector.connect(host=HOST, user=USER,
                               password=PASSWORD, database=DATABASE)

# Retrieves the page_id column of page
cur = conn.cursor()
cur.execute("SELECT page_id FROM page ORDER BY page_id")

page_to_node = {}

# Creates a dictionary mapping page_id to node
node = 0
for (pid,) in cur.fetchall():
    page_to_node[pid] = node
    node += 1

cur.close()
n = node
print(f"Node count: {n}")

# Initialize arrays of size n (node count) filled with zeros
fwdDeg = array('I', [0]) * n
revDeg = array('I', [0]) * n

# Retrieves the from_page_id and to_page_id columns of edges
cur = conn.cursor()
cur.execute("SELECT from_page_id, to_page_id FROM edges")

# Count the degrees of each node
# For the start page_id, increment the forward degree of the corresponding node
# For the target page_id, increment the reverse degree of the corresponding node
count = 0
for start, target in cur.fetchall():
    u = page_to_node[start]
    v = page_to_node[target]
    fwdDeg[u] += 1
    revDeg[v] += 1
    count += 1

cur.close()

# Create an offsets array for forward and reverse neighbors
fwdOff = array('I', [0]) * (n + 1)
revOff = array('I', [0]) * (n + 1)

# Calculate the offsets based on the degrees
for i in range(n):
    fwdOff[i + 1] = fwdOff[i] + fwdDeg[i]
    revOff[i + 1] = revOff[i] + revDeg[i]

# Initialize arrays for forward and reverse neighbors based on the offsets
fwdNbors = array('I', [0]) * fwdOff[-1]
revNbors = array('I', [0]) * revOff[-1]
fwdNext = array('I', fwdOff[:-1])
revNext = array('I', revOff[:-1])

# Retrieves the from_page_id and to_page_id columns
# of edges again to fill in the neighbor arrays
cur = conn.cursor()
cur.execute("SELECT from_page_id, to_page_id FROM edges")

# For each edge, find the corresponding nodes and fill in the neighbor arrays
count = 0
for start, target in cur.fetchall():
    u = page_to_node[start]
    v = page_to_node[target]
    fwdNbors[fwdNext[u]] = v
    fwdNext[u] += 1
    revNbors[revNext[v]] = u
    revNext[v] += 1
    count += 1

cur.close()
conn.close()

# Write data to binary files
for name, data in [
    ("forward_offsets.bin", fwdOff),
    ("forward_neighbors.bin", fwdNbors),
    ("reverse_offsets.bin", revOff),
    ("reverse_neighbors.bin", revNbors),
]:
    with open(os.path.join(DATA_DIR, name), "wb") as f:
        data.tofile(f)

print(f"Node count: {n}, Edge count: {count}")