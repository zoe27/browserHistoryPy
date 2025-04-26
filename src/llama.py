from llama_cpp import Llama

from llama_cpp import Llama

# 初始化模型（请将路径替换为你本地的模型路径）
modelPath = "/Users/zoe/Documents/pocs/browserHistory/model/qwen1_5-1_8b-chat-q5_k_m.gguf"

# llm = Llama(model_path=modelPath, n_ctx=2048, n_threads=4,  verbose=True)

llm = Llama(
      # model_path="./models/7B/llama-model.gguf",
      model_path = "/Users/zoe/Documents/pocs/browserHistory/model/qwen1_5-1_8b-chat-q5_k_m.gguf"
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)
output = llm(
      "Q: Name the planets in the solar system? A: ", # Prompt
      max_tokens=32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
      stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
      echo=True # Echo the prompt back in the output
) # Generate a completion, can also call create_completion
print(output)