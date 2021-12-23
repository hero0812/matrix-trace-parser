import os.path
import sqlite3

global conn


def init(offline):
    global conn
    if os.path.exists('trace.db'):
        if offline == 'True':
            conn = sqlite3.connect("trace.db")
        else:
            os.remove('trace.db')
            create_db_conn()
    else:
        create_db_conn()


def create_db_conn():
    global conn
    conn = sqlite3.connect("trace.db")
    sql = '''Create table TRACE(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date INTEGER,
                     scene TEXT,
                     type TEXT,
                     version TEXT,
                     key TEXT,
                     method_stack TEXT,
                     thread_stack TEXT)'''
    conn.execute(sql)


def insert(x):
    global conn
    insertSQL = '''insert into TRACE(key,scene,type,method_stack,date,thread_stack) values(?,?,?,?,?,?)'''
    t = (x['key'], x['scene'], x['type'], x['method_stack'], x['date'], x['thread_stack'])
    conn.execute(insertSQL, t)
    conn.commit()


# 查询累计排名前三的方法
def rank(issue_type='ANR'):
    global conn
    querySQL = '''select type,scene,key ,count(key) as count from TRACE 
    where type = ? group by key order by count desc'''
    args = []
    args.insert(0, issue_type)
    result = conn.execute(querySQL, args)
    return result.fetchall()


def query_method_stack(key, offset=0):
    global conn
    print("query_method_stack_detail key:%s offset:%d " % (key, offset))
    querySQL = '''select method_stack,thread_stack from TRACE where key = ?'''
    args = []
    args.insert(0, key)
    result = conn.execute(querySQL, args)
    result_list = result.fetchall()
    if offset >= len(result_list):
        return {}
    else:
        return result_list[offset]


if __name__ == '__main__':
    init(False)
