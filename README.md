# 课程观看嵌套记录的类型校验与列式查询

这是一个处理本地数据交换的仓湖项目。示例使用虚构机构和匿名合成记录，不连接业务平台。

## 数据契约

观看事件键全表唯一。当前写入结构固定：campus是含name、region两个非空文本的嵌套对象，seconds为非负整数，缺字段和未知字段均拒绝。实际Parquet保留嵌套STRUCT而不是JSON文本。表版本固定Schema与批次文件列表，只有显式发布后可读。

## 代码职责

- `coursecolumns/contracts.py`：嵌套字段结构和数值校验。
- `coursecolumns/columnio.py`：嵌套Parquet读写与地区查询。
- `coursecolumns/tables.py`：全表事件键与字段结构、文件清单绑定。
- `coursecolumns/storage.py`：本地事务、内容摘要和查询工具。

## 安装与运行

使用 Python 3.11。先执行 `python3 -m pip install -r requirements.txt`；依赖仅在准备环境时安装，运行与测试均可断网。

```sh
python3 -m compileall -q coursecolumns tests
python3 -m unittest discover -s tests -v
python3 -m coursecolumns
```

默认示例在独立临时目录执行，结束后删除目录。需要检查持久文件时可执行 `python3 -m coursecolumns --root state`。测试自己创建临时目录，不依赖固定端口、外部服务或其他用例顺序。

## 容器

```sh
docker build -t course-schema:local .
docker run --rm --network none course-schema:local
docker run --rm --network none course-schema:local python3 -m coursecolumns
```

容器构建负责预装锁定依赖，启动不下载包。示例输出是真实接入、查询和发布的数据，不读取预制输出。测试及示例可分别运行，退出码非零表示失败。

## 交换口径

进一步的字段含义、范围及兼容边界见 `docs/data-contract.md`。
