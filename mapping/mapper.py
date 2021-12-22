# 生成方法映射表
import os.path
import sys
from mapping import mapper

global __line_format

__line_format = "[%s :%s :%sms]"

global _mapping

_mapping = '/Users/antonzhang/Desktop/methodMapping.txt'

global mapping_dict
mapping_dict = {}

__NO_SUCH_METHOD = "NO_SUCH_METHOD : %s"


def set_mapping_file(file):
    global _mapping
    _mapping = file


def init_method_map():
    if not os.path.exists(_mapping):
        raise Exception('params error. methodMapping.txt must be set!')

    with open(_mapping) as mapping_file:
        for line in mapping_file:
            split_params = line.split(',')
            mapping_dict[split_params[0]] = split_params[2]

    print("mapping_dict ", len(mapping_dict))


def parse_stack(stack_trace):
    stack_array = stack_trace.split('\n')
    for i in range(0, len(stack_array) - 1):
        stack = stack_array[i]
        methods = stack.split(',')
        print((('*' * int(methods[0])) + __line_format % (mapper.mapping(methods[1]), methods[2], methods[3])))


def mapping(method_id):
    try:
        method_name = mapping_dict[method_id]
    except KeyError:
        return __NO_SUCH_METHOD % method_id
    else:
        return method_name
