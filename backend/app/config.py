from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_api_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model_id: str = "gpt-3.5-turbo"
    llm_embedding_model_id: str = "text-embedding-ada-002"
    embedding_dim: int = 1536

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
