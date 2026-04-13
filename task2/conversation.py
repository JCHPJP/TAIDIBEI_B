# conversation.py - 线程安全的多轮对话管理器
import threading
from llm_client import deepseek_client
from prompts.conversation_prompts import CONVERSATION_SYSTEM_PROMPT, get_conversation_user_prompt


class ConversationManager:
    """线程安全的多轮对话管理器"""
    
    def __init__(self):
        self._lock = threading.RLock()  # 可重入锁
        self._histories = {}  # 每个线程独立的对话历史
        self._contexts = {}   # 每个线程独立的上下文
    
    def _get_thread_id(self):
        """获取当前线程ID"""
        return threading.current_thread().ident
    
    def add_to_history(self, user_input, assistant_response):
        """添加对话到历史记录（线程安全）"""
        thread_id = self._get_thread_id()
        with self._lock:
            if thread_id not in self._histories:
                self._histories[thread_id] = []
            
            self._histories[thread_id].append({
                "user": user_input,
                "assistant": assistant_response
            })
            
            # 保持历史记录不超过最大长度
            if len(self._histories[thread_id]) > 10:
                self._histories[thread_id].pop(0)
    
    def get_history(self):
        """获取当前线程的对话历史"""
        thread_id = self._get_thread_id()
        with self._lock:
            return self._histories.get(thread_id, [])
    
    def clear_history(self):
        """清空当前线程的对话历史"""
        thread_id = self._get_thread_id()
        with self._lock:
            if thread_id in self._histories:
                del self._histories[thread_id]
            if thread_id in self._contexts:
                del self._contexts[thread_id]
    
    def set_context(self, key, value):
        """设置上下文信息（线程安全）"""
        thread_id = self._get_thread_id()
        with self._lock:
            if thread_id not in self._contexts:
                self._contexts[thread_id] = {}
            self._contexts[thread_id][key] = value
    
    def get_context(self, key):
        """获取上下文信息"""
        thread_id = self._get_thread_id()
        with self._lock:
            return self._contexts.get(thread_id, {}).get(key)
    
    def chat(self, user_input):
        """处理对话（线程安全）"""
        history = self.get_history()
        user_prompt = get_conversation_user_prompt(user_input, history)
        
        response = deepseek_client.chat_with_system(
            system_prompt=CONVERSATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.7
        )
        
        if response:
            self.add_to_history(user_input, response)
            return response
        
        return "抱歉，我遇到了一些问题，请稍后再试。"


# 全局对话管理器实例
conversation_manager = ConversationManager()