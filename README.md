# 题目文件
***
docs\B题-上市公司财报“智能问数”助手.pdf
***


# 任务一：构建结构化财报数据库 
***

## 📁 数据文件
| 文件 | 说明 |
|------|------|
| `data\raw\示例数据\附件2：财务报告` | 原始PDF文件 |
| `financial_data.db` | SQLite数据库文件 |
| `parsed_results` | PDF->Markdown的PDF数据解析存放地|
| `processed` | 对parsed_results的图片进行提取表格后的存放地|

## 📓 代码文件
| 文件 | 说明 | 数据流动 |
|------|------|--------|
| `01_财报解析探索.ipynb` | 测试第一问的代码 | 无 |
| `并行处理.py` | 使用MinerU镜像解析PDF（PDF→Markdown） |data\raw\示例数据\附件2：财务报告 -> parsed_results |
| `clearn_data.py` | 把图片数据转为表格（img->table)  | parsed_results-> processed|
| `create_table.py` | 创建四个表格数据 | 无 |
|  `Agent.py`| 从每个文件中获取四个表格数据 | processed-> financial_data.db|
## 📝 配置与文档
| 文件 | 说明 |
|------|------|
| `prompt-templates.md` | 提取四个数据的提示词（Text2SQL） |
| `.env` | 环境变量配置文件（存储API密钥等） |
| ` delete_keywords.txt`| 通过关键字过滤不必要的章节 |



***


# 任务二：搭建“智能问数”助手 
***

## RAG 
- [ ] 未完成
***





# 任务三：增强“智能问数”助手的可靠性
***
- [ ] 未完成
***
