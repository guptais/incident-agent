from dotenv import load_dotenv
load_dotenv()

# from langchain_anthropic import ChatAnthropic
# from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages 
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    messages: Annotated[list, add_messages] # type: ignore

@tool
def check_datadog(service: str) -> str:
    """Check Datadog for error rates and metrics for a given service"""
    return f"""
    Datadog metrics for {service}: 
    - Error rate: 70% (normal <1%)
    - P99 latency: 8200ms (normal <200ms)
    """

@tool
def check_github(service: str) -> str:
    """Check github for recent deployments with commits for a given service"""
    return f"""
    Recent commits on {service}:
    - 45 min ago: "increased cpu limit from 50 to 80"
    """

@tool
def check_sentry(service: str) -> str:
    """Check sentry for recent errors for a given service"""
    return f"""
    Sentry errors for {service} (last 1 hour):
    - CrashLooping: 20 occurrences - NEW
    """

tools = [
    check_datadog, 
    check_github, 
    check_sentry
]
model = ChatOpenAI(
        model="llama3.1", 
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    ).bind_tools(tools=tools)

def agent_node(state: AgentState):
    """The agent received messages, calls the LLM, returns its response. """
    messages = state.get("messages", [])
    # print(f"DEBUG agent_node: {len(messages)} messages in state")
    if not messages:
        return {"messages": []}
    response = model.invoke(messages)
    # print(f"DEBUG response type:{type(response)}")
    # print(f"DEBUG response content: {response.content}")
    # print(f"DEBUG response tool_calls:{response.tool_calls}")
    return {"messages": [response]}

def should_continue(state: AgentState):
    """decide whether to call a tool or end."""
    messages = state.get("messages",[])
    if not messages:
        return END
    last_message = messages[-1]
    # print(f"DEBUG should_continue: tool_calls={last_message.tool_calls}")
    if last_message.tool_calls:
        return "tools"
    return END

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")

    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()

app = build_graph()

if __name__ == "__main__":
    alert = {
        "alert_id": "PD-1234",
        "service": "payments-api",
        "severity": "critical",
        "message": "High error rate detected - 500s spiking on /v1/charge endpoint"
    }
    print(f"Processing alert: {alert['message']}\n")

    initial_state = { "messages": [HumanMessage(content=f"""
        You are an SRE incident assistant. Investigate this alert and provide a root cause analysis.
        Alert: {alert["message"]}
        Service: {alert["service"]}
        Severity: {alert["severity"]}

        Use the available tools to gather evidence, then summarize your findings.
        """)]}
    
    try:
        result = app.invoke(initial_state) # type: ignore
        print("--Incident Summary--")
        if result and result.get("messages"):
            print(result["messages"][-1].content)
        else:
            print("No response generated")
            print(f"Raw result:{result}")
    except Exception as e:
        print(f"ERROR during invoke:{e}")
        import traceback
        traceback.print_exc()

    
