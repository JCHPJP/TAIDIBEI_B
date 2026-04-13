# prompts/__init__.py
# Prompt模块导出

from .intent_prompts import INTENT_SYSTEM_PROMPT, get_intent_user_prompt
from .entity_prompts import ENTITY_SYSTEM_PROMPT, get_entity_user_prompt
from .analysis_prompts import ANALYSIS_SYSTEM_PROMPT, get_analysis_user_prompt
from .conversation_prompts import CONVERSATION_SYSTEM_PROMPT, get_conversation_user_prompt

__all__ = [
    'INTENT_SYSTEM_PROMPT',
    'get_intent_user_prompt',
    'SQL_SYSTEM_PROMPT',

    'ENTITY_SYSTEM_PROMPT',
    'get_entity_user_prompt',
    'ANALYSIS_SYSTEM_PROMPT',
    'get_analysis_user_prompt',
    'CONVERSATION_SYSTEM_PROMPT',
    'get_conversation_user_prompt',
]