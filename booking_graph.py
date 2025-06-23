from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.runnables import Runnable
#from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from llm_wrapper import llm
from db import save_booking

class AgentState(TypedDict):
    input: str
    username: str
    output: str

# Prompt templates
booking_prompt = PromptTemplate.from_template("""
You are a hotel booking assistant. Help the user book a hotel by asking them for:
1. Check-in date
2. Check-out date
3. Number of guests
4. Room type
Respond conversationally.
""")

faq_prompt = PromptTemplate.from_template("""
You are a helpful hotel assistant. Answer the user's question briefly and politely:
{input}
""")

booking_chain = booking_prompt | llm
faq_chain = faq_prompt | llm

# State handlers
def check_intent(state):
    user_input = state['input'].lower()
    if "book" in user_input:
        return {"next": "booking"}
    elif "reschedule" in user_input:
        return {"next": "reschedule"}
    elif "check-in" in user_input or "amenities" in user_input:
        return {"next": "faq"}
    return {"next": "faq"}

def booking_node(state):
    result = booking_chain.invoke({"input": state['input']})
    save_booking(state['username'], "2025-07-01", "2025-07-03", "Deluxe", 2)  # mock
    return {"output": result['text'], **state}

def reschedule_node(state):
    return {"output": "Please provide your new check-in and check-out dates.", **state}

def faq_node(state):
    result = faq_chain.invoke({"input": state['input']})
    return {"output": result['text'], **state}

# LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("check_intent", check_intent)
workflow.add_node("booking", booking_node)
workflow.add_node("reschedule", reschedule_node)
workflow.add_node("faq", faq_node)
workflow.set_entry_point("check_intent")
workflow.add_conditional_edges("check_intent", lambda x: x["next"], {
    "booking": "booking",
    "reschedule": "reschedule",
    "faq": "faq"
})
workflow.add_edge("booking", END)
workflow.add_edge("reschedule", END)
workflow.add_edge("faq", END)
agent_executor = workflow.compile()