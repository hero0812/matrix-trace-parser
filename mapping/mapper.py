"""生成方法映射表"""

import os.path
import sys
from pprint import pprint

from mapping import mapper
from retriever import retriever

global __line_format
__line_format = "[%s\t%s:%sms]"

global _mapping, _mapping_path
_mapping = None
_mapping_path = None

global mapping_dict
mapping_dict = {}

__NO_SUCH_METHOD = "NO_SUCH_METHOD : %s"


def set_mapping_file(file):
    global _mapping
    _mapping = file


def set_version_code(version):
    global _mapping_path
    _mapping_path = os.getcwd() + '/methodMapping/' + version + '/methodMapping.txt'
    if not os.path.exists(_mapping_path):
        # 本地没有mapping文件尝试从server下载
        mapping_server_url = 'http://download.ngrok.mangatoon.mobi:8091/production/mangatoon/' \
                             + version \
                             + '/portuguese/mapping/mangatoon_portugueseRelease/methodMapping.txt'
        result = retriever.get(mapping_server_url)
        print("download mapping from %s" % mapping_server_url)
        print("download result ==> %s" % result)
        f = open(_mapping_path, 'w')
        f.write(result.text)
        f.close()


def init_method_map():
    global _mapping
    if _mapping is None:
        _mapping = _mapping_path
    if not os.path.exists(_mapping):
        raise Exception('params error. methodMapping.txt must be set!')

    print("init method map with : %s" % _mapping)
    with open(_mapping) as mapping_file:
        for line in mapping_file:
            split_params = line.split(',')
            mapping_dict[split_params[0]] = split_params[2]


def parse_stack(method_trace):
    print('方法堆栈堆栈信息:')
    if method_trace is None:
        print('no available information.')
        return

    if method_trace != 'unknown':
        stack_array = method_trace.split('\n')
        for i in range(0, len(stack_array) - 1):
            stack = stack_array[i]
            methods = stack.split(',')
            line = ('-' * (int(methods[0]) - 1)) + ('*' * int(methods[0])) + __line_format % (
                mapper.mapping(methods[1]), methods[2], methods[3])
            print(line)
    else:
        print('no available information.')


def mapping(method_id):
    try:
        method_name = mapping_dict[method_id]
    except KeyError:
        return __NO_SUCH_METHOD % method_id
    else:
        return str(method_name).replace('\n', '')
