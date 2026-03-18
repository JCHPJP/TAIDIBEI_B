#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime

# ===== 配置 =====
PDF_ROOT = Path("/root/TAIDIBEI_B/data/raw/示例数据/附件2：财务报告")
OUTPUT_ROOT = Path("/root/TAIDIBEI_B/parsed_results")
LOG_DIR = Path("/root/TAIDIBEI_B/logs")
# ================

# 创建目录
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志
log_file = LOG_DIR / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def process_pdf(pdf_path):
    """处理单个PDF并自动移动文件"""
    
    # 提取信息
    company = pdf_path.parent.name  # reports-上交所 或 reports-深交所
    pdf_name = pdf_path.stem  # 不带后缀的文件名
    
    # 创建目标目录
    target_dir = OUTPUT_ROOT / company
    images_dir = target_dir / "images"


    target_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info(f"处理: {pdf_path.name}")
    logging.info(f"目标: {target_dir}")
    
    # 运行magic-pdf命令
    cmd = ["magic-pdf", "pdf-command", "--pdf", str(pdf_path), "--method", "auto"]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            # 查找临时目录中的结果
            tmp_dir = Path(f"/tmp/magic-pdf/{pdf_name}/auto")
            
            if tmp_dir.exists():
                # 移动markdown文件
                md_files = list(tmp_dir.glob("*.md"))
                for md in md_files:
                    shutil.move(str(md), str(target_dir / md.name))
                    logging.info(f"  📄 移动: {md.name}")
                
                # 移动json文件
                json_files = list(tmp_dir.glob("*.json"))
                for json in json_files:
                    shutil.move(str(json), str(target_dir / json.name))
                    logging.info(f"  📊 移动: {json.name}")
                
                # 移动图片
                img_dir = tmp_dir / "images"
                if img_dir.exists():
                    jpg_count = 0 
                    for img in img_dir.glob("*.jpg"):
                        shutil.move(str(img), str(images_dir / img.name))
                        jpg_count += 1
                    logging.info(f"  🖼️  移动图片: {jpg_count}张")
                    img_dir.rmdir()  # 删除空目录
                
                if tmp_dir.parent.exists():
                    shutil.rmtree(tmp_dir.parent) 
                    logging.info(f"  🗑️ 清理临时目录: {tmp_dir.parent}")
                
                logging.info(f"  ✅ 完成: {pdf_name}")
                return True
            else:
                logging.warning(f"  ⚠️ 未找到临时目录: {tmp_dir}")
                return False
        else:
            logging.error(f"  ❌ 处理失败: {pdf_path.name}")
            if result.stderr:
                logging.error(f"     错误: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error(f"  ⏰ 超时: {pdf_path.name}")
        return False
    except Exception as e:
        logging.error(f"  💥 异常: {pdf_path.name}, {str(e)}")
        return False

def main():
    # 查找所有PDF
    all_pdfs = list(PDF_ROOT.rglob("*.pdf"))
    logging.info(f"="*60)
    logging.info(f"🚀 开始处理，共 {len(all_pdfs)} 个PDF文件")
    logging.info(f"📁 输出目录: {OUTPUT_ROOT}")
    logging.info(f"📄 日志文件: {log_file}")
    logging.info(f"="*60)
    
    success = 0
    failed = 0
    start_time = time.time()
    
    for i, pdf in enumerate(all_pdfs, 1):
        logging.info(f"\n[{i}/{len(all_pdfs)}] 进度: {i/len(all_pdfs)*100:.1f}%")
        
        if process_pdf(pdf):
            success += 1
        else:
            failed += 1
        
        # 每5个文件休息一下
        if i % 5 == 0 and i < len(all_pdfs):
            logging.info(f"⏸️  已处理 {i} 个，休息3秒...")
            time.sleep(3)
    
    # 统计
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    logging.info("\n" + "="*60)
    logging.info(f"✅ 全部处理完成！")
    logging.info(f"📊 统计:")
    logging.info(f"   总文件: {len(all_pdfs)}")
    logging.info(f"   成功: {success}")
    logging.info(f"   失败: {failed}")
    logging.info(f"   用时: {hours}小时{minutes}分钟{seconds}秒")
    logging.info(f"📁 结果目录: {OUTPUT_ROOT}")
    logging.info(f"📄 日志文件: {log_file}")
    logging.info("="*60)

if __name__ == "__main__":
    main()