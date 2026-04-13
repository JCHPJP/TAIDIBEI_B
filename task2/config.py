# config.py
import os

class Config:
    # 数据库配置
    DB_PATH = "db/financial_data.db"
    
    # 本地DeepSeek模型配置
    LLM_API_URL = "http://localhost:11434/api/generate"  # Ollama
    MODEL_NAME = "deepseek-coder:7b"  # 或你的模型名
    
    # 输出配置
    RESULT_FOLDER = "result"
    OUTPUT_EXCEL = "result_2.xlsx"

    # 线程配置
    MAX_WORKERS = 5
    
    # 66家中药公司映射（根据附件1补充）
    COMPANY_MAPPING = {
        "金花股份": "600080",
        "华润三九": "000999",
        "华润双鹤": "600062",
        "白云山": "600332",
        "云南白药": "000538",
        "片仔癀": "600436",
        "千金药业": "600479",
        "香雪制药": "300147",
        "三金": "002275",  # 桂林三金
        "同仁堂": "600085",
        "东阿阿胶": "000423",
        "以岭药业": "002603",
        "天士力": "600535",
        "康缘药业": "600557",
        "步长制药": "603858",
        "济川药业": "600566",
        "太极集团": "600129",
        "江中药业": "600750",
        "马应龙": "600993",
        "健民集团": "600976",
        "九芝堂": "000989",
        "仁和药业": "000650",
        "葵花药业": "002737",
        "红日药业": "300026",
        "康恩贝": "600572",
        "西藏药业": "600211",
        "益佰制药": "600594",
        "神奇制药": "600613",
        "沃华医药": "002107",
        "龙津药业": "002750",
        "大理药业": "603963",
        "启迪药业": "000590",
        "特一药业": "002728",
        "众生药业": "002317",
        "精华制药": "002349",
        "贵州百灵": "002424",
        "信邦制药": "002390",
        "益盛药业": "002566",
        "太安堂": "002433",
        "嘉应制药": "002198",
        "方盛制药": "603998",
        "灵康药业": "603669",
        "赛隆药业": "002898",
        "华森制药": "002907",
        "新天药业": "002873",
        "盘龙药业": "002864",
        "易明医药": "002826",
        "卫信康": "603676",
        "奥赛康": "002755",
        "誉衡药业": "002437",
        "仟源医药": "300254",
        "舒泰神": "300204",
        "康芝药业": "300086",
        "振东制药": "300158",
        "福瑞股份": "300049",
        "佐力药业": "300181",
        "上海凯宝": "300039",
        "金石亚药": "300434",
        "陇神戎发": "300534",
        "新光药业": "300519",
        "维康药业": "300878",
        "华神科技": "000790",
        "广誉远": "600771",
        "中恒集团": "600252",
        "昆药集团": "600422",
        "桂林三金": "002275",
    }
    
    # 反向映射：股票代码 -> 公司简称
    CODE_TO_NAME = {v: k for k, v in COMPANY_MAPPING.items()}
    
    # 财务指标映射
    INDICATOR_MAPPING = {
        # 核心业绩指标
        "营收": "total_operating_revenue",
        "营业收入": "total_operating_revenue",
        "营业总收入": "total_operating_revenue",
        "利润总额": "total_profit",
        "净利润": "net_profit",
        "归母净利润": "net_profit_parent",
        "扣非净利润": "deducted_net_profit",
        "每股收益": "basic_eps",
        "净资产收益率": "roe",
        
        # 利润表
        "营业成本": "operating_cost",
        "销售费用": "sales_expense",
        "管理费用": "admin_expense",
        "财务费用": "financial_expense",
        "研发费用": "rd_expense",
        
        # 资产负债表
        "资产总计": "total_assets",
        "总资产": "total_assets",
        "负债合计": "total_liabilities",
        "总负债": "total_liabilities",
        "股东权益": "owner_equity",
        "货币资金": "cash_and_cash_equivalents",
        "应收账款": "accounts_receivable",
        "存货": "inventory",
        "短期借款": "short_term_borrowings",
        
        # 现金流量表
        "经营性现金流": "cash_flow_operating",
        "投资性现金流": "cash_flow_investing",
        "筹资性现金流": "cash_flow_financing",
    }
    
    # 表结构
    TABLE_SCHEMA = {
        "core_performance_indicators_sheet": {
            "fields": [
                "stock_code", "report_date", "total_operating_revenue", 
                "total_profit", "net_profit", "net_profit_parent",
                "deducted_net_profit", "basic_eps", "roe"
            ],
            "description": "核心业绩指标表"
        },
        "income_sheet": {
            "fields": [
                "stock_code", "report_date", "operating_revenue", 
                "operating_cost", "sales_expense", "admin_expense",
                "financial_expense", "rd_expense", "operating_profit", 
                "total_profit", "net_profit"
            ],
            "description": "利润表"
        },
        "balance_sheet": {
            "fields": [
                "stock_code", "report_date", "total_assets", 
                "total_liabilities", "owner_equity", "cash_and_cash_equivalents",
                "accounts_receivable", "inventory", "short_term_borrowings",
                "long_term_borrowings", "fixed_assets"
            ],
            "description": "资产负债表"
        },
        "cash_flow_sheet": {
            "fields": [
                "stock_code", "report_date", "cash_flow_operating",
                "cash_flow_investing", "cash_flow_financing", 
                "free_cash_flow", "ending_cash_balance"
            ],
            "description": "现金流量表"
        }
    }