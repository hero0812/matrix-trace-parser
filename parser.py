import sys

from retriever import retriever
from mapping import mapper
from database import mysqlite

print("####归总问题排行####")


def main():
    index = check_argv('-mapping')
    if index > 0:
        try:
            args = sys.argv
            mappingFile = args[index + 1]
            print(mappingFile)
            mapper.set_mapping_file(mappingFile)
        except IndexError as e:
            print("Invalid param -mapping . ", e)
    mapper.init_method_map()
    retriever.parse()

    result = mysqlite.rank(3)
    for i in range(0, len(result)):
        print("第%d名: %s" % (i + 1, mapper.mapping(str(result[i][0]).replace('|', ''))))

    print("###输入编号查看方法堆栈详情###")
    mapper.parse_stack(result[0][0])


def check_argv(name_of_arg):
    args = sys.argv
    for i in range(0, len(args) - 1):
        if args[i] == name_of_arg is True:
            return i
    return -1


if __name__ == '__main__':
    main()
