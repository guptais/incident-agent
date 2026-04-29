from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]


def my_node(state: State):
    print(f"DEBUG: messages in state = {state['messages']}")
    return {"messages": [HumanMessage(content="hello back")]}

graph = StateGraph(State)
graph.add_node("node", my_node)
graph.set_entry_point("node")
graph.add_edge("node", END)
app = graph.compile()

result = app.invoke({"messages":[HumanMessage(content="Hello")]})

print(f"Result:{result}")