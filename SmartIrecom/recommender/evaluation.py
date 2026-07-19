"""
Evaluation harness comparing Okapi BM25 (search_engine.py) against the
TF-IDF + Cosine Similarity baseline (tfidf_engine.py).

This is a real part of the `recommender` Django app — not a standalone
script — used by `python manage.py run_evaluation`
(recommender/management/commands/run_evaluation.py) to produce the
quantitative Precision/Recall/Hit Rate/NDCG table for the paper
(eval/results.md, eval/results.csv, eval/ground_truth.json).

/evaluasi/ (views.compare_view) also uses this module: via
parse_query_constraints() below, it tries to auto-detect the same
kind of structured constraints (variant/storage/platform/battery/region)
directly from whatever free-text query a visitor types, by matching
against the real distinct values in the currently-loaded dataset. When
that succeeds, ground truth — and therefore real Precision/Recall/Hit
Rate/NDCG — can be computed for that ad-hoc query too, using the exact
same _matches() AND-semantics as the curated queries (methodologically
identical rigor, just with automatically- rather than manually-written
constraints). When a query has no recognizable structured terms (e.g.
pure natural language with no matching variant/storage/platform/etc.),
no ground truth can be derived and no metrics are shown for it — this is
flagged explicitly in the UI, never silently defaulted to zero.

Ground truth (relevance judgments):
    Built deterministically from the real dataset (dataset_iphone.csv) by
    QUERY_CONSTRAINTS below — a product is RELEVANT to a query iff it
    satisfies ALL of that query's explicit constraints (AND semantics),
    matched against the same raw product attributes the app's own hard
    filters use (recommender/views.py): variant, storage, platform,
    region substring, certification category, battery-health lower bound.
    No relevance judgment is hand-typed; build_ground_truth() derives the
    relevant document IDs by filtering the real, currently-loaded products.

Metrics (Tahap 5): Precision@10, Recall@10, Hit Rate@10 (required),
NDCG@10 (optional, implemented). MAP/MRR intentionally not implemented.
"""

import math
import re
import time
from collections import Counter

from .search_engine import calculate_bm25_scores, load_products
from .tfidf_engine import calculate_tfidf_cosine_scores

K = 10

# Each query's constraints are matched against the exact product dict keys
# produced by search_engine.load_products(). Verified against the real
# dataset to each have a non-empty relevant set. Kept deliberately small
# (5) while still covering each constraint type used by _matches():
# variant+storage, +platform, +battery threshold, +region, +certification.
QUERY_CONSTRAINTS = [
    ('iPhone 11 64GB', dict(kategori_varian='iPhone 11', penyimpanan='64GB')),
    ('iPhone 12 128GB Shopee', dict(kategori_varian='iPhone 12', penyimpanan='128GB', platform='Shopee')),
    ('iPhone 13 Pro battery diatas 90', dict(kategori_varian='iPhone 13 Pro', min_battery=90)),
    ('iPhone 11 Pro 256GB Jakarta', dict(kategori_varian='iPhone 11 Pro', penyimpanan='256GB', wilayah_contains='Jakarta')),
    ('iPhone 12 Pro 128GB Resmi', dict(kategori_varian='iPhone 12 Pro', penyimpanan='128GB', kategori_iphone='Resmi')),
]

RELEVANCE_CRITERIA = (
    "A product is relevant to a query iff it satisfies ALL explicit constraints "
    "listed for that query (AND semantics), matched against the raw product "
    "attributes from dataset_iphone.csv (kategori_varian, penyimpanan, platform, "
    "wilayah_toko substring, kategori_iphone, battery_val >= threshold). Derived "
    "deterministically from the real, currently-loaded dataset — no relevance "
    "judgment is hand-typed."
)


def _matches(product, constraints):
    for key, expected in constraints.items():
        if key == 'wilayah_contains':
            if expected.lower() not in product['wilayah_toko'].lower():
                return False
        elif key == 'min_battery':
            batt = product.get('battery_val')
            if batt is None or batt < expected:
                return False
        else:
            if product.get(key, '') != expected:
                return False
    return True


def build_ground_truth(products):
    """Derive {query: [relevant doc_ids]} from the real dataset via QUERY_CONSTRAINTS."""
    ground_truth = []
    for query, constraints in QUERY_CONSTRAINTS:
        relevant_ids = [p['doc_id'] for p in products if _matches(p, constraints)]
        ground_truth.append({
            'query': query,
            'constraints': constraints,
            'relevant_doc_ids': relevant_ids,
        })
    return ground_truth


# ─── Ad-hoc ground truth: parse constraints out of a free-typed query ──────

_BATTERY_RE = re.compile(r'(?:battery|baterai)\D{0,12}(\d{2,3})')


def _distinct_values(products, key):
    """Ordered, de-duplicated list of the real values a product field actually takes."""
    seen = []
    for p in products:
        v = p.get(key, '')
        if v and v not in seen:
            seen.append(v)
    return seen


def parse_query_constraints(query, products):
    """
    Try to extract structured constraints from a free-typed query by
    matching it against the real distinct attribute values present in the
    currently-loaded dataset — the same schema _matches()/QUERY_CONSTRAINTS
    use (kategori_varian, penyimpanan, platform, kategori_iphone,
    wilayah_contains, min_battery).

    Matching is substring-based on the lowercased query, longest candidate
    first per field (so "iPhone 12 Pro Max" is preferred over "iPhone 12"
    when both would otherwise match). Fields with no match are simply
    omitted from the returned dict; an empty dict means nothing recognizable
    was found and no ground truth can be derived for this query.

    Returns:
        dict: constraints dict, possibly empty.
    """
    q_lower = query.lower()
    constraints = {}

    varian_values = sorted(_distinct_values(products, 'kategori_varian'), key=len, reverse=True)
    for v in varian_values:
        if v.lower() in q_lower:
            constraints['kategori_varian'] = v
            break

    storage_values = sorted(_distinct_values(products, 'penyimpanan'), key=len, reverse=True)
    for s in storage_values:
        if s.lower() in q_lower:
            constraints['penyimpanan'] = s
            break

    for plat in _distinct_values(products, 'platform'):
        if plat.lower() in q_lower:
            constraints['platform'] = plat
            break

    for cat in _distinct_values(products, 'kategori_iphone'):
        if cat.lower() in q_lower:
            constraints['kategori_iphone'] = cat
            break

    wilayah_values = sorted(_distinct_values(products, 'wilayah_toko'), key=len, reverse=True)
    for wil in wilayah_values:
        if wil.lower() in q_lower:
            constraints['wilayah_contains'] = wil
            break

    battery_match = _BATTERY_RE.search(q_lower)
    if battery_match:
        constraints['min_battery'] = int(battery_match.group(1))

    return constraints


# ─── Catalog validation: reject explicit model/storage requests the ────────
# ─── dataset genuinely has nothing for, before they ever reach ranking. ────

# "iphone" + a model number, optionally followed by one variant modifier
# word ("Pro Max" / "Pro" / "Mini" / ...). Requires a real space before the
# modifier (and a word boundary after it) so it can't grab a fragment out of
# an unrelated following word (e.g. "iPhone 11 processor").
_VARIANT_QUERY_RE = re.compile(
    r'iphone\s*(\d+)(?:\s+(pro\s*max|pro|mini|max|plus|se)\b)?',
    re.IGNORECASE,
)
_STORAGE_QUERY_RE = re.compile(r'\b(\d+)\s*(gb|tb)\b', re.IGNORECASE)

_VARIANT_MODIFIER_TITLES = {
    'pro max': 'Pro Max',
    'pro': 'Pro',
    'mini': 'Mini',
    'max': 'Max',
    'plus': 'Plus',
    'se': 'SE',
}


def validate_catalog_query(query, products):
    """
    Check whether an EXPLICIT iPhone model and/or storage capacity typed in
    `query` actually exists in the dataset, before any ranking runs.

    This exists because BM25 partially matches on generic tokens: a query
    like "iPhone 16" still scores nonzero against real "iPhone 11/12/13"
    listings purely because they all share the token "iphone", even though
    the model itself doesn't exist in the catalog at all. TF-IDF's stricter
    weighting already returns nothing for such queries; this makes BM25
    agree instead of surfacing near-zero-score matches as if they were real
    recommendations.

    Only explicit, structured mentions are checked (a model number right
    after "iphone", or a number immediately followed by "GB"/"TB") — never
    free-text words with no catalog meaning, so "iPhone 11 murah" still
    matches "iPhone 11" fine; "murah" simply isn't a recognized attribute.

    Args:
        query (str): The raw, untokenized search query.
        products (list[dict]): Product dicts from search_engine.load_products().

    Returns:
        dict: {'valid': bool, 'message': str | None} — message is only set
            when valid is False, in Indonesian, ready to show to the user.
    """
    variant_values = _distinct_values(products, 'kategori_varian')
    storage_values = _distinct_values(products, 'penyimpanan')
    variant_lookup = {v.lower() for v in variant_values}
    storage_lookup = {s.lower() for s in storage_values}

    variant_match = _VARIANT_QUERY_RE.search(query)
    requested_variant = None
    if variant_match:
        number = variant_match.group(1)
        modifier_raw = re.sub(r'\s+', ' ', (variant_match.group(2) or '').strip().lower())
        modifier_title = _VARIANT_MODIFIER_TITLES.get(modifier_raw, '')
        requested_variant = f"iPhone {number}" + (f" {modifier_title}" if modifier_title else '')

        if requested_variant.lower() not in variant_lookup:
            number_exists = any(
                re.match(rf'iphone\s*{re.escape(number)}\b', v, re.IGNORECASE)
                for v in variant_values
            )
            if not number_exists:
                return {'valid': False, 'message': f"iPhone {number} tidak tersedia pada dataset."}
            return {'valid': False, 'message': f"{requested_variant} tidak tersedia pada dataset."}

    storage_match = _STORAGE_QUERY_RE.search(query)
    if storage_match:
        value, unit = storage_match.groups()
        requested_storage = f"{value}{unit.upper()}"
        if requested_storage.lower() not in storage_lookup:
            if requested_variant:
                return {
                    'valid': False,
                    'message': f"Varian {requested_variant} dengan storage {requested_storage} tidak tersedia pada dataset.",
                }
            return {'valid': False, 'message': f"Storage {requested_storage} tidak tersedia pada dataset."}

    return {'valid': True, 'message': None}


# ─── Metrics (Tahap 5) ──────────────────────────────────────────────────────

def precision_at_k(ranked_doc_ids, relevant_doc_ids, k=K):
    relevant_set = set(relevant_doc_ids)
    top_k = ranked_doc_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / k


def recall_at_k(ranked_doc_ids, relevant_doc_ids, k=K):
    relevant_set = set(relevant_doc_ids)
    if not relevant_set:
        return 0.0
    top_k = ranked_doc_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)
    return hits / len(relevant_set)


def hit_rate_at_k(ranked_doc_ids, relevant_doc_ids, k=K):
    relevant_set = set(relevant_doc_ids)
    top_k = ranked_doc_ids[:k]
    return 1.0 if any(doc_id in relevant_set for doc_id in top_k) else 0.0


def ndcg_at_k(ranked_doc_ids, relevant_doc_ids, k=K):
    """Binary-relevance NDCG@k: DCG@k = sum rel_i / log2(i+1), normalized by the ideal ranking's DCG@k."""
    relevant_set = set(relevant_doc_ids)
    if not relevant_set:
        return 0.0

    top_k = ranked_doc_ids[:k]
    dcg = sum(
        1.0 / math.log2(i + 2)
        for i, doc_id in enumerate(top_k)
        if doc_id in relevant_set
    )
    ideal_hits = min(len(relevant_set), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


# ─── Experiment runner ──────────────────────────────────────────────────────

METHODS = {
    'TF-IDF + Cosine Similarity': calculate_tfidf_cosine_scores,
    'Okapi BM25': calculate_bm25_scores,
}


def run_evaluation(k=K):
    """
    Run every query in QUERY_CONSTRAINTS through both BM25 and TF-IDF,
    score each with Precision/Recall/Hit Rate/NDCG @k, and average.

    Returns:
        dict: {
            'k': int,
            'num_queries': int,
            'num_products': int,
            'relevance_criteria': str,
            'per_query': [ { 'query': str, 'results': {method: {metrics..., 'query_time_ms': float}} } ],
            'summary': { method: { averaged metrics..., 'avg_query_time_ms': float } },
        }
    """
    products = load_products()
    ground_truth = build_ground_truth(products)

    per_query = []
    totals = {method: Counter() for method in METHODS}

    for entry in ground_truth:
        query = entry['query']
        relevant_ids = entry['relevant_doc_ids']
        query_result = {'query': query, 'num_relevant': len(relevant_ids), 'results': {}}

        for method_name, score_fn in METHODS.items():
            start = time.perf_counter()
            scored = score_fn(query, products)
            elapsed_ms = (time.perf_counter() - start) * 1000

            ranked_doc_ids = [p['doc_id'] for p, score in scored if score > 0][:k]

            metrics = {
                'precision_at_k': precision_at_k(ranked_doc_ids, relevant_ids, k),
                'recall_at_k': recall_at_k(ranked_doc_ids, relevant_ids, k),
                'hit_rate_at_k': hit_rate_at_k(ranked_doc_ids, relevant_ids, k),
                'ndcg_at_k': ndcg_at_k(ranked_doc_ids, relevant_ids, k),
                'query_time_ms': elapsed_ms,
            }
            query_result['results'][method_name] = metrics

            for key, value in metrics.items():
                totals[method_name][key] += value

        per_query.append(query_result)

    num_queries = len(ground_truth)
    summary = {}
    for method_name in METHODS:
        summary[method_name] = {
            'precision_at_k': totals[method_name]['precision_at_k'] / num_queries,
            'recall_at_k': totals[method_name]['recall_at_k'] / num_queries,
            'hit_rate_at_k': totals[method_name]['hit_rate_at_k'] / num_queries,
            'ndcg_at_k': totals[method_name]['ndcg_at_k'] / num_queries,
            'avg_query_time_ms': totals[method_name]['query_time_ms'] / num_queries,
        }

    return {
        'k': k,
        'num_queries': num_queries,
        'num_products': len(products),
        'relevance_criteria': RELEVANCE_CRITERIA,
        'per_query': per_query,
        'summary': summary,
    }
