import openai
from dotenv import load_dotenv
import os
import base64

load_dotenv()

def getAgent(api_key: str, base_url: str):
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    return client

# 初始化客户端
client = getAgent(
    os.getenv("PARATERA_API_KEY"),
    os.getenv("PARATERA_BASE_URL")
)

# 准备图片（Base64 编码）
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 方式一：使用 Base64 编码
base64_image = encode_image("parsed_results\\reports-上交所\\images\\0a7ccf0742874e9a67f8048602eb1607f392024e52a3ecf2ed8eccbdbcffa0c4.jpg")  # 替换为实际图片路径

response = client.chat.completions.create(
    model="GLM-4V-Flash",  # 修改为多模态模型名称
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                },
                {
                    "type": "text",
                    "text": "请识别图片中的表格内容，并以 Markdown 格式返回。"
                }
            ]
        }
    ],
    max_tokens=1000  # 控制回复长度
)

print(response.choices[0].message.content)