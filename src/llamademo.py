from llama_cpp import Llama

# 初始化模型（请将路径替换为你本地的模型路径）
modelPath = "/Users/zoe/Documents/pocs/browserHistory/model/qwen1_5-1_8b-chat-q5_k_m.gguf"

llm = Llama(model_path=modelPath, n_ctx=2048, n_threads=4,  verbose=True)

# 要分析的文本
text = "OpenAI发布了GPT-4模型，引起了全球范围的关注和讨论。它在多个自然语言处理任务中表现优异。"

# 构建提示词
prompt = f"""
你是一个中文文本分析专家，请从下面这段文本中提取5个关键词：
{text}
请只输出关键词列表，用中文逗号分隔。
"""

# 调用模型
response = llm(
    prompt=prompt,
    temperature=0.7,
    top_p=0.9,
    max_tokens=100,
    stop=["\n"]
)

# 输出结果
print("提取的关键词：", response["choices"][0]["text"].strip())
