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


# 查询累计排名前三的方法
def rank(limit=3):
    querySQL = '''select key  from TRACE limit ?'''
    args = []
    args.insert(0, limit)
    result = conn.execute(querySQL, args)
    return result.fetchall()
