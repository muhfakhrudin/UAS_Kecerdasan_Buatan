"""
Views for the Smart IRecom recommender application.

- search_view (`/`): the main search page. Every query is run through
  BOTH Okapi BM25 (the system's actual ranking method) and the TF-IDF +
  Cosine Similarity baseline, always, so visitors see a live side-by-side
  comparison without needing to opt in.
- compare_view (`/evaluasi/`): a single-query demo comparison. The user
  types exactly one query and sees BM25 vs TF-IDF + Cosine Similarity
  ranked side by side, live.
- multi_query_evaluation_view (`/evaluasi/multi-query/`): a user-driven
  demo across exactly 5 manually-typed queries at once, averaging
  Precision/Recall/Hit Rate/NDCG@10 across them. An experiment the visitor
  runs themselves — distinct from the paper's fixed-query numbers, which
  are produced separately by `python manage.py run_evaluation`
  (recommender/evaluation.py's run_evaluation()) and are not exposed as a
  page in this app.

Both comparison views auto-derive ground truth per typed query via
recommender/evaluation.py's parse_query_constraints(), so
Precision/Recall/Hit Rate/NDCG can be shown when possible — a query with
no recognizable structured terms gets no metrics, shown as an explicit
notice rather than a fabricated 0. Both share _evaluate_query() below so
the ranking/metrics logic exists in exactly one place.
"""

import re
import time
from collections import Counter

from django.shortcuts import render

from .evaluation import (
    _matches,
    hit_rate_at_k,
    ndcg_at_k,
    parse_query_constraints,
    precision_at_k,
    recall_at_k,
    validate_catalog_query,
)
from .ranking import rank_products
from .search_engine import calculate_bm25_scores, load_products
from .tfidf_engine import calculate_tfidf_cosine_scores


def search_view(request):
    """
    Handle the main search page and AI-powered product search.

    Processes GET requests with an optional 'q' query parameter. When a
    query is present, loads all products from the CSV dataset and ranks
    them with BOTH BM25 and TF-IDF + Cosine Similarity through the
    identical threshold/filter/sort pipeline (recommender/ranking.py), so
    the two methods are only ever compared on ranking, never on
    diverging filter logic.

    Returns:
        HttpResponse: Rendered search.html template with context containing:
            - query (str): The user's search query
            - results / tfidf_results (list[tuple[dict, float]]): Ranked (product, score) tuples
            - total_results / tfidf_total_results (int): Matching product counts
            - total_scanned (int): Total products scanned in the database
            - execution_time / tfidf_execution_time (str): Ranking latency in seconds
            - max_score / tfidf_max_score (float): Highest score, for score bar normalization
            - query_tokens (list[str]): Tokenized query words for highlighting
    """
    query = request.GET.get('q', '').strip()

    # Filter parameters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_battery = request.GET.get('min_battery', '')
    category = request.GET.get('category', 'all')
    platform = request.GET.get('platform', 'all')
    sort_by = request.GET.get('sort', 'relevance')

    results = []
    tfidf_results = []
    total_found = 0
    tfidf_total_found = 0
    total_scanned = 0
    execution_time = 0.0
    tfidf_execution_time = 0.0
    query_tokens = set()
    validation_message = None

    if query:
        query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))

        products = load_products()
        total_scanned = len(products)

        validation = validate_catalog_query(query, products)
        if not validation['valid']:
            validation_message = validation['message']
        else:
            start_time = time.time()
            results, total_found = rank_products(
                calculate_bm25_scores, query, products, query_tokens,
                min_price, max_price, min_battery, category, platform, sort_by,
            )
            execution_time = time.time() - start_time

            start_time = time.time()
            tfidf_results, tfidf_total_found = rank_products(
                calculate_tfidf_cosine_scores, query, products, query_tokens,
                min_price, max_price, min_battery, category, platform, sort_by,
            )
            tfidf_execution_time = time.time() - start_time

    context = {
        'validation_message': validation_message,
        'query': query,
        'results': results,
        'total_results': total_found if query else 0,
        'total_displayed': len(results),
        'total_scanned': total_scanned,
        'execution_time': f"{execution_time:.4f}",
        'max_score': results[0][1] if results else 0,
        'query_tokens': list(query_tokens),
        # Pass filters back to template to keep state
        'min_price': min_price,
        'max_price': max_price,
        'min_battery': min_battery,
        'category': category,
        'platform': platform,
        'sort_by': sort_by,
        # TF-IDF comparison panel (always computed, qualitative — no ground-truth metrics)
        'tfidf_results': tfidf_results,
        'tfidf_total_results': tfidf_total_found if query else 0,
        'tfidf_execution_time': f"{tfidf_execution_time:.4f}",
        'tfidf_max_score': tfidf_results[0][1] if tfidf_results else 0,
    }

    return render(request, 'recommender/search.html', context)


_CONSTRAINT_LABELS = {
    'kategori_varian': 'varian',
    'penyimpanan': 'storage',
    'platform': 'platform',
    'kategori_iphone': 'kategori',
    'wilayah_contains': 'wilayah',
    'min_battery': 'battery ≥',
}


def _format_constraints(constraints):
    """Render a parsed constraints dict as a short human-readable string for display."""
    return ', '.join(f"{_CONSTRAINT_LABELS.get(k, k)}: {v}" for k, v in constraints.items())


METRIC_METHODS = ('Okapi BM25', 'TF-IDF + Cosine Similarity')


def _evaluate_query(query, products):
    """
    Rank `query` with both BM25 and TF-IDF and, when possible, derive
    ground truth and Precision/Recall/Hit Rate/NDCG@10 for it.

    Shared by compare_view (1 query) and multi_query_evaluation_view (5
    queries) so the ranking/metrics logic lives in exactly one place.

    Before ranking, validate_catalog_query() checks whether an explicitly
    requested model/storage actually exists in the dataset (e.g. "iPhone
    16" — BM25 would otherwise still return near-zero-score matches just
    from the shared "iphone" token). When it doesn't, ranking is skipped
    entirely and both result lists come back empty, with 'validation_message'
    set to an explanatory notice instead of 'metrics'.

    Returns:
        dict: {
            'query': str,
            'bm25_results' / 'tfidf_results': list[tuple[dict, float]] (top 10),
            'bm25_time' / 'tfidf_time': float, ranking latency in seconds,
            'metrics': dict or None — None when no structured attributes
                (variant/storage/platform/battery/region) could be detected
                in the query text, i.e. no ground truth is derivable.
            'validation_message': str or None — set (and 'metrics' left
                None) when the query explicitly names a model/storage the
                dataset doesn't have, so ranking never even ran.
        }
    """
    validation = validate_catalog_query(query, products)
    if not validation['valid']:
        return {
            'query': query,
            'bm25_results': [],
            'bm25_time': 0.0,
            'tfidf_results': [],
            'tfidf_time': 0.0,
            'metrics': None,
            'validation_message': validation['message'],
        }

    query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))

    start_time = time.time()
    bm25_results, _ = rank_products(calculate_bm25_scores, query, products, query_tokens, top_n=10)
    bm25_time = time.time() - start_time

    start_time = time.time()
    tfidf_results, _ = rank_products(calculate_tfidf_cosine_scores, query, products, query_tokens, top_n=10)
    tfidf_time = time.time() - start_time

    constraints = parse_query_constraints(query, products)
    metrics = None
    if constraints:
        relevant_ids = [p['doc_id'] for p in products if _matches(p, constraints)]
        per_method = {
            'Okapi BM25': [p['doc_id'] for p, _ in bm25_results],
            'TF-IDF + Cosine Similarity': [p['doc_id'] for p, _ in tfidf_results],
        }
        metrics = {
            'constraints_display': _format_constraints(constraints),
            'num_relevant': len(relevant_ids),
            'methods': {
                method_name: {
                    'precision_at_k': precision_at_k(doc_ids, relevant_ids),
                    'recall_at_k': recall_at_k(doc_ids, relevant_ids),
                    'hit_rate_at_k': hit_rate_at_k(doc_ids, relevant_ids),
                    'ndcg_at_k': ndcg_at_k(doc_ids, relevant_ids),
                }
                for method_name, doc_ids in per_method.items()
            },
        }

    return {
        'query': query,
        'bm25_results': bm25_results,
        'bm25_time': bm25_time,
        'tfidf_results': tfidf_results,
        'tfidf_time': tfidf_time,
        'metrics': metrics,
        'validation_message': None,
    }


def compare_view(request):
    """
    Single-query BM25 vs TF-IDF demo comparison at /evaluasi/.

    Accepts exactly one 'query' GET param and ranks it with both methods
    via _evaluate_query(), computed fresh on every request.
    """
    query = request.GET.get('query', '').strip()

    total_scanned = 0
    result = None

    if query:
        products = load_products()
        total_scanned = len(products)
        evaluated = _evaluate_query(query, products)
        result = {
            **evaluated,
            'bm25_time': f"{evaluated['bm25_time']:.4f}",
            'tfidf_time': f"{evaluated['tfidf_time']:.4f}",
        }

    context = {
        'query': query,
        'total_scanned': total_scanned,
        'result': result,
    }
    return render(request, 'recommender/evaluation.html', context)


MULTI_QUERY_COUNT = 5


def multi_query_evaluation_view(request):
    """
    Multi-query BM25 vs TF-IDF demo at /evaluasi/multi-query/.

    Accepts exactly MULTI_QUERY_COUNT (5) named GET params 'query1'..
    'query5' (a 'submitted' marker distinguishes a fresh page load from a
    submission with empty fields). Each query is ranked via the same
    _evaluate_query() compare_view uses, which also gates each one through
    validate_catalog_query() — a query naming a model/storage the dataset
    doesn't have gets a validation notice instead of ranking, and is
    excluded from every average below (Precision/Recall/Hit Rate/NDCG@10
    AND execution time), never padding in a fabricated 0/result for it.
    Among the remaining ranked queries, Precision/Recall/Hit Rate/NDCG@10
    are further averaged only over those with derivable ground truth (same
    rule as compare_view and the paper's run_evaluation()).

    This is a visitor-run experiment, not the paper's official numbers —
    the template labels it explicitly as a demo.
    """
    field_names = [f'query{i}' for i in range(1, MULTI_QUERY_COUNT + 1)]
    submitted = 'submitted' in request.GET
    raw_values = [request.GET.get(name, '').strip() for name in field_names]
    query_inputs = [
        {'name': name, 'label': f'Query {i}', 'value': value}
        for i, (name, value) in enumerate(zip(field_names, raw_values), start=1)
    ]

    error = None
    result = None

    if submitted:
        non_empty = [q for q in raw_values if q]
        if len(non_empty) != MULTI_QUERY_COUNT:
            error = 'Masukkan 5 query untuk menjalankan evaluasi multi-query.'
        else:
            products = load_products()
            total_scanned = len(products)

            query_results = []
            summary_totals = {method: Counter() for method in METRIC_METHODS}
            time_totals_ms = {method: 0.0 for method in METRIC_METHODS}
            num_with_ground_truth = 0
            num_valid = 0

            for query in non_empty:
                evaluated = _evaluate_query(query, products)

                if evaluated['validation_message']:
                    # Explicitly requested model/storage doesn't exist —
                    # ranking never ran, so this query is excluded from
                    # every average below (metrics AND execution time).
                    query_results.append({
                        'query': query,
                        'bm25_results': [],
                        'bm25_time_ms': None,
                        'tfidf_results': [],
                        'tfidf_time_ms': None,
                        'metrics': None,
                        'validation_message': evaluated['validation_message'],
                    })
                    continue

                num_valid += 1
                time_totals_ms['Okapi BM25'] += evaluated['bm25_time'] * 1000
                time_totals_ms['TF-IDF + Cosine Similarity'] += evaluated['tfidf_time'] * 1000

                if evaluated['metrics']:
                    num_with_ground_truth += 1
                    for method, method_metrics in evaluated['metrics']['methods'].items():
                        for key, value in method_metrics.items():
                            summary_totals[method][key] += value

                query_results.append({
                    'query': query,
                    'bm25_results': evaluated['bm25_results'],
                    'bm25_time_ms': f"{evaluated['bm25_time'] * 1000:.2f}",
                    'tfidf_results': evaluated['tfidf_results'],
                    'tfidf_time_ms': f"{evaluated['tfidf_time'] * 1000:.2f}",
                    'metrics': evaluated['metrics'],
                    'validation_message': None,
                })

            summary = None
            if num_with_ground_truth > 0:
                summary = {
                    method: {
                        **{
                            key: summary_totals[method][key] / num_with_ground_truth
                            for key in ('precision_at_k', 'recall_at_k', 'hit_rate_at_k', 'ndcg_at_k')
                        },
                        'avg_time_ms': time_totals_ms[method] / num_valid,
                    }
                    for method in METRIC_METHODS
                }

            result = {
                'total_scanned': total_scanned,
                'query_results': query_results,
                'num_with_ground_truth': num_with_ground_truth,
                'num_valid': num_valid,
                'summary': summary,
            }

    context = {
        'query_inputs': query_inputs,
        'submitted': submitted,
        'error': error,
        'result': result,
        'num_queries': MULTI_QUERY_COUNT,
    }
    return render(request, 'recommender/multi_query_evaluation.html', context)
