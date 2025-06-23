# hotel_agent/llm_wrapper.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

llm = ChatGroq(
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-8b-8192"
)
