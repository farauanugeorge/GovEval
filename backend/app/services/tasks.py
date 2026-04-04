import asyncio
import logging
from datetime import datetime, timezone

import numpy as np
from celery import Task

from app.config import settings
from app.database import SessionLocal
from app.models import Analysis, Embedding, Source, Verdict
from app.services.academic import search_all_sources
from app.services.extraction import extract_policy_text
from app.services.llm import generate_search_queries, generate_verdict, get_embeddings
from app.worker import celery_app

logger = logging.getLogger(__name__)


class AnalysisTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        db = SessionLocal()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == task_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_msg = str(exc)[:500]
                db.commit()
        finally:
            db.close()


@celery_app.task(
    bind=True,
    base=AnalysisTask,
    max_retries=2,
    default_retry_delay=10,
    name="app.services.tasks.run_analysis_pipeline",
)
def run_analysis_pipeline(self, analysis_id: str):
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return

        analysis.status = "processing"
        db.commit()

        # Step 1: Extract policy text
        self.update_state(state="PROGRESS", meta={"step": "Reading policy text"})
        if analysis.input_type != "text":
            policy_text = extract_policy_text(analysis.input_type, analysis.input_raw)
            analysis.policy_text = policy_text
            db.commit()
        else:
            policy_text = analysis.policy_text

        # Step 2: Generate search queries
        self.update_state(state="PROGRESS", meta={"step": "Generating search queries"})
        queries = generate_search_queries(policy_text)
        logger.info(f"Generated {len(queries)} search queries for {analysis_id}")

        # Step 3: Search academic databases
        self.update_state(
            state="PROGRESS", meta={"step": "Searching academic databases"}
        )
        all_papers = []
        for query in queries:
            papers = asyncio.get_event_loop().run_until_complete(
                search_all_sources(query, limit_per_source=settings.retrieval_top_n // 3)
            )
            all_papers.extend(papers)

        # Deduplicate again across queries
        seen_dois = set()
        unique_papers = []
        for p in all_papers:
            if p.doi and p.doi in seen_dois:
                continue
            if p.doi:
                seen_dois.add(p.doi)
            unique_papers.append(p)

        # Store sources in DB
        source_records = []
        for p in unique_papers:
            source = Source(
                analysis_id=analysis.id,
                doi=p.doi,
                title=p.title,
                authors=p.authors,
                year=p.year,
                abstract=p.abstract,
                origin=p.origin,
            )
            db.add(source)
            source_records.append(source)
        db.commit()

        # Step 4: Embed and rerank
        self.update_state(state="PROGRESS", meta={"step": "Ranking relevant studies"})
        if source_records:
            abstracts = [s.abstract for s in source_records]
            all_texts = [policy_text] + abstracts
            embeddings = get_embeddings(all_texts)

            policy_emb = np.array(embeddings[0])
            abstract_embs = [np.array(e) for e in embeddings[1:]]

            # Compute cosine similarity
            for i, (source, emb) in enumerate(zip(source_records, abstract_embs)):
                similarity = float(
                    np.dot(policy_emb, emb)
                    / (np.linalg.norm(policy_emb) * np.linalg.norm(emb) + 1e-10)
                )
                source.relevance_score = similarity

                # Store embedding
                embedding_record = Embedding(
                    source_id=source.id,
                    embedding=emb.tolist(),
                )
                db.add(embedding_record)

            db.commit()

            # Select top-K
            ranked = sorted(source_records, key=lambda s: s.relevance_score or 0, reverse=True)
            top_k = ranked[: settings.rerank_top_k]
            for s in top_k:
                s.used_in_verdict = True
            db.commit()
        else:
            top_k = []

        # Step 5: Generate verdict
        self.update_state(state="PROGRESS", meta={"step": "Generating verdict"})
        if top_k:
            abstracts_for_llm = [
                {"title": s.title, "doi": s.doi or "N/A", "abstract": s.abstract}
                for s in top_k
            ]
            verdict_data, raw_output = generate_verdict(policy_text, abstracts_for_llm)
        else:
            verdict_data = {
                "verdict": "mixed",
                "confidence": 10,
                "summary": (
                    "Insufficient academic evidence was found to evaluate this policy. "
                    "The academic databases searched did not return relevant peer-reviewed "
                    "studies addressing the specific claims in this policy. This does not "
                    "mean the policy is good or bad — it means the automated system could "
                    "not find enough evidence to render a confident verdict."
                ),
                "evidence_for": [],
                "evidence_against": [],
            }
            raw_output = "No sources found - default insufficient evidence response"

        # Validate verdict value
        if verdict_data.get("verdict") not in ("smart", "mixed", "poor"):
            verdict_data["verdict"] = "mixed"
        confidence = max(0, min(100, int(verdict_data.get("confidence", 50))))

        verdict = Verdict(
            analysis_id=analysis.id,
            verdict=verdict_data["verdict"],
            confidence=confidence,
            studies_used=len(top_k),
            summary=verdict_data.get("summary", ""),
            evidence_for=verdict_data.get("evidence_for", []),
            evidence_against=verdict_data.get("evidence_against", []),
            raw_llm_output=raw_output,
        )
        db.add(verdict)

        analysis.status = "complete"
        analysis.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Analysis {analysis_id} completed: {verdict_data['verdict']}")

    except Exception as exc:
        logger.exception(f"Analysis {analysis_id} failed")
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = "failed"
            analysis.error_msg = str(exc)[:500]
            db.commit()
        raise
    finally:
        db.close()
