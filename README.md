# 
解析markdown数据，使用大模型图生文大模型进行图片解析，调用qwen3-vl-flash模型。
一个新的虚拟环境
conda create -n py10 python=3.10
conda activate py10
pip install numpy pandas matplotlib scikit-learn
pip install ipykernel jupyter

python -m ipykernel install --user --name=py10 --display-name="py10"
Installed kernelspec py10 in C:\Users\86193\AppData\Roaming\jupyter\kernels\py10

pip install python-dotenv #配置全局环境
pip install openai
pip install openpyxl
pip install tqdm

pip install zai-sdk