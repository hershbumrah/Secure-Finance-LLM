import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")

def get_llm():
    return ChatOllama(model=LLM_MODEL, base_url=LLM_BASE_URL, temperature=0.0)

def test_llm():
    llm = get_llm()
    response = llm.invoke([HumanMessage(content="Say 'LLM is ready for assistance'")])
    return response.content