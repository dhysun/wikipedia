import mysql.connector
import pickle
import os

HOST = "localhost"
USER = "root"
PASSWORD = "password" # This would be replaced with actual password
DATABASE = "data" # This is the name of the database

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

conn = mysql.connector.connect(host=HOST, user=USER,
                                password=PASSWORD, database=DATABASE)

# Retrieves the page_is_redirect column of page
cur = conn.cursor()
cur.execute("SELECT page_is_redirect FROM page ORDER BY page_id")

# Creates a bytearray to store the redirect status of each page
# 1 for redirect, 0 for non-redirect
is_redirect = bytearray()

# Appends the redirect status of each page to the bytearray
for (redirect,) in cur:
    is_redirect.append(redirect)

# Write the data to a binary file using pickle
with open(os.path.join(DATA_DIR, "is_redirect_array.bin"), "wb") as f:
    pickle.dump(is_redirect, f, protocol=pickle.HIGHEST_PROTOCOL)

cur.close()
conn.close()