from fastapi import FastAPI
import uvicorn

# 创建一个 FastAPI 应用实例
app = FastAPI()

# 定义一个路由和处理函数
# @app.get("/") 表示当收到对根路径 "/" 的 GET 请求时，由下面的函数处理
@app.get("/")
async def read_root():
    detect_res = """
        {
            "timestamp": 1760320451.9664695,
            "detection_method": "rule_based",
            "attack_info": {
                "is_attack": true,
                "attack_type": "intrusion",
                "confidence": 0.8,
                "severity": "high",
                "description": "规则匹配: 非法设备入侵检测 - 检测源节点在实体图中不存在的非法设备入侵攻击",
                "detection_method": "rule_based",
                "timestamp": 1760320451.9657648
            },
            "trace_info": {
                "source_nodes": [
                "192.168.5.20:59755"
                ],
                "trace_path": [
                "192.168.5.20:59755",
                "192.168.7.99:1883"
                ],
                "confidence": 0.95,
                "description": "基于异常事件数据的溯源分析: 检测到新的网络通信端点:\n  源: 192.168.5.20:59755\n  目标: 192.168.7.99:1883\n"
            },
            "blocking_actions": [],
            "summary": {
                "attack_type": "intrusion",
                "severity": "high",
                "confidence": 0.8,
                "source_nodes_count": 1,
                "blocking_actions_count": 0
            }
        }
    """

    return {"message": detect_res}

if __name__ == "__main__":
    print("启动FastAPI应用服务器")
    
    uvicorn.run(
        app, 
        host="127.0.0.1",
        port=8899
    )