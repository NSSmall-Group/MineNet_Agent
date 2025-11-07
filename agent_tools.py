from langchain_core.tools import tool

import requests
import json

import os

# --- 必要的 imports ---
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI # 假设你使用OpenAI的LLM作为Agent的大脑
from langchain_community.vectorstores import Chroma # 确保导入
from langchain_community.embeddings import ModelScopeEmbeddings # 确保导入
import os

@tool
def get_iii_type_agent_network_status():
    """
    用于获取3类智能体的当前的网络安全状况
    """
    print("\n------------正在调用工具，检查3类智能体的网络安全状况---------------\n")
    
    url = "http://localhost:8899" #TODO

    # 发送Get请求，调用异常检测系统
    response = requests.get(url)

    # print(response.json())
    
    # 获取检测结果
    detect_res = response.json()

    return detect_res


import datetime 

@tool
def generate_security_report(security_analysis_summary:str)->str:
    """
    接受一段对网络安全状况的【分析和总结】，而不是原始数据。
    它会将这段分析性的文字格式化成一份正式的Markdown安全报告，
    并保存到本地文件 'security_report.md'。
    """

    print("\n------------正在调用工具，生成网络安全报告中---------------\n")

    dir = "/home/xd/llm_deploy/menet_agent/cyper_security_reports"
    filename = "security_report.md"
    save_path = os.path.join(dir, filename)
    report_title = "# 网络安全状况报告"
    timestamp = f"**生成时间：** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    status_section = "## 状况摘要"
    conclusion = "## 结论\n \n 报告已经生成，请相关人员查阅并跟进。"

    # 组合成 Markdown 格式的内容
    markdown_content = f"{report_title}\n\n{timestamp}\n\n{status_section}\n\n> {security_analysis_summary}\n\n{conclusion}"

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return f"报告已成功生成并保存到本地文件: {save_path}"
    except Exception as e:
        return f"生成报告时发生错误: {e}"
    

def make_cve_retriever_tool(retriever):
    """
    一个工厂函数：接受一个retriever，然后返回一个封装了该retriever的LangChain工具
    """
    @tool
    def cve_knowledge_retriever(query: str) -> str:
        """
        当用户询问关于特定CVE漏洞、软件漏洞、或网络安全技术问题时，使用此工具检索相关的背景知识。
        输入应该是用户的原始问题。此工具返回的是原始的技术资料，而不是最终答案。
        """
        print(f"\n--- 调用CVE知识库检索工具, 查询: '{query}' ---\n")
        
        docs = retriever.invoke(query)

        if not docs:
            return "--- 在CVE知识库中没有找到相关信息 ---"
            
        context = "--- 从CVE知识库中检索到的相关信息 ---\n\n"
        context += "\n\n---\n\n".join([doc.page_content for doc in docs])
        return context

    return cve_knowledge_retriever
