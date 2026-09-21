
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


# ================================================================
# PATHS
# ================================================================

APP_DIR = Path(__file__).resolve().parent

with open(APP_DIR / "artifact_config.json", "r") as f:
    CONFIG = json.load(f)

ARTIFACT_ROOT = APP_DIR / CONFIG["artifact_root"]

RAG_ROOT = ARTIFACT_ROOT / "rag_knowledge"
EMBEDDING_DIR = RAG_ROOT / "embeddings"

CHUNKS_PATH = RAG_ROOT / "chunks.json"
EMBEDDINGS_PATH = EMBEDDING_DIR / "chunk_embeddings.npy"
FAISS_PATH = EMBEDDING_DIR / "pestai_faiss.index"
SOURCE_REGISTRY_PATH = RAG_ROOT / "source_registry.csv"


# ================================================================
# TARGET PESTS
# ================================================================

TARGET_PESTS = [
    "Brown planthopper",
    "Caseworm",
    "Gall midge",
    "Green leafhopper",
    "Leaf folder",
    "Mirid bug",
    "White-backed planthopper",
    "Yellow stem borer",
    "Zig-zag leafhopper",
]


# ================================================================
# TOPIC DETECTION
# ================================================================

TOPIC_KEYWORDS = {
    "identification": [
        "identify",
        "identification",
        "what is",
        "recognize",
        "appearance",
    ],

    "symptoms": [
        "symptom",
        "symptoms",
        "damage",
        "damaging",
        "injury",
        "signs",
    ],

    "favorable_conditions": [
        "favorable",
        "favourable",
        "weather",
        "condition",
        "conditions",
        "climate",
        "temperature",
        "humidity",
        "rainfall",
    ],

    "monitoring": [
        "monitor",
        "monitoring",
        "scout",
        "scouting",
        "observe",
        "observation",
        "trap",
    ],

    "cultural_control": [
        "cultural",
        "crop management",
        "field management",
        "nutrition",
        "fertilizer",
        "fertilisation",
        "fertilization",
        "drainage",
        "planting",
        "cropping",
    ],

    "biological_control": [
        "biological",
        "biocontrol",
        "natural enemy",
        "natural enemies",
        "predator",
        "parasitoid",
    ],

    "mechanical_control": [
        "mechanical",
        "physical",
        "light trap",
        "hand pick",
        "remove",
    ],

    "chemical_control": [
        "chemical",
        "pesticide",
        "insecticide",
        "spray",
        "chemical control",
    ],

    "integrated_pest_management": [
        "integrated pest management",
        "integrated pest",
        "ipm",
        "management",
    ],
}


# ================================================================
# PEST ALIASES
# ================================================================

PEST_ALIASES = {
    "brown planthopper": "Brown planthopper",
    "bph": "Brown planthopper",

    "caseworm": "Caseworm",

    "gall midge": "Gall midge",

    "green leafhopper": "Green leafhopper",
    "glh": "Green leafhopper",

    "leaf folder": "Leaf folder",
    "leaffolder": "Leaf folder",

    "mirid bug": "Mirid bug",
    "mirid": "Mirid bug",

    "white-backed planthopper": "White-backed planthopper",
    "wbph": "White-backed planthopper",

    "yellow stem borer": "Yellow stem borer",
    "ysb": "Yellow stem borer",

    "zig-zag leafhopper": "Zig-zag leafhopper",
    "zig zag leafhopper": "Zig-zag leafhopper",
    "zzlh": "Zig-zag leafhopper",
}


# ================================================================
# GLOBAL LOAD
# ================================================================

_model = None
_index = None
_chunks = None
_source_registry = None


def _load():
    global _model, _index, _chunks, _source_registry

    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    if _index is None:
        _index = faiss.read_index(str(FAISS_PATH))

    if _chunks is None:
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict):
            _chunks = raw.get("chunks", [])
        else:
            _chunks = raw

    if _source_registry is None:
        if SOURCE_REGISTRY_PATH.exists():
            _source_registry = pd.read_csv(SOURCE_REGISTRY_PATH)
        else:
            _source_registry = pd.DataFrame()


def load_rag():
    """Load all validated RAG artifacts."""
    _load()

    usable = [
        c for c in _chunks
        if str(c.get("status", "")).upper() != "SOURCE_NOT_FOUND"
        and str(c.get("text", "")).strip()
    ]

    return {
        "model": _model,
        "index": _index,
        "chunks": _chunks,
        "usable_chunks": usable,
        "source_registry": _source_registry,
    }


# ================================================================
# DETECT PEST
# ================================================================

def detect_pest(query, selected_pest=None):

    if selected_pest in TARGET_PESTS:
        return selected_pest

    q = str(query).lower()

    for alias, canonical in sorted(
        PEST_ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        if alias in q:
            return canonical

    return None


# ================================================================
# DETECT TOPIC
# ================================================================

def detect_topic(query):

    q = str(query).lower()

    # More specific topics first
    priority = [
        "integrated_pest_management",
        "chemical_control",
        "biological_control",
        "mechanical_control",
        "cultural_control",
        "favorable_conditions",
        "monitoring",
        "symptoms",
        "identification",
    ]

    scores = {}

    for topic in priority:
        score = 0

        for keyword in TOPIC_KEYWORDS[topic]:
            if keyword in q:
                score += 1

        scores[topic] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return None

    return best


# ================================================================
# SOURCE EXTRACTION
# ================================================================

def _extract_sources(chunk):

    metadata = chunk.get("source_metadata", {})

    if not isinstance(metadata, dict):
        return []

    sources = metadata.get("sources", [])

    if not isinstance(sources, list):
        return []

    output = []

    for src in sources:

        if not isinstance(src, dict):
            continue

        title = str(src.get("title", "")).strip()
        organization = str(src.get("organization", "")).strip()
        url = str(src.get("url", "")).strip()

        # Remove markdown URL wrapper if present
        match = re.match(r"\[.*?\]\((https?://.*?)\)", url)

        if match:
            url = match.group(1)

        if title or organization or url:
            output.append({
                "title": title,
                "organization": organization,
                "url": url,
            })

    # Deduplicate
    unique = []
    seen = set()

    for src in output:

        key = (
            src["title"],
            src["organization"],
            src["url"],
        )

        if key not in seen:
            seen.add(key)
            unique.append(src)

    return unique


# ================================================================
# RERANKING
# ================================================================

def _rerank_score(
    semantic_score,
    chunk_pest,
    detected_pest,
    chunk_topic,
    detected_topic,
):

    score = float(semantic_score)

    if detected_pest and chunk_pest == detected_pest:
        score += 0.30

    if detected_topic and chunk_topic == detected_topic:
        score += 0.25

    return score


# ================================================================
# RETRIEVE RAG CONTEXT
# ================================================================

def retrieve_rag_context(
    query,
    selected_pest=None,
    top_k=10,
):

    _load()

    query = str(query).strip()

    if not query:
        return {
            "query": query,
            "detected_pest": selected_pest,
            "detected_topic": None,
            "results": [],
        }

    detected_pest = detect_pest(
        query,
        selected_pest=selected_pest
    )

    detected_topic = detect_topic(query)

    # Encode query
    embedding = _model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype("float32")

    # Retrieve a larger candidate set before reranking
    candidate_k = min(
        max(top_k * 4, 20),
        _index.ntotal
    )

    scores, indices = _index.search(
        embedding,
        candidate_k
    )

    candidates = []

    for semantic_score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0 or idx >= len(_chunks):
            continue

        chunk = _chunks[idx]

        # Never retrieve unresolved chunks
        if str(chunk.get("status", "")).upper() == "SOURCE_NOT_FOUND":
            continue

        text = str(chunk.get("text", "")).strip()

        if not text:
            continue

        chunk_pest = chunk.get("pest_name")
        chunk_topic = chunk.get("topic")

        rerank = _rerank_score(
            semantic_score,
            chunk_pest,
            detected_pest,
            chunk_topic,
            detected_topic,
        )

        candidates.append({
            "chunk_id": chunk.get("chunk_id"),
            "pest_id": chunk.get("pest_id"),
            "pest_name": chunk_pest,
            "crop": chunk.get("crop"),
            "category": chunk.get("category"),
            "topic": chunk_topic,
            "text": text,
            "semantic_score": float(semantic_score),
            "rerank_score": float(rerank),
            "sources": _extract_sources(chunk),
        })

    # Production ordering
    candidates.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    # Avoid duplicate chunk IDs
    results = []
    seen = set()

    for item in candidates:

        cid = item["chunk_id"]

        if cid in seen:
            continue

        seen.add(cid)
        results.append(item)

        if len(results) >= top_k:
            break

    return {
        "query": query,
        "detected_pest": detected_pest,
        "detected_topic": detected_topic,
        "results": results,
    }


# ================================================================
# BUILD FARMER-FACING EVIDENCE CONTEXT
# ================================================================

def build_evidence_context(
    query,
    selected_pest=None,
    top_k=10,
):

    retrieval = retrieve_rag_context(
        query=query,
        selected_pest=selected_pest,
        top_k=top_k,
    )

    evidence = []

    for item in retrieval["results"]:

        evidence.append({
            "pest": item["pest_name"],
            "topic": item["topic"],
            "text": item["text"],
            "sources": item["sources"],
            "semantic_score": item["semantic_score"],
            "rerank_score": item["rerank_score"],
        })

    return {
        "query": retrieval["query"],
        "detected_pest": retrieval["detected_pest"],
        "detected_topic": retrieval["detected_topic"],
        "evidence": evidence,
    }


# ================================================================
# SANITY TEST
# ================================================================

def rag_sanity_check():

    test_queries = [
        (
            "Brown planthopper symptoms",
            "Brown planthopper",
            "symptoms",
        ),
        (
            "Brown planthopper monitoring",
            "Brown planthopper",
            "monitoring",
        ),
        (
            "Gall midge favorable weather conditions",
            "Gall midge",
            "favorable_conditions",
        ),
        (
            "Green leafhopper biological control",
            "Green leafhopper",
            "biological_control",
        ),
        (
            "White-backed planthopper chemical control",
            "White-backed planthopper",
            "chemical_control",
        ),
        (
            "Yellow stem borer cultural practices",
            "Yellow stem borer",
            "cultural_control",
        ),
        (
            "Leaf folder integrated pest management",
            "Leaf folder",
            "integrated_pest_management",
        ),
    ]

    results = []

    for query, expected_pest, expected_topic in test_queries:

        result = retrieve_rag_context(
            query=query,
            selected_pest=expected_pest,
            top_k=5,
        )

        top = result["results"][0] if result["results"] else None

        pest_ok = (
            top is not None
            and top["pest_name"] == expected_pest
        )

        topic_ok = (
            top is not None
            and top["topic"] == expected_topic
        )

        evidence_ok = (
            top is not None
            and bool(top["text"])
        )

        results.append({
            "query": query,
            "pest_ok": pest_ok,
            "topic_ok": topic_ok,
            "evidence_ok": evidence_ok,
            "top_pest": top["pest_name"] if top else None,
            "top_topic": top["topic"] if top else None,
        })

    passed = sum(
        r["pest_ok"] and r["topic_ok"] and r["evidence_ok"]
        for r in results
    )

    return {
        "total": len(results),
        "passed": int(passed),
        "failed": len(results) - int(passed),
        "results": results,
    }




# ================================================================
# STEP 5.2 — TOPIC-SPECIFIC RETRIEVAL
# ================================================================

VALIDATED_TOPICS = [
    "identification",
    "symptoms",
    "favorable_conditions",
    "monitoring",
    "cultural_control",
    "biological_control",
    "mechanical_control",
    "chemical_control",
    "integrated_pest_management",
]


def retrieve_topic_evidence(
    pest,
    topics=None,
    top_k_per_topic=3,
):
    """
    Retrieve validated evidence separately for each requested topic.

    Important:
    - Does NOT modify FAISS.
    - Does NOT modify embeddings.
    - Excludes SOURCE_NOT_FOUND chunks.
    - Enforces pest + topic matching.
    - Deduplicates chunks.
    """

    _load()

    if topics is None:
        topics = VALIDATED_TOPICS.copy()

    # Normalize requested topics
    requested_topics = []

    for topic in topics:
        topic = str(topic).strip()

        if topic in VALIDATED_TOPICS:
            requested_topics.append(topic)

    # Remove duplicates while preserving order
    requested_topics = list(
        dict.fromkeys(requested_topics)
    )

    all_evidence = []
    seen_chunk_ids = set()

    topic_results = {}

    for topic in requested_topics:

        # Build a topic-specific query.
        query = f"{pest} rice {topic.replace('_', ' ')}"

        result = retrieve_rag_context(
            query=query,
            selected_pest=pest,
            top_k=max(top_k_per_topic * 4, 10),
        )

        matched = []

        for item in result["results"]:

            # Strict pest matching
            if item["pest_name"] != pest:
                continue

            # Strict topic matching
            if item["topic"] != topic:
                continue

            # Evidence must exist
            if not str(item.get("text", "")).strip():
                continue

            # Exclude duplicate chunks
            chunk_id = item["chunk_id"]

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(chunk_id)

            evidence_item = {
                "chunk_id": chunk_id,
                "pest_id": item["pest_id"],
                "pest_name": item["pest_name"],
                "topic": item["topic"],
                "text": item["text"],
                "semantic_score": float(
                    item["semantic_score"]
                ),
                "rerank_score": float(
                    item["rerank_score"]
                ),
                "sources": item.get(
                    "sources",
                    []
                ),
            }

            matched.append(evidence_item)
            all_evidence.append(evidence_item)

            if len(matched) >= top_k_per_topic:
                break

        topic_results[topic] = matched

    return {
        "pest": pest,
        "requested_topics": requested_topics,
        "topic_results": topic_results,
        "evidence": all_evidence,
        "evidence_count": len(all_evidence),
    }


def build_farmer_evidence_context(
    pest,
    topics=None,
    top_k_per_topic=1,
):
    """
    Build a clean evidence context for the advisory layer.

    Returns internal provenance separately from farmer-facing text.
    """

    result = retrieve_topic_evidence(
        pest=pest,
        topics=topics,
        top_k_per_topic=top_k_per_topic,
    )

    evidence_context = []

    for item in result["evidence"]:

        evidence_context.append({
            "topic": item["topic"],
            "text": item["text"],
        })

    return {
        "pest": result["pest"],
        "evidence": evidence_context,
        "provenance": result["evidence"],
        "evidence_count": result["evidence_count"],
    }


def topic_specific_rag_audit(
    pest,
    topics=None,
    top_k_per_topic=1,
):
    """
    Validate topic-specific retrieval.

    Pass criteria:
    - correct pest
    - correct topic
    - non-empty evidence
    - no SOURCE_NOT_FOUND chunks
    """

    if topics is None:
        topics = VALIDATED_TOPICS.copy()

    result = retrieve_topic_evidence(
        pest=pest,
        topics=topics,
        top_k_per_topic=top_k_per_topic,
    )

    topic_results = result["topic_results"]

    checks = []

    for topic in result["requested_topics"]:

        matches = topic_results.get(
            topic,
            []
        )

        if matches:

            for item in matches:

                pest_ok = (
                    item["pest_name"] == pest
                )

                topic_ok = (
                    item["topic"] == topic
                )

                text_ok = bool(
                    str(
                        item.get("text", "")
                    ).strip()
                )

                status_ok = True

                checks.append({
                    "topic": topic,
                    "chunk_id": item["chunk_id"],
                    "pest_ok": pest_ok,
                    "topic_ok": topic_ok,
                    "text_ok": text_ok,
                    "status_ok": status_ok,
                    "passed": (
                        pest_ok
                        and topic_ok
                        and text_ok
                        and status_ok
                    ),
                })

        else:

            # No evidence is a failure for normal topics.
            checks.append({
                "topic": topic,
                "chunk_id": None,
                "pest_ok": False,
                "topic_ok": False,
                "text_ok": False,
                "status_ok": False,
                "passed": False,
            })

    passed = sum(
        bool(x["passed"])
        for x in checks
    )

    total = len(checks)

    return {
        "pest": pest,
        "requested_topics": result[
            "requested_topics"
        ],
        "topic_results": topic_results,
        "evidence_count": result[
            "evidence_count"
        ],
        "checks": checks,
        "passed": passed,
        "total": total,
        "failed": total - passed,
        "status": (
            "PASSED"
            if total > 0
            and passed == total
            else "CHECK_REQUIRED"
        ),
    }




# ================================================================
# STEP 5.2.1 — STRICT TOPIC-FIRST RETRIEVAL
# ================================================================

def retrieve_topic_evidence_strict(
    pest,
    topics=None,
    top_k_per_topic=1,
):
    """
    Production-safe topic-specific retrieval.

    Uses the RAG engine's own loaded artifact state.
    Does not depend on notebook/global variables.
    """

    # -----------------------------------------------------------
    # Load RAG artifacts inside the function
    # -----------------------------------------------------------

    loaded = _load()

    # Some versions of _load() return the RAG object,
    # while others only populate module-level state.
    if loaded is not None:
        local_rag = loaded
    else:
        # Try known module-level RAG variables.
        local_rag = globals().get("rag")

        if local_rag is None:
            local_rag = globals().get("_RAG")

        if local_rag is None:
            raise RuntimeError(
                "RAG artifacts were not available after _load()."
            )

    # -----------------------------------------------------------
    # Requested topics
    # -----------------------------------------------------------

    if topics is None:
        topics = VALIDATED_TOPICS.copy()

    requested_topics = [
        topic
        for topic in topics
        if topic in VALIDATED_TOPICS
    ]

    requested_topics = list(
        dict.fromkeys(requested_topics)
    )

    # -----------------------------------------------------------
    # Resolve pest ID from validated chunks
    # -----------------------------------------------------------

    target_pest_id = None

    for chunk in local_rag["usable_chunks"]:

        chunk_pest = str(
            chunk.get(
                "pest_name",
                ""
            )
        ).strip().lower()

        if chunk_pest == str(
            pest
        ).strip().lower():

            target_pest_id = chunk.get(
                "pest_id"
            )

            break

    if target_pest_id is None:

        raise ValueError(
            f"Validated pest not found: {pest}"
        )

    # -----------------------------------------------------------
    # Retrieval
    # -----------------------------------------------------------

    all_evidence = []
    seen_chunk_ids = set()
    topic_results = {}

    for topic in requested_topics:

        matches = []

        # -------------------------------------------------------
        # A. Semantic retrieval
        # -------------------------------------------------------

        query = (
            f"{pest} rice "
            f"{topic.replace('_', ' ')}"
        )

        semantic_result = retrieve_rag_context(
            query=query,
            selected_pest=pest,
            top_k=max(
                top_k_per_topic * 6,
                12
            ),
        )

        for item in semantic_result[
            "results"
        ]:

            if item.get(
                "pest_name"
            ) != pest:
                continue

            if item.get(
                "topic"
            ) != topic:
                continue

            text = str(
                item.get(
                    "text",
                    ""
                )
            ).strip()

            if not text:
                continue

            chunk_id = item[
                "chunk_id"
            ]

            if chunk_id in seen_chunk_ids:
                continue

            evidence_item = {
                "chunk_id": chunk_id,
                "pest_id": item[
                    "pest_id"
                ],
                "pest_name": item[
                    "pest_name"
                ],
                "topic": item[
                    "topic"
                ],
                "text": text,
                "semantic_score": float(
                    item[
                        "semantic_score"
                    ]
                ),
                "rerank_score": float(
                    item[
                        "rerank_score"
                    ]
                ),
                "sources": item.get(
                    "sources",
                    []
                ),
                "retrieval_method": (
                    "semantic"
                ),
            }

            matches.append(
                evidence_item
            )

            seen_chunk_ids.add(
                chunk_id
            )

            if len(
                matches
            ) >= top_k_per_topic:

                break

        # -------------------------------------------------------
        # B. STRICT VALIDATED CHUNK FALLBACK
        # -------------------------------------------------------

        if len(
            matches
        ) < top_k_per_topic:

            for chunk in local_rag[
                "usable_chunks"
            ]:

                if (
                    chunk.get(
                        "pest_id"
                    )
                    != target_pest_id
                ):
                    continue

                if (
                    chunk.get(
                        "topic"
                    )
                    != topic
                ):
                    continue

                text = str(
                    chunk.get(
                        "text",
                        ""
                    )
                ).strip()

                if not text:
                    continue

                chunk_id = chunk[
                    "chunk_id"
                ]

                if chunk_id in seen_chunk_ids:
                    continue

                # Source extraction
                try:
                    sources = _extract_sources(
                        chunk
                    )
                except Exception:
                    sources = []

                fallback_item = {
                    "chunk_id": chunk_id,
                    "pest_id": chunk.get(
                        "pest_id"
                    ),
                    "pest_name": chunk.get(
                        "pest_name"
                    ),
                    "topic": chunk.get(
                        "topic"
                    ),
                    "text": text,
                    "semantic_score": 0.0,
                    "rerank_score": 1.0,
                    "sources": sources,
                    "retrieval_method": (
                        "validated_topic_fallback"
                    ),
                }

                matches.append(
                    fallback_item
                )

                seen_chunk_ids.add(
                    chunk_id
                )

                if len(
                    matches
                ) >= top_k_per_topic:

                    break

        topic_results[
            topic
        ] = matches

        all_evidence.extend(
            matches
        )

    return {
        "pest": pest,
        "pest_id": target_pest_id,
        "requested_topics": requested_topics,
        "topic_results": topic_results,
        "evidence": all_evidence,
        "evidence_count": len(
            all_evidence
        ),
    }


def strict_topic_rag_audit(
    pest,
    topics=None,
    top_k_per_topic=1,
):
    """
    Strict audit for topic-specific retrieval.
    """

    if topics is None:
        topics = VALIDATED_TOPICS.copy()

    result = retrieve_topic_evidence_strict(
        pest=pest,
        topics=topics,
        top_k_per_topic=top_k_per_topic,
    )

    checks = []

    for topic in result["requested_topics"]:

        matches = result[
            "topic_results"
        ].get(topic, [])

        if not matches:

            checks.append({
                "topic": topic,
                "chunk_id": None,
                "pest_ok": False,
                "topic_ok": False,
                "text_ok": False,
                "source_ok": False,
                "passed": False,
            })

            continue

        for item in matches:

            pest_ok = (
                item["pest_name"]
                == pest
            )

            topic_ok = (
                item["topic"]
                == topic
            )

            text_ok = bool(
                str(
                    item.get("text", "")
                ).strip()
            )

            # Chemical evidence must still have source metadata.
            source_ok = bool(
                item.get("sources")
            )

            passed = (
                pest_ok
                and topic_ok
                and text_ok
                and source_ok
            )

            checks.append({
                "topic": topic,
                "chunk_id": item[
                    "chunk_id"
                ],
                "pest_ok": pest_ok,
                "topic_ok": topic_ok,
                "text_ok": text_ok,
                "source_ok": source_ok,
                "retrieval_method": item.get(
                    "retrieval_method"
                ),
                "passed": passed,
            })

    passed = sum(
        bool(x["passed"])
        for x in checks
    )

    total = len(checks)

    return {
        "pest": pest,
        "checks": checks,
        "passed": passed,
        "total": total,
        "failed": total - passed,
        "status": (
            "PASSED"
            if total > 0
            and passed == total
            else "CHECK_REQUIRED"
        ),
    }

# ============================================================
# PRODUCTION TOPIC-SPECIFIC RETRIEVAL
# ============================================================

VALIDATED_TOPICS = [
    "identification",
    "symptoms",
    "favorable_conditions",
    "monitoring",
    "cultural_control",
    "biological_control",
    "mechanical_control",
    "chemical_control",
    "integrated_pest_management",
]


def retrieve_topic_evidence_explicit(
    rag,
    pest,
    topics,
    top_k_per_topic=1,
):
    """
    Production-safe topic-specific retrieval.

    For every requested topic:
      1. Try semantic retrieval.
      2. Prefer exact pest + exact topic matches.
      3. If semantic retrieval misses the exact pair,
         deterministically fall back to the validated chunk.
      4. Never return SOURCE_NOT_FOUND chunks.

    This function is intentionally self-contained so that
    Streamlit can execute it without relying on notebook globals.
    """

    # --------------------------------------------------------
    # Validate RAG state
    # --------------------------------------------------------
    if not isinstance(rag, dict):
        raise TypeError("rag must be the dictionary returned by load_rag()")

    chunks = rag.get("chunks", [])
    model = rag.get("model")
    index = rag.get("index")

    if model is None:
        raise RuntimeError("RAG embedding model is not loaded")

    if index is None:
        raise RuntimeError("FAISS index is not loaded")

    # --------------------------------------------------------
    # Normalize helpers
    # --------------------------------------------------------
    def norm(value):
        return str(value).strip().lower()

    pest_norm = norm(pest)

    requested_topics = [
        str(t).strip()
        for t in topics
        if str(t).strip() in VALIDATED_TOPICS
    ]

    results = []

    # --------------------------------------------------------
    # Helper: exact validated chunk
    # --------------------------------------------------------
    def exact_chunk(target_pest, target_topic):
        matches = []

        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue

            if chunk.get("status") == "SOURCE_NOT_FOUND":
                continue

            cp = norm(chunk.get("pest_name", ""))
            ct = norm(chunk.get("topic", ""))

            if cp == pest_norm and ct == norm(target_topic):
                text = str(chunk.get("text", "")).strip()

                if text:
                    matches.append(chunk)

        if not matches:
            return None

        # Deterministic selection
        matches.sort(
            key=lambda x: str(x.get("chunk_id", ""))
        )

        return matches[0]

    # --------------------------------------------------------
    # Retrieve topic-by-topic
    # --------------------------------------------------------
    for topic in requested_topics:

        topic_norm = norm(topic)

        # ----------------------------------------------------
        # Semantic query
        # ----------------------------------------------------
        query = f"{pest} rice {topic.replace('_', ' ')}"

        try:
            query_embedding = model.encode(
                [query],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )

            scores, indices = index.search(
                query_embedding,
                min(10, index.ntotal),
            )

            candidates = []

            for score, idx in zip(scores[0], indices[0]):

                if idx < 0 or idx >= len(chunks):
                    continue

                chunk = chunks[int(idx)]

                if not isinstance(chunk, dict):
                    continue

                if chunk.get("status") == "SOURCE_NOT_FOUND":
                    continue

                cp = norm(chunk.get("pest_name", ""))
                ct = norm(chunk.get("topic", ""))

                # Exact pest + topic gets strongest priority.
                pest_match = cp == pest_norm
                topic_match = ct == topic_norm

                rerank_score = float(score)

                if pest_match:
                    rerank_score += 0.30

                if topic_match:
                    rerank_score += 0.25

                if pest_match and topic_match:
                    rerank_score += 0.25

                candidates.append(
                    {
                        "chunk": chunk,
                        "semantic_score": float(score),
                        "rerank_score": rerank_score,
                        "pest_match": pest_match,
                        "topic_match": topic_match,
                    }
                )

            candidates.sort(
                key=lambda x: (
                    x["pest_match"] and x["topic_match"],
                    x["rerank_score"],
                ),
                reverse=True,
            )

        except Exception:
            candidates = []

        # ----------------------------------------------------
        # Prefer exact validated pest + topic
        # ----------------------------------------------------
        exact = None

        for item in candidates:
            if (
                item["pest_match"]
                and item["topic_match"]
            ):
                exact = item
                break

        # ----------------------------------------------------
        # Deterministic fallback if semantic search misses it
        # ----------------------------------------------------
        if exact is None:

            fallback = exact_chunk(
                pest,
                topic,
            )

            if fallback is not None:

                exact = {
                    "chunk": fallback,
                    "semantic_score": None,
                    "rerank_score": None,
                    "pest_match": True,
                    "topic_match": True,
                    "fallback": True,
                }

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------
        if exact is not None:

            chunk = exact["chunk"]

            results.append(
                {
                    "topic": topic,
                    "chunk_id": chunk.get("chunk_id"),
                    "pest_id": chunk.get("pest_id"),
                    "pest_name": chunk.get("pest_name"),
                    "topic_name": chunk.get("topic"),
                    "status": chunk.get("status"),
                    "text": chunk.get("text"),
                    "semantic_score": exact.get(
                        "semantic_score"
                    ),
                    "rerank_score": exact.get(
                        "rerank_score"
                    ),
                    "fallback_used": bool(
                        exact.get("fallback", False)
                    ),
                    "source_metadata": chunk.get(
                        "source_metadata",
                        {},
                    ),
                }
            )

    # --------------------------------------------------------
    # Return production result
    # --------------------------------------------------------
    return {
        "pest": pest,
        "requested_topics": requested_topics,
        "results": results,
        "coverage": {
            "requested": len(requested_topics),
            "retrieved": len(results),
            "missing": [
                topic
                for topic in requested_topics
                if not any(
                    r["topic"] == topic
                    for r in results
                )
            ],
        },
    }
