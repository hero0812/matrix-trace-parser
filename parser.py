import sys

from retriever import retriever
from mapping import mapper
from database import mysqlite

print("####归总问题排行####")

global __offset, __method_stack_key
__offset = 0
__method_stack_key = ''

global offline
offline = False


def main():
    global offline
    args = sys.argv
    index_mapping = check_argv('-mapping')
    index_offline = check_argv('-offline')
    if index_offline > 0:
        offline = args[index_offline + 1]
    if index_mapping > 0:
        try:
            mappingFile = args[index_mapping + 1]
            print(mappingFile)
            mapper.set_mapping_file(mappingFile)
        except IndexError as e:
            print("Invalid param -mapping . ", e)
    mapper.init_method_map()
    retriever.retrieve(offline)
    while True:
        handle_next(3)


def show_rank():
    print("方法耗时排行###")
    result = mysqlite.rank(3)
    for i in range(0, len(result)):
        print("第%d名: 场景:%s 方法:%s 统计:%d次" % (
            i + 1,
            str(result[i][0]),
            mapper.mapping(str(result[i][1]).replace('|', '')),
            result[i][2]
        ))
    return result


def handle_next(next_step):
    global __offset
    global __method_stack_key
    if next_step == 1:
        exit(0)
    elif next_step == 2:
        __offset += 1
        next_step = show_detail(__method_stack_key, __offset)
        handle_next(next_step)
    else:
        result = show_rank()
        index = eval(input('输入编号查看方法堆栈详情 :\n'))
        __method_stack_key = result[index - 1][1]
        handle_next(2)


def show_detail(method_stack_key, offset):
    method_stack = mysqlite.query_method_stack(method_stack_key, offset)
    if len(method_stack) == 0:
        print("没有更多数据")
    else:
        mapper.parse_stack(method_stack[0])
    next_step = eval(input('输入1/2/3 :\n'))
    return next_step


def check_argv(name_of_arg):
    args = sys.argv
    for i in range(0, len(args) - 1):
        if args[i] == name_of_arg:
            print('find arg[ %s ] index %d' % (name_of_arg, i))
            return i
    return -1


if __name__ == '__main__':
    main()
