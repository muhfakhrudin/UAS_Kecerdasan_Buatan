"""
TF-IDF + Cosine Similarity baseline — comparison method for the Okapi BM25
recommender implemented in search_engine.py.

This module is intentionally separate from search_engine.py: BM25 remains
the sole ranking method used by the Django search view (views.py). This
baseline is only invoked from the offline evaluation harness
(eval/run_experiment.py) to produce the BM25-vs-TF-IDF comparison table.

It reuses the exact same preprocessing pipeline as BM25
(recommender.preprocessing.preprocess) and the exact same dataset loader
(recommender.search_engine.load_products) — imported, not duplicated — so
that any ranking difference between the two methods reflects the ranking
algorithm itself, not divergent text handling or data loading.

Design decision — stdlib only, no scikit-learn: the task brief allows
scikit-learn specifically for this baseline (it isn't the core research
method), but it is implemented here with pure Python standard library
(math, collections) instead, to stay consistent with the project's
overall "no third-party ML framework" posture (KNF-1) applied project-wide
rather than only to BM25. See AUDIT_REPORT.md (Tahap 4) for the reasoning.

Formulas (standard/raw TF-IDF, natural-log IDF):
    TF(t, d)      = f(t, d)                      raw term frequency of t in d
    IDF(t)        = ln(N / df(t))                 N = corpus size, df(t) = doc count containing t
    weight(t, d)  = TF(t, d) * IDF(t)
    cosine(q, d)  = (q . d) / (||q|| * ||d||)

A query term with df(t) = 0 (never appears anywhere in the corpus) cannot
contribute to any document's dot product by definition, so — to avoid a
division-by-zero in ln(N / 0) — such terms are simply given weight 0
rather than introducing smoothing the task brief did not specify. This
does not change the ranking: a term absent from every document can never
distinguish one document's score from another's.
"""

import math
from collections import Counter

from .preprocessing import preprocess


def _corpus_document_frequencies(doc_tokens_list):
    """Compute df(t) — the number of documents containing term t — for every term in the corpus."""
    df = Counter()
    for tokens in doc_tokens_list:
        for term in set(tokens):
            df[term] += 1
    return df


def calculate_tfidf_cosine_scores(query, products):
    """
    Rank products against a query using raw TF-IDF weighting and Cosine Similarity.

    Args:
        query (str): The user's search query string.
        products (list[dict]): List of product dictionaries, each containing
                                a 'search_content' key (see search_engine.load_products).

    Returns:
        list[tuple[dict, float]]: (product, cosine_score) tuples for all
                                   products, sorted by score descending.
    """
    if not query or not products:
        return [(p, 0.0) for p in products]

    query_tokens = preprocess(query)
    if not query_tokens:
        return [(p, 0.0) for p in products]

    N = len(products)
    doc_tokens_list = [preprocess(p['search_content']) for p in products]
    df = _corpus_document_frequencies(doc_tokens_list)

    def idf(term):
        n_t = df.get(term, 0)
        if n_t == 0:
            return None
        return math.log(N / n_t)

    # ── Query TF-IDF vector (terms absent from the whole corpus get weight 0) ──
    query_tf = Counter(query_tokens)
    query_vec = {}
    for term, tf in query_tf.items():
        term_idf = idf(term)
        if term_idf is not None:
            query_vec[term] = tf * term_idf
    query_norm = math.sqrt(sum(w * w for w in query_vec.values()))

    scores = []
    for product, doc_tokens in zip(products, doc_tokens_list):
        if query_norm == 0 or not doc_tokens:
            scores.append((product, 0.0))
            continue

        # Full document TF-IDF vector is required for a correct ||d|| norm —
        # not just the terms shared with the query.
        doc_tf = Counter(doc_tokens)
        doc_vec = {term: tf * idf(term) for term, tf in doc_tf.items()}
        doc_norm = math.sqrt(sum(w * w for w in doc_vec.values()))

        if doc_norm == 0:
            scores.append((product, 0.0))
            continue

        dot = sum(
            query_vec[term] * weight
            for term, weight in doc_vec.items()
            if term in query_vec
        )
        cosine = dot / (query_norm * doc_norm)
        scores.append((product, round(cosine, 4)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
