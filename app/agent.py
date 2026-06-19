import os
import json
import operator
from typing import TypedDict, Annotated, Sequence, Union, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from tools import calculate_pemdi_index, list_aspects, search_pemdi_doc
from prompts import SYSTEM_PROMPT

TOKENROUTER_API_KEY = os.getenv("TOKENROUTER_API_KEY", "")
TOKENROUTER_BASE_URL = os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "MiniMax-M3")

# Initialize LLM without bind_tools to avoid TokenRouter bug
llm = ChatOpenAI(
    api_key=TOKENROUTER_API_KEY,
    base_url=TOKENROUTER_BASE_URL,
    model=LLM_MODEL_NAME,
    temperature=0.1,
    model_kwargs={"response_format": {"type": "json_object"}}
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

REACT_PROMPT = """Anda adalah asisten AI RAG untuk dokumen Indeks Pemdi.
Anda memiliki akses ke tools berikut:
1. search_pemdi_doc: Mencari informasi dari dokumen. Input: string query.
2. calculate_pemdi_index: Menghitung indeks. Input: dictionary indicators (misal: {"Dampak": 3, "Kompleksitas": 4}).
3. list_aspects: Menampilkan aspek penilaian. Input: string kosong "".

ANDA WAJIB MERESPONS DALAM FORMAT JSON BERIKUT (dan HANYA JSON):
{
  "thought": "pemikiran Anda tentang apa yang harus dilakukan",
  "action": "nama aksi (search_pemdi_doc, calculate_pemdi_index, list_aspects) ATAU 'none' jika sudah ada jawaban final",
  "action_input": <input untuk aksi, gunakan format sesuai spesifikasi, atau null jika action 'none'>,
  "final_answer": "jawaban akhir untuk pengguna, isi null jika masih perlu menggunakan aksi"
}

Pertanyaan pengguna akan diberikan di bawah ini.
"""

import re

def extract_json(content: str) -> dict:
    try:
        return json.loads(content)
    except:
        pass
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return {}

def call_model(state):
    messages = state["messages"]
    
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=REACT_PROMPT)] + list(messages)
        
    response = llm.invoke(messages)
    return {"messages": [response]}

def call_tool(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        parsed = extract_json(last_message.content)
        action = parsed.get("action", "none")
        action_input = parsed.get("action_input", "")
        
        if action == "search_pemdi_doc":
            result = search_pemdi_doc.invoke({"query": str(action_input)})
        elif action == "calculate_pemdi_index":
            result = calculate_pemdi_index.invoke({"indicators": action_input})
        elif action == "list_aspects":
            result = list_aspects.invoke({})
        else:
            result = "Action not found."
            
        tool_response = f"Observation for {action}:\n{result}"
    except Exception as e:
        tool_response = f"Error processing action: {str(e)}"
        
    return {"messages": [HumanMessage(content=tool_response)]}

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        parsed = extract_json(last_message.content)
        if parsed.get("action") and parsed.get("action") != "none":
            return "continue"
    except:
        pass
    return "end"

# Define LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")

app_agent = workflow.compile()

