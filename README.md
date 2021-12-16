# matrix-trace-parser
TraceCanary 慢方法监控日志解析脚本
1.  按照筛选条件[版本号、日期] 调用服务端接口获取token拉取对应trace文件存到本地。【暂时可以写死筛选条件】
2. 本地遍历所有文件，按行读取json，stackKey作为归总依据，提取method耗时记录次数信息；为每次该method出现的位置（哪个trace文件的哪一行）建立索引。
3. 统计出method耗时排行，查看详情能一次调取对应trace文件中的json上报记录
4. 根据版本号读取mapping文件，显示解析结果