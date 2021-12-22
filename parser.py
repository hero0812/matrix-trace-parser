# /usr/bin/env python
"""matrix trace解析脚本"""

import sys

from retriever import retriever
from mapping import mapper
from database import mysqlite

global __offset, __method_stack_key
__offset = -1
__method_stack_key = ''


def main():
    print("####start main####")
    args = sys.argv
    index_mapping = check_argv('-mapping')
    index_offline = check_argv('-offline')
    offline = False
    if index_offline > 0:
        offline = args[index_offline + 1]
        print("arg offline %s" % offline)
    if index_mapping > 0:
        try:
            mappingFile = args[index_mapping + 1]
            print("arg mappingFile %s" % mappingFile)
            mapper.set_mapping_file(mappingFile)
        except IndexError as e:
            print("Invalid param -mapping . " % e)
    mysqlite.init(offline)
    mapper.init_method_map()
    retriever.retrieve(offline)
    while True:
        handle_next(3)


def show_rank(issue_type):
    print("方法统计排行###")
    result = mysqlite.rank(issue_type)
    if len(result) == 0:
        print("本地数据库没有数据～")
        return None
    for i in range(0, len(result)):
        print("第%d名: 类型:%s 方法:%s 统计:%d次" % (
            i + 1,
            result[i][0],
            mapper.mapping(str(result[i][2]).replace('|', '')),
            result[i][3]
        ))
    return result


def handle_next(next_step):
    print("####handle_next %d" % next_step)
    global __offset
    global __method_stack_key
    if next_step == 1:
        exit(0)
    elif next_step == 2:
        __offset += 1
        next_step = show_detail(__method_stack_key, __offset)
        handle_next(next_step)
    else:
        type_num = eval(input('输入要查看issue类型：1. ANR、2. 普通慢方法:\n'))
        type_str = 'ANR'
        if type_num == 1:
            type_str = 'ANR'
        elif type_num == 2:
            type_str = 'NORMAL'

        result = show_rank(type_str)
        if result is None:
            handle_next(1)
        index = eval(input('输入编号查看方法堆栈详情 :\n'))
        __method_stack_key = result[index - 1][2]
        __offset = -1
        handle_next(2)


def show_detail(method_stack_key, offset):
    method_stack = mysqlite.query_method_stack(method_stack_key, offset)
    if len(method_stack) == 0:
        print("没有更多数据")
    else:
        mapper.parse_stack(method_stack)
    next_step = eval(input('输入1/2/3 :\n'))
    return next_step


def check_argv(name_of_arg):
    args = sys.argv
    for i in range(0, len(args) - 1):
        if args[i] == name_of_arg:
            return i
    return -1


if __name__ == '__main__':
    main()
