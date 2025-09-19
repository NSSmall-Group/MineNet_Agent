# MineNet_Agent
> 用于检查当前网络安全状况的Agent。


1. 启动VLLM服务
```
python -m vllm.entrypoints.openai.api_server \
  --model /home/xd/llm_model/Qwen2_5_32B_Instruct/ \
  --host localhost \
  --port 6666 \
  --dtype=half \
  --tensor-parallel-size 4 \
  --max_model_len 16384 \
  --gpu_memory_utilization 0.95 \
  --enable-auto-tool-choice \
  --tool_call_parser hermes
```

2. 运行Agent
```
Python menet_agent.py
```
