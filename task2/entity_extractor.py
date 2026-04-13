# entity_extractor.py
# 实体提取器

import json
from llm_client import deepseek_client
from prompts.entity_prompts import ENTITY_SYSTEM_PROMPT, get_entity_user_prompt


class EntityExtractor:
    """实体提取器类"""
    
    def __init__(self):
        self.entity_types = ["time", "product", "category", "region", "metric", "condition"]
    
    def extract(self, user_input):
        """
        从用户输入中提取实体
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            dict: 提取的实体字典
        """
        user_prompt = get_entity_user_prompt(user_input)
        
        response = deepseek_client.chat_with_system(
            system_prompt=ENTITY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3
        )
        
        if response:
            entities = deepseek_client.extract_json(response)
            if entities and "entities" in entities:
                # 确保所有实体类型都存在
                for entity_type in self.entity_types:
                    if entity_type not in entities["entities"]:
                        entities["entities"][entity_type] = []
                return entities["entities"]
        
        # 返回空实体
        return {entity_type: [] for entity_type in self.entity_types}
    
    def build_condition_from_entities(self, entities):
        """
        根据提取的实体构建查询条件描述
        
        Args:
            entities: 实体字典
        
        Returns:
            str: 条件描述文本
        """
        conditions = []
        
        if entities.get("time"):
            conditions.append(f"时间范围: {', '.join(entities['time'])}")
        if entities.get("product"):
            conditions.append(f"产品: {', '.join(entities['product'])}")
        if entities.get("category"):
            conditions.append(f"类别: {', '.join(entities['category'])}")
        if entities.get("region"):
            conditions.append(f"地区: {', '.join(entities['region'])}")
        if entities.get("metric"):
            conditions.append(f"指标: {', '.join(entities['metric'])}")
        if entities.get("condition"):
            conditions.append(f"约束条件: {', '.join(entities['condition'])}")
        
        return "; ".join(conditions) if conditions else "无特殊条件"
    
    def get_entity_summary(self, entities):
        """获取实体提取的简要总结"""
        found_entities = []
        for entity_type, values in entities.items():
            if values:
                found_entities.append(f"{entity_type}: {', '.join(values)}")
        
        if found_entities:
            return f"提取到实体 - {'; '.join(found_entities)}"
        return "未提取到关键实体"


# 全局实体提取器实例
entity_extractor = EntityExtractor()