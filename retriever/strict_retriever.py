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

# 解析StrictMode日志
global version
version = ''

global offline_mode
offline_mode = 'True'

global __locale_list_dir
__locale_list_dir = os.getcwd() + '/' + 'resources' + '/'  # 本地模式 trace文件存放位置


def provide():
    global version
    if version == '':
        raise Exception("version has not been set")
    local_list = os.listdir(__locale_list_dir + version + '/StrictMode')
    print('look up locale_list_dir %s' % local_list)
    return version, local_list


def retrieve(offline, apk_version):
    """retrieve trace json file from qiniu server"""
    global offline_mode, version
    version = apk_version
    # offline_mode = offline # StrictMode日志仅支持本地（离线）模式
    print("start retrieve offline " + offline_mode)
    data = provide()
    if version is None:
        version = data[0]
    list_size = len(data[1])
    for i in range(0, list_size):
        local_file_name = __locale_list_dir + data[0] + '/StrictMode/' + data[1][i]
        # print("start parse file: %d. %s " % (i + 1, local_file_name))
        with open(local_file_name, "r", encoding='utf-8') as f:
            read_by_line(f)

    return version


def read_by_line(f):
    line_mode = True
    while True:
        try:
            line = f.readline()
            # print("read ==> %s" % line)
            if line == '':
                # print("read ==> End")
                break
            value = json.loads(line)
        except Exception:
            print("not single line mode.")
            line_mode = False
            return line_mode
        else:
            detail_type = ''
            if not value['tag'] == 'StrictMode':
                print('not StrictMode tag')
            else:
                detail_type = 'StrictMode'

            if 'stack' not in value:
                stack = 'unknown'
            else:
                stack = value['stack']

            if 'threadStack' not in value:
                threadStack = "unknown"
            else:
                threadStack = value['threadStack']

            if 'key' not in value:
                scene = "unknown"
            else:
                scene = value['key']

            sub_type = 'unknown'
            if 'type' in value:
                sub_type = value['type']

            device_info = 'unknown'
            if 'machine' in value:
                device_info = value['machine']
            cpu_usage = ''
            if 'usage' in value:
                cpu_usage = value['usage']

            mem_total = ''
            if 'mem' in value:
                mem_total = value['mem']

            mem_free = ''
            if 'mem_free' in value:
                mem_free = value['mem_free']

            d = {'key': sub_type, 'scene': scene, 'type': detail_type, 'device_info': device_info,
                 'date': '', 'cpu_usage': cpu_usage, 'mem_total': mem_total, 'mem_free': mem_free,
                 'version': version, 'method_stack': stack,
                 'thread_stack': json.dumps(threadStack, ensure_ascii=False)}
            db.insert(d)

    return line_mode
