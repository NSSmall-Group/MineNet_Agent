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
            "anomalies": 
            {
                "timestamp": 1756904477.3335204,
                "type": "network_endpoint_anomaly",
                "severity": {
                "score": 0.6,
                "confidence": 0.7
                },
                "description": "检测到新的网络通信端点:\n  源: 127.0.0.1:9097\n  目标: 127.0.0.1:56838\n",
                "affected_entity": {
                "id": "127.0.0.1:9097_127.0.0.1:56838",
                "type": "network_endpoint",
                "details": {
                    "source": {
                    "ip": "127.0.0.1",
                    "port": 9097
                    },
                    "destination": {
                    "ip": "127.0.0.1",
                    "port": 56838
                    },
                    "protocol": "OTHER",
                    "packet_size": null
                }
                },
                "context": {
                "baseline_comparison": {},
                "related_entities": []
                }
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