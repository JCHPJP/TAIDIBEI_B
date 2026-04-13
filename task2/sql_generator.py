# sql_generator.py
# SQL生成器

from database import db


class SQLGenerator:
    """SQL生成器类"""
    
    def __init__(self, llm_client, config):
        self.llm_client = llm_client
        self.config = config
        self.schema_info = None
        self._load_schema()
    
    def _load_schema(self):
        """加载数据库表结构信息"""
        self.schema_info = db.get_table_info()
    
    def generate(self, user_query):
        """
        根据用户查询生成SQL语句
        
        Args:
            user_query: 用户查询文本
        
        Returns:
            str: 生成的SQL语句
        """
        system_prompt = SQL_SYSTEM_PROMPT.format(schema_info=self.schema_info)
        user_prompt = get_sql_user_prompt(user_query, self.schema_info)
        
        response = self.llm_client.chat_with_system(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        if response:
            # 提取SQL语句
            sql = self._extract_sql(response)
            if sql:
                return sql
        
        return None
    
    def _extract_sql(self, response):
        """
        从响应中提取SQL语句
        
        Args:
            response: 模型响应文本
        
        Returns:
            str: 提取的SQL语句
        """
        import re
        
        # 清理响应文本
        response = response.strip()
        
        # 尝试从代码块中提取
        sql_pattern = r'```sql\s*([\s\S]*?)\s*```'
        match = re.search(sql_pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 尝试匹配以SELECT开头的语句
        select_pattern = r'(SELECT\s+[\s\S]+?;)'
        match = re.search(select_pattern, response, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # 如果响应本身就是SQL
        if response.upper().startswith('SELECT'):
            return response
        
        return None
    
    def validate_sql(self, sql):
        """
        验证SQL语句是否安全（只允许SELECT）
        
        Args:
            sql: SQL语句
        
        Returns:
            bool: 是否安全
        """
        if not sql:
            return False
        
        sql_upper = sql.upper().strip()
        
        # 只允许SELECT查询
        if not sql_upper.startswith('SELECT'):
            return False
        
        # 禁止危险操作
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False
        
        return True
    
    def execute(self, sql):
        """
        执行SQL并返回结果
        
        Args:
            sql: SQL语句
        
        Returns:
            tuple: (df, columns, data) 结果的DataFrame、列名和数据
        """
        if not self.validate_sql(sql):
            raise Exception("SQL语句不安全或无效，只允许SELECT查询")
        
        try:
            df = db.execute_query_to_df(sql)
            columns, data = db.execute_query(sql)
            return df, columns, data
        except Exception as e:
            raise Exception(f"SQL执行失败: {e}")


# 全局SQL生成器实例
sql_generator = SQLGenerator()