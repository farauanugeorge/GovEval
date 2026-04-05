import json
import logging
import re
from typing import Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: Optional[OpenAI] = None
_embedding_model = None


def get_llm_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base_url,
        )
    return _client


def _strip_thinking(text: str) -> str:
    """Strip <thinking>...</thinking> blocks from model output."""
    return re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()


def generate_search_queries(policy_text: str) -> list[str]:
    client = get_llm_client()

    response = client.chat.completions.create(
        model=settings.llm_model_id,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Given a government policy, extract the 3-5 most "
                    "important factual claims that can be verified against academic literature. "
                    "Return ONLY a JSON array of search query strings. No explanation. No markdown. "
                    "Each query should be suitable for an academic database search."
                ),
            },
            {"role": "user", "content": f"Policy: {policy_text[:4000]}"},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    raw = _strip_thinking(response.choices[0].message.content.strip())
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    try:
        queries = json.loads(raw)
        if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
            return queries[:5]
    except json.JSONDecodeError:
        pass

    # Fallback: split by newlines if JSON parse fails
    return [line.strip().strip('"') for line in raw.split("\n") if line.strip()][:5]


def generate_verdict(policy_text: str, abstracts: list[dict]) -> tuple[dict, str]:
    client = get_llm_client()

    abstracts_text = ""
    for i, a in enumerate(abstracts, 1):
        abstracts_text += f"[{i}] Title: {a['title']} | DOI: {a.get('doi', 'N/A')} | Abstract: {a['abstract']}\n\n"

    response = client.chat.completions.create(
        model=settings.llm_model_id,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evidence-based policy analyst. You will evaluate a government policy "
                    "EXCLUSIVELY using the academic abstracts provided below. You must not use any "
                    "prior knowledge, training data, or external information.\n\n"
                    "If the abstracts do not contain sufficient evidence, say so explicitly.\n"
                    "Do not fabricate citations. Do not speculate beyond what the abstracts state.\n\n"
                    "Return your analysis as valid JSON matching exactly this schema:\n"
                    "{\n"
                    '  "verdict": "smart" | "mixed" | "poor",\n'
                    '  "confidence": <integer 0-100>,\n'
                    '  "summary": <string, 200-350 words, plain language>,\n'
                    '  "evidence_for": [{"claim": string, "doi": string, "title": string}],\n'
                    '  "evidence_against": [{"claim": string, "doi": string, "title": string}]\n'
                    "}\n\n"
                    "Confidence scoring guidance:\n"
                    "  90-100: 8+ consistent studies, strong consensus\n"
                    "  70-89:  5-7 studies, mostly consistent\n"
                    "  50-69:  3-5 studies, mixed results\n"
                    "  30-49:  1-2 studies, or highly contradictory evidence\n"
                    "  0-29:   No relevant studies found\n\n"
                    "Return ONLY the JSON object. No markdown. No explanation."
                ),
            },
            {
                "role": "user",
                "content": f"POLICY: {policy_text[:4000]}\n\nACADEMIC ABSTRACTS:\n{abstracts_text}",
            },
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    raw_output = response.choices[0].message.content
    raw = _strip_thinking(raw_output.strip())
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    return json.loads(raw), raw_output


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using sentence-transformers locally."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Loaded embedding model: all-MiniLM-L6-v2")

    embeddings = _embedding_model.encode(texts, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]
