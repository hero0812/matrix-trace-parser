import os.path
import sqlite3

global conn


def init(offline='False'):
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
    insertSQL = '''insert into TRACE(key,scene,type,method_stack,date,version,thread_stack) values(?,?,?,?,?,?,?)'''
    t = (x['key'], x['scene'], x['type'], x['method_stack'], x['date'], x['version'], x['thread_stack'])
    conn.execute(insertSQL, t)
    conn.commit()


# 查询方法排名
def rank(issue_type='ANR'):
    global conn
    querySQL = '''select type,scene,key ,count(key) as count from TRACE 
    where type = ? group by key order by count desc'''
    args = []
    args.insert(0, issue_type)
    result = conn.execute(querySQL, args)
    return result.fetchall()


def query_method_stack(detail_type, key, offset=0):
    global conn
    print("query_method_stack type:%s key:%s offset:%d " % (detail_type, key, offset))
    querySQL = '''select method_stack,thread_stack from TRACE where type = ? and key = ?'''
    args = []
    args.insert(0, detail_type)
    args.insert(1, key)
    result = conn.execute(querySQL, args)
    result_list = result.fetchall()
    if offset >= len(result_list):
        return {}
    else:
        return result_list[offset]


def query_version():
    global conn
    querySQL = '''select version from TRACE limit 1'''
    result = conn.execute(querySQL)
    result_list = result.fetchall()
    version_code = 0
    if len(result_list) > 0:
        version_code = result_list[0]
    print("query version :%s " % version_code)
    return version_code


if __name__ == '__main__':
    init(False)
