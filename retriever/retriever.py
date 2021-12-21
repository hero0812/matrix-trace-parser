#!/usr/bin/python
import json
import logging
import os
from typing import List
import requests
# 导入文件操作库
import codecs

import retriever
import database.mysqlite as db

# 给请求指定一个请求头来模拟chrome浏览器
global headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/54.0.2840.99 Safari/537.36'}


def retrieve(offline_mode):
    """retrieve trace json file from qiniu server"""
    print("start retrieve offline mode %s" % offline_mode)
    if offline_mode:
        return
    global headers
    data = retriever.provide()
    list_size = len(data)

    for i in range(0, list_size):
        # print("start parse %d", i + 1)
        file_url = data[i]
        res = requests.get(file_url, headers=headers)
        # print('开始保存')
        file_name = 'temp.json'
        f = open(file_name, 'w')
        f.write(res.text)
        f.close()

        with open("temp.json", "r", encoding='utf-8') as f:
            line_mode = read_by_line(f)
            if not line_mode:
                try:
                    jsonObj = json.load(f)
                    value = jsonObj['content']
                    print("read file ==> ", jsonObj)
                    if not jsonObj['tag'] == 'Trace_EvilMethod':
                        print('not Trace_EvilMethod tag')
                        break
                    t = (value['stackKey'], value['stack'], value['time'])
                    db.insert(t)
                    os.remove('temp.json')
                except Exception as jsonError:
                    print(jsonError)


def read_by_line(f):
    line_mode = True
    while True:
        try:
            line = f.readline()
            # print("read ==> %s" % line)
            if line == '':
                # print("read ==> End")
                break
            jsonObj = json.loads(line)
            value = jsonObj['content']
        except Exception:
            print("not single line mode.")
            line_mode = False
            return line_mode
        else:
            if not jsonObj['tag'] == 'Trace_EvilMethod':
                print('not Trace_EvilMethod tag')
                continue
            if 'stackKey' not in value:
                continue
            if 'scene' not in value:
                scene = "unknown"
            else:
                scene = value['scene']
            d = {'key': value['stackKey'], 'scene': scene, 'date': value['time'],
                 'method_stack': value['stack']}
            db.insert(d)

    if line_mode:
        os.remove('temp.json')
    return line_mode
