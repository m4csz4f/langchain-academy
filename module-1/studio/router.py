from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

credential = DefaultAzureCredential()
scope = "https://cognitiveservices.azure.com/.default"
token_provider = get_bearer_token_provider(credential, scope)

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
    api_version=os.getenv("API_VERSION"),
    azure_ad_token_provider=token_provider,
    openai_api_type=os.getenv("OPENAI_API_TYPE"),
    model=os.getenv("MODEL"),
    temperature=0.0,
    streaming=False,
    callbacks=[],
    verbose=False,
    timeout=120,
)


# Tool
def multiply(a: int, b: int) -> int:
    """Multiplies a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# LLM with bound tool
llm_with_tools = llm.bind_tools([multiply])


# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", END)

# Compile graph
graph = builder.compile()
