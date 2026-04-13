# main.py - 支持多线程版本
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import time
from intent_recognizer import intent_recognizer
from sql_generator import sql_generator
from conversation import conversation_manager
from output_formatter import output_formatter


class ThreadSafeDataAssistant:
    """线程安全的数据分析助手"""
    
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
    
    def process_query(self, user_input, user_id=None):
        """
        处理单个查询（线程安全）
        
        Args:
            user_input: 用户输入
            user_id: 用户ID，用于隔离不同用户的对话历史
        
        Returns:
            str: 处理结果
        """
        # 为不同用户设置不同的对话上下文
        if user_id:
            # 可以基于user_id隔离对话历史
            pass
        
        # 识别意图
        intent_result = intent_recognizer.recognize(user_input)
        intent = intent_result.get("intent", "unknown")
        
        # 根据意图处理
        if intent == "query":
            return self._handle_query(user_input)
        elif intent == "analysis":
            return self._handle_analysis(user_input)
        elif intent == "visualize":
            return self._handle_visualize(user_input)
        else:
            return conversation_manager.chat(user_input)
    
    def _handle_query(self, user_input):
        """处理查询（线程安全）"""
        try:
            sql = sql_generator.generate(user_input)
            if not sql:
                return "无法生成SQL语句"
            
            df, columns, data = sql_generator.execute(sql)
            return output_formatter.format_query_result(columns, data)
        except Exception as e:
            return f"查询失败: {e}"
    
    def _handle_analysis(self, user_input):
        """处理分析（线程安全）"""
        return "分析功能开发中..."
    
    def _handle_visualize(self, user_input):
        """处理可视化（线程安全）"""
        return "可视化功能开发中..."
    
    def batch_process(self, queries_with_users):
        """
        批量处理多个查询（多线程）
        
        Args:
            queries_with_users: [(query, user_id), ...] 列表
        
        Returns:
            list: 处理结果列表
        """
        futures = []
        for query, user_id in queries_with_users:
            future = self.executor.submit(self.process_query, query, user_id)
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        
        return results
    
    def process_stream(self, query_queue, result_queue):
        """
        流式处理查询
        
        Args:
            query_queue: 输入队列
            result_queue: 输出队列
        """
        while True:
            try:
                query, user_id = query_queue.get(timeout=1)
                if query is None:  # 停止信号
                    break
                
                result = self.process_query(query, user_id)
                result_queue.put((query, result, user_id))
            except:
                break
    
    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)


# 多线程使用示例
def example_1_basic():
    """基础多线程示例"""
    assistant = ThreadSafeDataAssistant(max_workers=5)
    
    queries = [
        ("查询北京地区的销售额", "user1"),
        ("统计各产品销量", "user2"),
        ("分析销售趋势", "user1"),
        ("生成销售图表", "user3"),
        ("你好，请问你能做什么？", "user2"),
    ]
    
    # 方式1：逐个处理
    for query, user_id in queries:
        result = assistant.process_query(query, user_id)
        print(f"用户{user_id}: {query[:20]}... -> {result[:50]}...")
    
    # 方式2：批量并行处理
    results = assistant.batch_process(queries)
    for result in results:
        print(result[:100])


def example_2_high_concurrency():
    """高并发示例"""
    assistant = ThreadSafeDataAssistant(max_workers=20)
    
    # 模拟100个用户同时请求
    queries = [(f"查询第{i}个产品的销售额", f"user_{i%10}") for i in range(100)]
    
    start_time = time.time()
    results = assistant.batch_process(queries)
    end_time = time.time()
    
    print(f"处理100个请求耗时: {end_time - start_time:.2f}秒")
    print(f"平均每个请求: {(end_time - start_time)/100*1000:.2f}毫秒")


def example_3_producer_consumer():
    """生产者-消费者模式"""
    assistant = ThreadSafeDataAssistant(max_workers=10)
    query_queue = Queue()
    result_queue = Queue()
    
    # 启动工作线程
    worker_thread = threading.Thread(
        target=assistant.process_stream,
        args=(query_queue, result_queue)
    )
    worker_thread.start()
    
    # 生产者：不断添加查询
    for i in range(50):
        query_queue.put((f"查询第{i}个产品的销售", f"user_{i%5}"))
    
    # 发送停止信号
    query_queue.put((None, None))
    worker_thread.join()
    
    # 收集结果
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    print(f"处理完成，共{len(results)}个结果")


def example_4_web_simulation():
    """模拟Web服务场景"""
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    assistant = ThreadSafeDataAssistant(max_workers=50)
    
    @app.route('/query', methods=['POST'])
    def handle_query():
        """处理HTTP请求（每个请求在独立线程中）"""
        data = request.json
        user_input = data.get('query', '')
        user_id = data.get('user_id', 'default')
        
        # 这个调用会在Flask的线程中执行
        result = assistant.process_query(user_input, user_id)
        
        return jsonify({
            'success': True,
            'result': result,
            'user_id': user_id
        })
    
    @app.route('/batch', methods=['POST'])
    def handle_batch():
        """批量处理"""
        data = request.json
        queries = data.get('queries', [])
        
        # 注意：在Web应用中，不要在请求线程中等待大量并行任务
        # 应该使用异步处理
        results = assistant.batch_process(queries)
        
        return jsonify({
            'success': True,
            'results': results
        })
    
    # 启动服务
    # app.run(host='0.0.0.0', port=5000, threaded=True)


class ThreadPoolWithRateLimit:
    """带限流的线程池"""
    
    def __init__(self, max_workers=10, max_qps=5):
        self.max_workers = max_workers
        self.max_qps = max_qps
        self.min_interval = 1.0 / max_qps
        self.last_request_time = 0
        self._lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _rate_limit(self):
        """限流控制"""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_interval:
                time.sleep(self.min_interval - time_since_last)
            self.last_request_time = time.time()
    
    def submit(self, fn, *args, **kwargs):
        """提交任务（带限流）"""
        self._rate_limit()
        return self.executor.submit(fn, *args, **kwargs)
    
    def shutdown(self):
        self.executor.shutdown()


if __name__ == "__main__":
    print("1. 基础多线程示例")
    example_1_basic()
    
    print("\n2. 高并发示例")
    example_2_high_concurrency()
    
    print("\n3. 生产者-消费者示例")
    example_3_producer_consumer()