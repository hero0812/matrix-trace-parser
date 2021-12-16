#!/usr/bin/python
import json
import logging
import os
from typing import List
import requests
# 导入文件操作库
import codecs

import retriever.retriever as retriever

logger = logging.getLogger(__name__)

# 给请求指定一个请求头来模拟chrome浏览器
global headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}


def parse():
    global headers
    data = retriever.provide()
    list_size = len(data)
    for i in range(0, list_size):
        print("start parse %d", i)
        file_url = data[i]
        res = requests.get(file_url, headers=headers)
        print("res ==>", res.text)
        # data2 = json.dumps()


# 创建存放文件夹
def create_trace_dir():
    trace_dir = os.getcwd() + "\\trace\\"
    if not os.path.exists(trace_dir):
        os.mkdir(trace_dir)
    return trace_dir


# 写入文件
def write_txt(chapter, content, code):
    with codecs.open(chapter, 'a', encoding=code) as f:
        f.write(content)
