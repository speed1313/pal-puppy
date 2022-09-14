import os
import sqlite3
from flask import g

con = sqlite3.connect('example.db')

cur = con.cursor()

# Create table
cur.execute('''CREATE TABLE IF NOT EXISTS STOCKS (NAME CHAR NOT NULL, UID INTEGER NOT NULL PRIMARY KEY)''')
data = ("speed", 14)
# Insert a row of data
try:
    cur.execute("INSERT INTO STOCKS VALUES (?, ?)", data)
except sqlite3.IntegrityError as e:
    print(e)
# Save (commit) the changes
con.commit()

print(cur.execute('''SELECT * FROM STOCKS''').fetchall())
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()