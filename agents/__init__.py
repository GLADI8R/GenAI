import os
import warnings
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

# Initialize the Azure OpenAI LLM
llm = AzureChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    model="gpt-4o",
    temperature=0
    # timeout=None
)
