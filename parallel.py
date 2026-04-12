import os
import subprocess
import shutil
import logging
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import threading
import os 

# ===== 设置环境变量（必须在导入其他库之前） =====
# 限制每个进程的OpenMP线程数，避免线程爆炸
cpu_cores = cpu_count()
omp_threads = min(2, cpu_cores)  # 每个magic-pdf进程最多使用2个CPU线程
os.environ['OMP_NUM_THREADS'] = str(omp_threads)
os.environ['MKL_NUM_THREADS'] = str(omp_threads)
os.environ['OPENBLAS_NUM_THREADS'] = str(omp_threads)
os.environ['VECLIB_MAXIMUM_THREADS'] = str(omp_threads)

# ===== 配置 =====
PDF_ROOT = Path.cwd() / 'data' / 'raw' / '示例数据' / '附件2：财务报告'
OUTPUT_ROOT = Path.cwd() / 'parsed_results'
LOG_DIR = Path.cwd() / 'logs'

# 根据GPU和CPU情况调整并发数
# RTX 4080建议从2-3开始测试
MAX_WORKERS = 3  # 并发进程数
# ================

# 创建目录
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志（线程安全）
log_file = LOG_DIR / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 线程锁，用于保护共享资源
file_lock = threading.Lock()

def safe_log(level, message):
    """线程安全的日志记录"""
    with file_lock:
        getattr(logging, level)(message)

def process_pdf(pdf_path):
    """处理单个PDF并自动移动文件"""
    thread_name = threading.current_thread().name
    
    try:
        # 提取信息
        company = pdf_path.parent.name
        pdf_name = pdf_path.stem
        
        # 创建目标目录（使用锁避免并发创建冲突）
        target_dir = OUTPUT_ROOT / company
        images_dir = target_dir / "images"
        
        with file_lock:
            target_dir.mkdir(parents=True, exist_ok=True)
            images_dir.mkdir(parents=True, exist_ok=True)
        
        safe_log('info', f"[{thread_name}] 处理: {pdf_path.name}")
        
        # 为每个子进程设置独立的环境变量，避免线程竞争
        env = os.environ.copy()
        # 每个子进程只使用1个线程，避免嵌套并行导致性能下降
        env['OMP_NUM_THREADS'] = '1'
        env['MKL_NUM_THREADS'] = '1'
        env['OPENBLAS_NUM_THREADS'] = '1'
        
        # 运行magic-pdf命令
        cmd = ["magic-pdf", "pdf-command", "--pdf", str(pdf_path), "--method", "auto"]
        
        # 执行命令，传入自定义环境变量
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, env=env)
        
        if result.returncode == 0:
            # 查找临时目录中的结果
            tmp_dir = Path(f"/tmp/magic-pdf/{pdf_name}/auto")
            
            if tmp_dir.exists():
                # 移动markdown文件
                md_files = list(tmp_dir.glob("*.md"))
                for md in md_files:
                    with file_lock:
                        shutil.move(str(md), str(target_dir / md.name))
                    safe_log('info', f"[{thread_name}]   📄 移动: {md.name}")
                
                # 移动json文件
                json_files = list(tmp_dir.glob("*.json"))
                for json in json_files:
                    with file_lock:
                        shutil.move(str(json), str(target_dir / json.name))
                    safe_log('info', f"[{thread_name}]   📊 移动: {json.name}")
                
                # 移动图片
                img_dir = tmp_dir / "images"
                if img_dir.exists():
                    jpg_count = 0 
                    for img in img_dir.glob("*.jpg"):
                        with file_lock:
                            shutil.move(str(img), str(images_dir / img.name))
                        jpg_count += 1
                    safe_log('info', f"[{thread_name}]   🖼️  移动图片: {jpg_count}张")
                    
                    with file_lock:
                        if img_dir.exists():
                            try:
                                img_dir.rmdir()  # 删除空目录
                            except OSError:
                                pass  # 目录可能非空，忽略
                
                # 清理临时目录
                with file_lock:
                    if tmp_dir.parent.exists():
                        try:
                            shutil.rmtree(tmp_dir.parent)
                        except OSError:
                            pass
                
                safe_log('info', f"[{thread_name}]   ✅ 完成: {pdf_name}")
                return True, pdf_path.name
            else:
                safe_log('warning', f"[{thread_name}]   ⚠️ 未找到临时目录: {tmp_dir}")
                return False, pdf_path.name
        else:
            safe_log('error', f"[{thread_name}]   ❌ 处理失败: {pdf_path.name}")
            if result.stderr:
                safe_log('error', f"[{thread_name}]      错误: {result.stderr[:200]}")
            return False, pdf_path.name
            
    except subprocess.TimeoutExpired:
        safe_log('error', f"[{thread_name}]   ⏰ 超时: {pdf_path.name}")
        return False, pdf_path.name
    except Exception as e:
        safe_log('error', f"[{thread_name}]   💥 异常: {pdf_path.name}, {str(e)}")
        return False, pdf_path.name

def main():
    # 查找所有PDF
    all_pdfs = list(PDF_ROOT.rglob("*.pdf"))
    total = len(all_pdfs)
    
    if total == 0:
        logging.warning(f"未找到PDF文件！路径: {PDF_ROOT}")
        return
    
    logging.info("="*60)
    logging.info(f"🚀 开始并行处理，共 {total} 个PDF文件")
    logging.info(f"📁 输出目录: {OUTPUT_ROOT}")
    logging.info(f"📄 日志文件: {log_file}")
    logging.info(f"⚡ 并发数: {MAX_WORKERS}")
    logging.info(f"💻 CPU核心数: {cpu_count()}")
    logging.info(f"🔧 OpenMP线程限制: {os.environ.get('OMP_NUM_THREADS', '未设置')}")
    logging.info("="*60)
    
    success = 0
    failed = 0
    start_time = time.time()
    
    # 使用线程池处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_pdf = {executor.submit(process_pdf, pdf): pdf for pdf in all_pdfs}
        
        # 处理完成的任务
        for i, future in enumerate(as_completed(future_to_pdf), 1):
            pdf = future_to_pdf[future]
            try:
                result, name = future.result()
                if result:
                    success += 1
                else:
                    failed += 1
                
                # 每5个文件或完成时打印进度
                if i % 5 == 0 or i == total:
                    progress = i/total*100
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0
                    remaining = (total - i) / rate if rate > 0 else 0
                    
                    logging.info(f"📊 进度: {i}/{total} ({progress:.1f}%) | "
                               f"成功: {success} | 失败: {failed} | "
                               f"速度: {rate:.2f}个/秒 | 预计剩余: {remaining:.0f}秒")
                    
            except Exception as e:
                logging.error(f"任务执行异常: {pdf.name}, {str(e)}")
                failed += 1
    
    # 统计
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    logging.info("\n" + "="*60)
    logging.info(f"✅ 全部处理完成！")
    logging.info(f"📊 统计:")
    logging.info(f"   总文件: {total}")
    logging.info(f"   成功: {success}")
    logging.info(f"   失败: {failed}")
    logging.info(f"   成功率: {success/total*100:.1f}%")
    logging.info(f"   用时: {hours}小时{minutes}分钟{seconds}秒")
    logging.info(f"📁 结果目录: {OUTPUT_ROOT}")
    logging.info(f"📄 日志文件: {log_file}")
    logging.info("="*60)

if __name__ == "__main__":
    main()