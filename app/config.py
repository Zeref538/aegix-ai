"""Environment configuration. Loads .env once at import."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from supabase import Client, create_client

load_dotenv()


@lru_cache
def get_chat_model() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_deployment=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
        temperature=0,
    )


@lru_cache
def get_embeddings() -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_deployment=os.environ.get(
            "AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-small"
        ),
    )


@lru_cache
def get_supabase() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    )
