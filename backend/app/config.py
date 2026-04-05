from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_api_base_url: str = "https://api.featherless.ai/v1"
    llm_api_key: str = ""
    llm_model_id: str = "arcee-ai/Trinity-Large-Thinking"
    embedding_dim: int = 384  # all-MiniLM-L6-v2 (local sentence-transformers)

    # Database
    database_url: str = "postgresql://goveval:goveval@localhost:5432/goveval"

    # Queue
    redis_url: str = "redis://localhost:6379/0"

    # Academic APIs
    semantic_scholar_api_key: str = ""
    pubmed_email: str = "dev@yourdomain.com"

    # RAG config
    retrieval_top_n: int = 20
    rerank_top_k: int = 10

    # App
    environment: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
