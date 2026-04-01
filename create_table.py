import sqlite3


class FinancialDatabaseCreator:
    """财务数据库创建器"""
    def __init__(self, db_path='financial_data.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        print(f"✓ 连接到数据库: {self.db_path}")
        
    def create_all_tables(self):
        """创建所有表"""
        
        # 1. 核心业绩指标表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_performance_indicators_sheet (
                serial_number INTEGER,
                stock_code VARCHAR(20),
                stock_abbr VARCHAR(50),
                eps DECIMAL(10,4),
                total_operating_revenue DECIMAL(20,2),
                operating_revenue_yoy_growth DECIMAL(10,4),
                operating_revenue_qoq_growth DECIMAL(10,4),
                net_profit_10k_yuan DECIMAL(20,2),
                net_profit_yoy_growth DECIMAL(10,4),
                net_profit_qoq_growth DECIMAL(10,4),
                net_asset_per_share DECIMAL(10,4),
                roe DECIMAL(10,4),
                operating_cf_per_share DECIMAL(10,4),
                net_profit_excl_non_recurring DECIMAL(20,2),
                net_profit_excl_non_recurring_yoy DECIMAL(10,4),
                gross_profit_margin DECIMAL(10,4),
                net_profit_margin DECIMAL(10,4),
                roe_weighted_excl_non_recurring DECIMAL(10,4),
                report_period VARCHAR(20),
                report_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (serial_number, stock_code, report_year, report_period)
            )
        ''')
        print("✓ 创建表: core_performance_indicators_sheet")
        
        # 2. 资产负债表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_sheet (
                serial_number INTEGER,
                stock_code VARCHAR(20),
                stock_abbr VARCHAR(50),
                asset_cash_and_cash_equivalents DECIMAL(20,2),
                asset_accounts_receivable DECIMAL(20,2),
                asset_inventory DECIMAL(20,2),
                asset_trading_financial_assets DECIMAL(20,2),
                asset_construction_in_progress DECIMAL(20,2),
                asset_total_assets DECIMAL(20,2),
                asset_total_assets_yoy_growth DECIMAL(10,4),
                liability_accounts_payable DECIMAL(20,2),
                liability_advance_from_customers DECIMAL(20,2),
                liability_total_liabilities DECIMAL(20,2),
                liability_total_liabilities_yoy_growth DECIMAL(10,4),
                liability_contract_liabilities DECIMAL(20,2),
                liability_short_term_loans DECIMAL(20,2),
                asset_liability_ratio DECIMAL(10,4),
                equity_unappropriated_profit DECIMAL(20,2),
                equity_total_equity DECIMAL(20,2),
                report_period VARCHAR(20),
                report_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (serial_number, stock_code, report_year, report_period)
            )
        ''')
        print("✓ 创建表: balance_sheet")
        
        # 3. 利润表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_sheet (
                serial_number INTEGER,
                stock_code VARCHAR(20),
                stock_abbr VARCHAR(50),
                net_profit DECIMAL(20,2),
                net_profit_yoy_growth DECIMAL(10,4),
                other_income DECIMAL(20,2),
                total_operating_revenue DECIMAL(20,2),
                operating_revenue_yoy_growth DECIMAL(10,4),
                operating_expense_cost_of_sales DECIMAL(20,2),
                operating_expense_selling_expenses DECIMAL(20,2),
                operating_expense_administrative_expenses DECIMAL(20,2),
                operating_expense_financial_expenses DECIMAL(20,2),
                operating_expense_rnd_expenses DECIMAL(20,2),
                operating_expense_taxes_and_surcharges DECIMAL(20,2),
                total_operating_expenses DECIMAL(20,2),
                operating_profit DECIMAL(20,2),
                total_profit DECIMAL(20,2),
                asset_impairment_loss DECIMAL(20,2),
                credit_impairment_loss DECIMAL(20,2),
                report_period VARCHAR(20),
                report_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (serial_number, stock_code, report_year, report_period)
            )
        ''')
        print("✓ 创建表: income_sheet")
        
        # 4. 现金流量表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_flow_sheet (
                serial_number INTEGER,
                stock_code VARCHAR(20),
                stock_abbr VARCHAR(50),
                net_cash_flow DECIMAL(20,2),
                net_cash_flow_yoy_growth DECIMAL(10,4),
                operating_cf_net_amount DECIMAL(20,2),
                operating_cf_ratio_of_net_cf DECIMAL(10,4),
                operating_cf_cash_from_sales DECIMAL(20,2),
                investing_cf_net_amount DECIMAL(20,2),
                investing_cf_ratio_of_net_cf DECIMAL(10,4),
                investing_cf_cash_for_investments DECIMAL(20,2),
                investing_cf_cash_from_investment_recovery DECIMAL(20,2),
                financing_cf_cash_from_borrowing DECIMAL(20,2),
                financing_cf_cash_for_debt_repayment DECIMAL(20,2),
                financing_cf_net_amount DECIMAL(20,2),
                financing_cf_ratio_of_net_cf DECIMAL(10,4),
                report_period VARCHAR(20),
                report_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (serial_number, stock_code, report_year, report_period)
            )
        ''')
        print("✓ 创建表: cash_flow_sheet")
        
        self.conn.commit()
        print("\n✓ 所有表创建完成！")
        
    def create_indexes(self):
        """创建索引提升查询性能"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_core_stock_code ON core_performance_indicators_sheet(stock_code)",
            "CREATE INDEX IF NOT EXISTS idx_core_report_year ON core_performance_indicators_sheet(report_year)",
            "CREATE INDEX IF NOT EXISTS idx_balance_stock_code ON balance_sheet(stock_code)",
            "CREATE INDEX IF NOT EXISTS idx_balance_report_year ON balance_sheet(report_year)",
            "CREATE INDEX IF NOT EXISTS idx_income_stock_code ON income_sheet(stock_code)",
            "CREATE INDEX IF NOT EXISTS idx_income_report_year ON income_sheet(report_year)",
            "CREATE INDEX IF NOT EXISTS idx_cashflow_stock_code ON cash_flow_sheet(stock_code)",
            "CREATE INDEX IF NOT EXISTS idx_cashflow_report_year ON cash_flow_sheet(report_year)"
        ]
        
        for idx_sql in indexes:
            self.cursor.execute(idx_sql)
        
        self.conn.commit()
        print("✓ 索引创建完成")
        
    def show_tables(self):
        """显示所有表"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = self.cursor.fetchall()
        print("\n数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
            
    def show_table_schema(self, table_name):
        """显示表结构"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()
        print(f"\n表 {table_name} 的结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print("\n✓ 数据库连接已关闭")

# 使用示例
if __name__ == "__main__":
    # 创建数据库
    db_creator = FinancialDatabaseCreator('financial_data.db')
    db_creator.connect()
    
    # 创建表
    db_creator.create_all_tables()
    
    # 创建索引
    db_creator.create_indexes()
    
    # 查看表
    db_creator.show_tables()
    
    # 查看某个表的结构
    db_creator.show_table_schema('core_performance_indicators_sheet')
    
    # 关闭连接
    db_creator.close()
