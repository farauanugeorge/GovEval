import asyncio
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings


@dataclass
class Paper:
    doi: Optional[str]
    title: str
    authors: Optional[str]
    year: Optional[int]
    abstract: str
    origin: str


async def search_semantic_scholar(query: str, limit: int = 10) -> list[Paper]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,externalIds",
    }
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

    papers = []
    for item in data.get("data", []):
        abstract = item.get("abstract")
        if not abstract:
            continue
        doi = (item.get("externalIds") or {}).get("DOI")
        authors = ", ".join(a.get("name", "") for a in (item.get("authors") or [])[:5])
        papers.append(
            Paper(
                doi=doi,
                title=item.get("title", ""),
                authors=authors or None,
                year=item.get("year"),
                abstract=abstract,
                origin="semantic_scholar",
            )
        )
    return papers


async def search_openalex(query: str, limit: int = 10) -> list[Paper]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": limit,
        "select": "doi,title,authorships,publication_year,abstract_inverted_index",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

    papers = []
    for item in data.get("results", []):
        inv_index = item.get("abstract_inverted_index")
        if not inv_index:
            continue
        abstract = _reconstruct_abstract(inv_index)
        if not abstract:
            continue

        doi = item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None
        authors = ", ".join(
            a.get("author", {}).get("display_name", "")
            for a in (item.get("authorships") or [])[:5]
        )
        papers.append(
            Paper(
                doi=doi,
                title=item.get("title", ""),
                authors=authors or None,
                year=item.get("publication_year"),
                abstract=abstract,
                origin="openalex",
            )
        )
    return papers


async def search_pubmed(query: str, limit: int = 10) -> list[Paper]:
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            # Search for IDs
            resp = await client.get(
                search_url,
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmax": limit,
                    "retmode": "json",
                    "email": settings.pubmed_email,
                },
            )
            resp.raise_for_status()
            ids = resp.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            # Fetch details
            resp = await client.get(
                fetch_url,
                params={
                    "db": "pubmed",
                    "id": ",".join(ids),
                    "retmode": "xml",
                    "email": settings.pubmed_email,
                },
            )
            resp.raise_for_status()
        except Exception:
            return []

    return _parse_pubmed_xml(resp.text)


def _parse_pubmed_xml(xml_text: str) -> list[Paper]:
    from xml.etree import ElementTree as ET

    papers = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    for article in root.findall(".//PubmedArticle"):
        medline = article.find("MedlineCitation")
        if medline is None:
            continue

        art = medline.find("Article")
        if art is None:
            continue

        abstract_el = art.find("Abstract/AbstractText")
        if abstract_el is None or not abstract_el.text:
            continue

        title_el = art.find("ArticleTitle")
        title = title_el.text if title_el is not None and title_el.text else ""

        # Extract DOI
        doi = None
        for id_el in article.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text
                break

        # Extract authors
        authors_list = []
        for author in art.findall("AuthorList/Author")[:5]:
            last = author.findtext("LastName", "")
            first = author.findtext("ForeName", "")
            if last:
                authors_list.append(f"{first} {last}".strip())

        # Extract year
        year = None
        date_el = art.find("Journal/JournalIssue/PubDate/Year")
        if date_el is not None and date_el.text:
            try:
                year = int(date_el.text)
            except ValueError:
                pass

        papers.append(
            Paper(
                doi=doi,
                title=title,
                authors=", ".join(authors_list) or None,
                year=year,
                abstract=abstract_el.text,
                origin="pubmed",
            )
        )
    return papers


def _reconstruct_abstract(inverted_index: dict) -> str:
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)


async def search_all_sources(query: str, limit_per_source: int = 7) -> list[Paper]:
    results = await asyncio.gather(
        search_semantic_scholar(query, limit_per_source),
        search_openalex(query, limit_per_source),
        search_pubmed(query, limit_per_source),
        return_exceptions=True,
    )

    papers = []
    seen_dois = set()
    for result in results:
        if isinstance(result, Exception):
            continue
        for paper in result:
            # Deduplicate by DOI
            if paper.doi and paper.doi in seen_dois:
                continue
            if paper.doi:
                seen_dois.add(paper.doi)
            papers.append(paper)

    return papers
