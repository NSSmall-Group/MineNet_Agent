inference_server_url = "http://localhost:6666/v1"
from langchain_openai import ChatOpenAI
from system_prompt import SystemPrompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent_tools import get_iii_type_agent_network_status, generate_security_report

from utils import Colors

# ------------------------构建Agent--------------------------------------
llm = ChatOpenAI(
    model="/home/xd/llm_model/Qwen2_5_32B_Instruct/",
    openai_api_key="none",
    openai_api_base=inference_server_url,
    max_tokens=512,
    temperature=0,
)
# ------------------------构建Agent--------------------------------------


from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

tools = [get_iii_type_agent_network_status, generate_security_report]

# Modification: tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

import json

from langchain_core.messages import ToolMessage


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot") #工具信息会返回给chatbot
graph_builder.add_edge(START, "chatbot") 
graph = graph_builder.compile() # 编译图

# #非流式输出，不显示思考过程
# def stream_graph_updates(user_input: str): 
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
#         for node_name, value in event.items():
#             # 只打印 chatbot 节点的输出，并且确保不是工具调用
#             if node_name == "chatbot":
#                 last_message = value["messages"][-1]
#                 if not hasattr(last_message, "tool_calls") or len(last_message.tool_calls) == 0:
#                     print("Assistant:", last_message.content)


# 把LLM的决策过程显示出来
def stream_graph_updates(user_input: str): 
    # 使用 graph.stream 实时获取图的每一步更新
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        # event 是一个字典，key 是节点名，value 是该节点的输出
        for node_name, value in event.items():
            print(f"--- [ 节点: {node_name} ] ---")
            
            # 从节点的输出中获取最新的消息
            # 无论是 chatbot 还是 tools 节点，输出的 value 都是 {"messages": [some_message]} 格式
            last_message = value["messages"][-1]

            # --- 对 chatbot 节点的输出进行解读 ---
            if node_name == "chatbot":
                # 情况1: LLM 决定调用工具
                if last_message.tool_calls:
                    print(Colors.GREEN + "✨ LLM 决策: 我需要使用工具来回答。" + Colors.RESET)
                    for tool_call in last_message.tool_calls:
                        tool_name = tool_call['name']
                        tool_args = tool_call['args']
                        print(Colors.GREEN + f"   - 准备调用工具: `{tool_name}`" + Colors.RESET)
                        print(Colors.GREEN + f"   - 提供的参数: {tool_args}" + Colors.RESET)
                # 情况2: LLM 决定直接回答 (通常是最后一步)
                else:
                    print(Colors.CYAN + f"✅ LLM 最终回答:\n{last_message.content}" + Colors.RESET)

            # --- 对 tools 节点的输出进行解读 ---
            elif node_name == "tools":
                # tools 节点的输出是 ToolMessage 列表，我们只看最新的一个
                print(Colors.BLUE + "⚒️  工具执行结果:" + Colors.RESET)
                print(Colors.BLUE + f"   - 工具 `{last_message.name}` 已执行。" + Colors.RESET)
                print(Colors.BLUE + f"   - 返回内容: {last_message.content}" + Colors.RESET)
            
            print("-" * 25 + "\n") # 打印分隔符，让输出更清晰


print("----------------------MeNet智能体构建成功----------------------")
print()
print()
print("----------------------你好，我是MeNet智能体，有什么我能帮您的？----------------------")
print()
print()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("再见! 期待下次见！")
        break

    print("----------------------正在思考中，请耐心等待----------------------")

    stream_graph_updates(user_input)

# TODO： 查询当前状态、历史状态

# # 5. 调用这个Chain，只需要提供占位符的内容即可
# response = chain.invoke({"input": "请用中文回答你是谁"})

# print(response)