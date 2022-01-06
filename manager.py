# /usr/bin/env python
"""matrix trace解析脚本"""
import json
import sys

from retriever import retriever
from retriever import strict_retriever
from mapping import mapper
from database import mysqlite

global __offset, __method_stack_key
__offset = -1
__method_stack_key = ''

global type_str
type_str = 'ANR'

global offline, apk_version
offline = 'True'
apk_version = '2.06.04.8080'


def main():
    global offline, apk_version
    print("####start main####")
    args = sys.argv
    index_mapping = check_argv('-mappingFile')
    index_offline = check_argv('-offlineMode')
    index_version = check_argv('-apkVersion')

    if index_version > 0:
        apk_version = args[index_version + 1]
        print("arg apk_version %s" % apk_version)
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

    while True:
        handle_next(3)


def show_rank(issue_type):
    print("方法统计排行###")
    result = mysqlite.rank(issue_type)
    if len(result) == 0:
        print("没有数据～")
        return None
    for i in range(0, len(result)):
        print("第%d名: 场景:%s 方法:%s 统计:%d次" % (
            i + 1,
            result[i][1],
            mapper.mapping(str(result[i][2]).replace('|', '')),
            result[i][3]
        ))
    return result


def init_retriever(event_type):
    global offline, apk_version
    if event_type == 'StrictMode':
        version_code = strict_retriever.retrieve(offline, apk_version)
    else:
        version_code = retriever.retrieve(offline, apk_version)
        mapper.set_version_code(version_code)  # 应该做成元组，支持多个版本号
        mapper.init_method_map()


def handle_next(next_step):
    global __offset
    global __method_stack_key
    global type_str
    if next_step == 1:
        exit(0)
    elif next_step == 2:
        __offset += 1
        next_step = show_detail(type_str, __method_stack_key, __offset)
        handle_next(next_step)
    elif next_step == 4:
        __offset += 10
        next_step = show_detail(type_str, __method_stack_key, __offset)
        handle_next(next_step)
    elif next_step == 5:
        __offset -= 10
        next_step = show_detail(type_str, __method_stack_key, __offset)
        handle_next(next_step)
    elif next_step == 3:
        mysqlite.init()
        type_num = handle_input('输入要查看issue类型：1. ANR、2. 普通慢方法: 3.StrictMode\n', (1, 2, 3))
        if type_num == 1:
            type_str = 'ANR'
        elif type_num == 2:
            type_str = 'NORMAL'
        elif type_num == 3:
            type_str = 'StrictMode'

        init_retriever(type_str)
        result = show_rank(type_str)
        if len(result) == 0:
            print('no available information.')
            handle_next(3)
            return
        gen = (n for n in range(1, len(result) + 1))
        index = handle_input('输入编号查看方法堆栈详情 :\n', tuple(gen))
        __method_stack_key = result[index - 1][2]
        __offset = -1
        handle_next(2)


def show_thread_stack_info(thread_stack_str):
    print('UI线程堆栈信息:')
    if thread_stack_str is None:
        print('no available information.')
        return

    if thread_stack_str != 'unknown':
        thread_stack_array = thread_stack_str.split('\n')
        for i in range(0, len(thread_stack_array) - 1):
            print('-> %s' % thread_stack_array[i])
    else:
        print('no available information.')


def show_device_info(device_info=None, cpu_info=None, mem_info_total=None, mem_info_free=None):
    print('设备信息:')
    print('device_info: %s' % device_info)
    print('cpu_info: %s' % cpu_info)
    print('mem_info：[total:%s free: %s]' % (mem_info_total, mem_info_free))


def show_strict_mode_thread_stack(thread_stack_str):
    print('UI线程堆栈信息:')
    if thread_stack_str is None:
        print('no available information.')
        return

    if thread_stack_str != 'unknown':
        thread_stack_list = json.loads(thread_stack_str)
        for method_info in thread_stack_list:
            print('-> %s#%s ' % (method_info['className'], method_info['methodName']))
    else:
        print('no available information.')


# 非法输入容错处理
def handle_input(tip, tuple_choices):
    input_next_step = -1
    while True:
        try:
            # do next
            input_next_step = eval(input(tip))
        except Exception:
            pass
        finally:
            if input_next_step in tuple_choices:
                return input_next_step
            else:
                print('别瞎按,请输入正确的指令 ')


def show_detail(detail_type, method_stack_key, offset):
    result_tuple = mysqlite.query_method_stack(detail_type, method_stack_key, offset)

    if result_tuple is not None:
        # scene
        print('场景:%s ' % result_tuple[6])

        # parse method stack
        method_stack = result_tuple[0]
        mapper.parse_stack(method_stack)

        # show thread stack
        thread_stack_str = result_tuple[1]
        if 'StrictMode' == detail_type:
            show_strict_mode_thread_stack(thread_stack_str)
        else:
            show_thread_stack_info(thread_stack_str)

        # show cpu & memory info
        show_device_info(result_tuple[2], result_tuple[3], result_tuple[4], result_tuple[5])
    else:
        print("没有更多数据~")

    return handle_input('输入1:exit 2:下一个 3:返回上一步 4:下一页 5:上一页\n', (1, 2, 3, 4, 5))


def check_argv(name_of_arg):
    args = sys.argv
    for i in range(0, len(args) - 1):
        if args[i] == name_of_arg:
            return i
    return -1


if __name__ == '__main__':
    main()
