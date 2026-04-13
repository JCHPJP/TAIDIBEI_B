# output_formatter.py
# 输出格式化器

import pandas as pd


class OutputFormatter:
    """输出格式化器类"""
    
    def __init__(self):
        self.max_rows = 20  # 最大显示行数
        self.max_col_width = 50  # 最大列宽
    
    def format_query_result(self, columns, data, limit=20):
        """
        格式化查询结果
        
        Args:
            columns: 列名列表
            data: 数据行列表
            limit: 最大显示行数
        
        Returns:
            str: 格式化后的表格字符串
        """
        if not columns or not data:
            return "查询结果为空。"
        
        # 限制显示行数
        display_data = data[:limit]
        
        # 创建DataFrame用于展示
        df = pd.DataFrame(display_data, columns=columns)
        
        # 格式化输出
        output = []
        output.append(f"查询成功！共找到 {len(data)} 条记录：")
        output.append("")
        
        # 转换为表格字符串
        table_str = df.to_string(index=False)
        output.append(table_str)
        
        if len(data) > limit:
            output.append(f"\n(仅显示前{limit}条，共{len(data)}条)")
        
        return "\n".join(output)
    
    def format_analysis_result(self, analysis_text, query_result=None):
        """
        格式化分析结果
        
        Args:
            analysis_text: 分析文本
            query_result: 查询结果数据
        
        Returns:
            str: 格式化后的分析结果
        """
        output = []
        output.append("=" * 50)
        output.append("📊 数据分析报告")
        output.append("=" * 50)
        output.append("")
        output.append(analysis_text)
        output.append("")
        output.append("=" * 50)
        
        return "\n".join(output)
    
    def format_visualize_result(self, chart_path, description=""):
        """
        格式化可视化结果
        
        Args:
            chart_path: 图表文件路径
            description: 图表描述
        
        Returns:
            str: 格式化后的可视化结果
        """
        output = []
        output.append("📈 图表已生成")
        output.append("-" * 30)
        if description:
            output.append(f"说明：{description}")
        output.append(f"保存路径：{chart_path}")
        output.append("")
        output.append("提示：请在 result 目录下查看生成的图表文件。")
        
        return "\n".join(output)
    
    def format_error(self, error_message):
        """
        格式化错误信息
        
        Args:
            error_message: 错误信息
        
        Returns:
            str: 格式化后的错误信息
        """
        output = []
        output.append("❌ 操作失败")
        output.append("-" * 30)
        output.append(f"错误信息：{error_message}")
        output.append("")
        output.append("请检查输入或稍后重试。")
        
        return "\n".join(output)
    
    def format_help(self):
        """格式化帮助信息"""
        help_text = """
📖 使用帮助

支持的操作类型：
1. 数据查询 - 例如："查询所有销售记录"、"统计各产品销售额"
2. 数据分析 - 例如："分析销售趋势"、"对比各地区业绩"
3. 数据可视化 - 例如："生成销售额柱状图"、"画一个饼图"
4. 多轮对话 - 支持上下文追问，如"那北京的呢？"

示例问题：
- 查询1月份的所有销售记录
- 统计每个产品的总销售额
- 生成各地区的销售占比饼图
- 分析最近两个月的销售趋势

💡 提示：
- 支持自然语言提问
- 可以基于上次结果继续追问
- 生成的图表保存在 result 目录下
"""
        return help_text
    
    def format_response(self, intent, result, chart_path=None):
        """
        根据意图格式化响应
        
        Args:
            intent: 意图类型
            result: 结果内容
            chart_path: 图表路径（仅可视化时使用）
        
        Returns:
            str: 格式化后的响应
        """
        if intent == "query":
            return self.format_query_result(result[0], result[1]) if isinstance(result, tuple) else str(result)
        elif intent == "analysis":
            return self.format_analysis_result(result)
        elif intent == "visualize":
            return self.format_visualize_result(chart_path or result, "")
        elif intent == "conversation":
            return result
        else:
            return str(result)


# 全局输出格式化器实例
output_formatter = OutputFormatter()