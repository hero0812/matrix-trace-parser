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

global version
version = ''

global offline_mode
offline_mode = 'False'

# mock server data
__list = ['https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-15/6989878/1639561460445.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-15/6989878/1639562298347.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-16/4386863/1639627806674.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-17/6989878/1639733371899.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-19/13425149/1639870679225.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-20/6989878/1639970265920.json',
          'https://cn.e.pic.mangatoon.mobi/client/data/2.06.03/8046/2021-12-21/985e7355/1640073150725.json']

global __locale_list_dir
__locale_list_dir = os.getcwd() + '/' + 'resources' + '/'  # 本地模式 trace文件存放位置


def provide():
    global version
    if offline_mode == 'True':
        local_list = os.listdir(__locale_list_dir + version)
        print('look up locale_list_dir %s' % local_list)
        return version, local_list
    else:
        # get through api , not supported yet
        version_code = parse_version_code(__list[0])
        return version_code, __list


def parse_version_code(file_url):
    global version
    url_segments = file_url.split('/')
    data_index = url_segments.index('data')
    if data_index < 0:
        return version
    if data_index + 2 >= len(url_segments):
        return version
    versionCode = url_segments[data_index + 1] + '.' + url_segments[data_index + 2]
    print("parseVersionCode %s", versionCode)
    return versionCode


def retrieve(offline, apk_version):
    """retrieve trace json file from qiniu server"""
    global offline_mode, version
    version = apk_version
    offline_mode = offline
    print("start retrieve offline " + offline_mode)
    data = provide()
    if version is None:
        version = data[0]
    list_size = len(data[1])
    if offline_mode == 'False':
        for i in range(0, list_size):
            file_url = data[1][i]
            # print("start parse url :%d. %s " % (i + 1, file_url))
            res = get(file_url)
            file_name = 'temp.json'
            f = open(file_name, 'w')
            f.write(res.text)
            f.close()
            with open("temp.json", "r", encoding='utf-8') as f:
                read_by_line(f)
    else:
        for i in range(0, list_size):
            local_file_name = __locale_list_dir + data[0] + '/' + data[1][i]
            # print("start parse file: %d. %s " % (i + 1, local_file_name))
            with open(local_file_name, "r", encoding='utf-8') as f:
                read_by_line(f)
    return version


def get(file_url):
    return requests.get(file_url, headers=headers)


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
            if 'threadStack' not in value:
                threadStack = "No available thread stack information."
            else:
                threadStack = value['threadStack']
            if 'scene' not in value:
                scene = "unknown"
            else:
                scene = value['scene']
            d = {'key': value['stackKey'], 'scene': scene, 'type': value['detail'], 'date': value['time'],
                 'version': version, 'method_stack': value['stack'], 'thread_stack': threadStack}
            db.insert(d)

    return line_mode
