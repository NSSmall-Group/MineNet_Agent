from langchain_core.tools import tool

import requests
import json

@tool
def get_iii_type_agent_network_status():
    """
    用于获取3类智能体的当前的网络安全状况
    """
    print("------------正在调用工具，检查3类智能体的网络安全状况---------------")
    
    url = "http://localhost:8899" #TODO

    # 发送Get请求，调用异常检测系统
    response = requests.get(url)

    # print(response.json())
    
    # 获取检测结果
    detect_res = response.json()

    return detect_res