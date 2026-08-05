import mysql.connector
import pickle
import os

HOST = "localhost"
USER = "root"
PASSWORD = "cr4nB399!"
DATABASE = "wikigraph"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

conn = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)

cur = conn.cursor()
cur.execute("""
    SELECT page_is_redirect
    FROM page
    ORDER BY page_id
""")

is_redirect = bytearray()

for (redirect,) in cur:
    is_redirect.append(redirect)

print(f"Node count: {len(is_redirect):,}")

with open(os.path.join(DATA_DIR, "is_redirect_array.bin"), "wb") as f:
    pickle.dump(is_redirect, f, protocol=pickle.HIGHEST_PROTOCOL)

cur.close()
conn.close()