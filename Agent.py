import json
import sqlite3
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from multiprocessing import Pool, Manager
import time
from functools import partial
from datetime import datetime

load_dotenv()

# ==================== 配置日志 ====================
# 创建日志目录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 生成日志文件名（按日期）
log_filename = f"{log_dir}/extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),  # 输出到文件
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger(__name__)

# ==================== 配置 ====================
DB_PATH = "financial_data.db"
PROMPT_FILE = "prompt-templates.md"
MAX_PROCESSES = 20  # 进程数
# ============================================

def load_delete_keywords(file_path):
    """
    从文件加载删除关键词
    支持注释行（以#开头）和空行自动跳过
    """
    delete_keywords = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # 去除首尾空白
                line = line.strip()
                
                # 跳过空行
                if not line:
                    continue
                
                # 跳过注释行（以#开头）
                if line.startswith('#'):
                    continue
                
                # 添加到列表
                delete_keywords.append(line)
        
        print(f"✅ 加载成功，共 {len(delete_keywords)} 个关键词")
        return delete_keywords
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return []
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return []

def filter_paragraphs_by_keywords(report_text):
    """
    按关键字筛选段落
    规则：
    1. 包含保留关键字 → 保留
    2. 包含删除关键字 → 删除（优先级更高）
    3. 其他 → 默认保留
    """
    
    # ========== 1. 定义关键字 ==========
    
    # 保留关键字（明确要保留的）
    keep_keywords = [
        '主要会计数据',
        '主要财务指标',
        '非经常性损益',
        '科目变动分析表',
        '合并资产负债表',
        '合并利润表',
        '合并现金流量表',
        '母公司资产负债表',
        '母公司利润表',
        '母公司现金流量表',
        '营业收入',
        '营业成本',
        '净利润',
        '每股收益',
        '净资产收益率',
        '总资产',
        '净资产',
    ]
    
    # 删除关键字（明确要删除的冗余内容）
    delete_keywords = load_delete_keywords("delete_keywords.txt")
    # ========== 2. 按 # 分割段落 ==========
    sections = report_text.split('#')
    
    # ========== 3. 筛选段落 ==========
    kept = []
    for s in sections:
        # 跳过空段落
        if not s.strip():
            continue
        
        # 获取标题部分（第一行）
        first_line = s.split('\n')[0] if s else ''
        
        # 假设这段不是废话
        is_bad = False
        
        # 逐个检查删除关键词（只检查标题部分）
        for word in delete_keywords:
            if word in first_line:
                is_bad = True
                break
        
        # 如果是废话，跳过
        if is_bad:
            continue
        
        # 保留
        kept.append( s)
    
    result = '\n'.join(kept)
    return result


def get_client():
    """每个进程独立创建客户端"""
    return OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )


def call_llm(prompt, file_name=""):
    """调用大模型"""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的财务数据提取专家，擅长从Markdown格式的财报文件中提取结构化数据，并生成SQL INSERT语句。请严格按照JSON格式返回结果，不要包含其他解释性文字。"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            stream=False,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        content = response.choices[0].message.content.strip()
        
        # 清理JSON格式
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        result = json.loads(content)
        logger.debug(f"[{file_name}] API调用成功")
        return {"success": True, "data": result, "file": file_name}
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败: {e}"
        logger.error(f"[{file_name}] {error_msg}")
        logger.debug(f"[{file_name}] 返回内容: {content[:500]}...")  # 只记录前500字符
        return {"success": False, "error": error_msg, "file": file_name}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{file_name}] API调用失败: {error_msg}")
        return {"success": False, "error": error_msg, "file": file_name}


def save_to_db(sql_statements, db_lock, file_name=""):
    """保存到数据库（使用锁）"""
    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            cursor = conn.cursor()
            
            success_count = 0
            fail_count = 0
            
            for table_name, sql in sql_statements.items():
                if sql and sql.strip():
                    try:
                        cursor.execute(sql)
                        success_count += 1
                        logger.debug(f"[{file_name}] 成功插入表: {table_name}")
                    except Exception as e:
                        fail_count += 1
                        logger.error(f"[{file_name}] 插入失败 [{table_name}]: {e}")
                        logger.debug(f"[{file_name}] SQL语句: {sql[:200]}...")
            
            conn.commit()
            conn.close()
            
            if success_count > 0:
                logger.info(f"[{file_name}] 数据库插入完成: 成功 {success_count} 条, 失败 {fail_count} 条")
            
            return success_count, fail_count
            
        except Exception as e:
            logger.error(f"[{file_name}] 数据库连接失败: {e}")
            return 0, 0


def process_one_file(file_path, prompt_template, db_lock):
    """处理单个文件"""
    file_name = os.path.basename(file_path)
    logger.info(f"开始处理文件: {file_name}")
    
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 清洗：删除无关段落
        markdown_content = filter_paragraphs_by_keywords(markdown_content)
        
        logger.debug(f"[{file_name}] 清洗后文件大小: {len(markdown_content)} 字符")
        
        # 构建提示词
        if "{在这里粘贴你的财报 Markdown 内容}" in prompt_template:
            prompt = prompt_template.replace(
                "{在这里粘贴你的财报 Markdown 内容}",
                markdown_content
            )
        else:
            prompt = prompt_template + "\n\n" + markdown_content
        
        # 调用大模型
        result = call_llm(prompt, file_name)
        
        if not result["success"]:
            logger.error(f"[{file_name}] 处理失败: {result.get('error')}")
            return {
                "file": file_name,
                "success": False,
                "error": result.get("error", "未知错误"),
                "timestamp": datetime.now().isoformat()
            }
        
        # 保存到数据库
        data = result["data"]
        success_count, fail_count = save_to_db(data.get('sql_statements', {}), db_lock, file_name)
        
        # 记录提取的财务信息
        company_info = data.get('company_info', {})
        logger.info(f"[{file_name}] ✓ 成功提取: {company_info.get('stock_abbr', '未知')} ({company_info.get('stock_code', '未知')}) - {company_info.get('report_period', '')}{company_info.get('report_year', '')}")
        
        if data.get('extraction_notes'):
            logger.info(f"[{file_name}] 提取说明: {', '.join(data['extraction_notes'])}")
        
        return {
            "file": file_name,
            "success": True,
            "company_info": company_info,
            "extraction_notes": data.get('extraction_notes', []),
            "db_inserts": {"success": success_count, "fail": fail_count},
            "timestamp": datetime.now().isoformat()
        }
        
    except FileNotFoundError:
        error_msg = f"文件不存在: {file_path}"
        logger.error(f"[{file_name}] {error_msg}")
        return {"file": file_name, "success": False, "error": error_msg, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"[{file_name}] 处理异常: {error_msg}", exc_info=True)
        return {"file": file_name, "success": False, "error": error_msg, "timestamp": datetime.now().isoformat()}


def main():
    # 记录程序开始
    logger.info("="*60)
    logger.info("程序开始运行")
    logger.info(f"日志文件: {log_filename}")
    logger.info("="*60)
    
    try:
        # 读取提示词模板
        logger.info(f"读取提示词模板: {PROMPT_FILE}")
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        logger.info(f"提示词模板加载成功，长度: {len(prompt_template)} 字符")
    except FileNotFoundError:
        logger.error(f"找不到提示词文件: {PROMPT_FILE}")
        return
    except Exception as e:
        logger.error(f"读取提示词文件失败: {e}")
        return
    
    # 获取所有md文件
    folder_path = "processed"
    logger.info(f"扫描文件夹: {folder_path}")
    
    md_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    if not md_files:
        logger.warning(f"在 {folder_path} 下未找到任何 .md 文件")
        return
    
    logger.info(f"找到 {len(md_files)} 个Markdown文件")
    logger.info(f"使用 {MAX_PROCESSES} 个进程并发处理")
    
    # 创建进程间共享的锁
    manager = Manager()
    db_lock = manager.Lock()
    
    # 记录处理开始时间
    start_time = time.time()
    
    # 使用进程池处理
    logger.info("开始批量处理...")
    with Pool(processes=MAX_PROCESSES) as pool:
        func = partial(process_one_file, prompt_template=prompt_template, db_lock=db_lock)
        results = pool.map(func, md_files)
    
    # 计算处理时间
    elapsed_time = time.time() - start_time
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    
    # 详细统计
    total_db_inserts = sum(r.get("db_inserts", {}).get("success", 0) for r in results if r["success"])
    
    # 打印汇总
    logger.info("="*60)
    logger.info("处理完成汇总")
    logger.info("="*60)
    logger.info(f"总文件数: {len(results)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {fail_count}")
    logger.info(f"总数据库插入数: {total_db_inserts}")
    logger.info(f"总耗时: {elapsed_time:.2f} 秒")
    logger.info(f"平均每个文件耗时: {elapsed_time/len(results):.2f} 秒")
    
    # 保存结果
    summary_file = "extraction_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"汇总结果已保存到: {summary_file}")
    
    # 记录失败的文件
    if fail_count > 0:
        logger.warning("失败的文件列表:")
        for r in results:
            if not r["success"]:
                logger.warning(f"  - {r['file']}: {r.get('error', '未知错误')}")
    
    # 记录日志文件位置
    logger.info(f"详细日志已保存到: {log_filename}")
    logger.info("程序运行结束")


if __name__ == "__main__":
    main()