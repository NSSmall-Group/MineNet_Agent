# MineNet_Agent
网络安全状况Agent

> 用于检查当前网络安全状况的Agent。


1. 启动接口服务
```
python get_detect_res_test.py
```

2. 启动VLLM服务
```
python -m vllm.entrypoints.openai.api_server \
  --model /home/xd/llm_model/Qwen2_5_32B_Instruct/ \
  --host localhost \
  --port 6666 \
  --dtype=half \
  --tensor-parallel-size=2  \
  --pipeline-parallel-size=3 \
  --max_model_len 16384 \
  --gpu_memory_utilization 0.95 \
  --enable-auto-tool-choice \
  --tool_call_parser hermes
```

3. 运行Agent
```
python menet_agent.py
```


4. Prompt
```
请你检查一下3类智能体的网络安全状况,并依据安全状况检索相关的CVE知识，然后一同生成一份网络安全报告。
```
