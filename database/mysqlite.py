import os.path
import sqlite3
import sys

if os.path.exists('trace.db'):
    os.remove('trace.db')

conn = sqlite3.connect("trace.db")

sql = '''Create table TRACE(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date INTEGER,
    version TEXT,
    key TEXT,
    method TEXT,
    stack TEXT)'''

conn.execute(sql)


# conn.close()

def insert(x):
    insertSQL = '''insert into TRACE(key,stack,date) values(?,?,?)'''
    conn.execute(insertSQL, x)
    conn.commit()
