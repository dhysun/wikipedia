import mysql.connector
import pickle
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

# Retrieves the page_id and page_title columns of page
cur = conn.cursor()
cur.execute("SELECT page_id, page_title FROM page ORDER BY page_id")

titles = []

# Creates a list of titles as UTF-8 strings
for page_id, title in cur:
    title = title.decode("utf-8")
    titles.append(title)

print(f"Node count: {len(titles):,}")

# Creates a dictionary mapping titles to nodes
title_to_node = {t: i for i, t in enumerate(titles)}

# Writes data to binary files using pickle

titles_path = os.path.join(DATA_DIR, "titles.bin")

with open(titles_path, "wb") as f:
    pickle.dump(titles, f, protocol=pickle.HIGHEST_PROTOCOL)

title_to_node_path = os.path.join(DATA_DIR, "title_to_node.bin")

with open(title_to_node_path, "wb") as f:
    pickle.dump(title_to_node, f, protocol=pickle.HIGHEST_PROTOCOL)

cur.close()
conn.close()