"""
Views for the Smart IRecom recommender application.

- search_view (`/`): the main search page. Every query is run through
  BOTH Okapi BM25 (the system's actual ranking method) and the TF-IDF +
  Cosine Similarity baseline, always, so visitors see a live side-by-side
  comparison without needing to opt in.
- compare_view (`/evaluasi/`): a focused, filter-free version of the same
  live comparison, for exhibition/demo purposes. Tries to auto-derive
  ground truth for each typed query (recommender/evaluation.py's
  parse_query_constraints) so Precision/Recall/Hit Rate/NDCG can be shown
  when possible — but a query with no recognizable structured terms gets
  no metrics, shown as an explicit notice rather than a fabricated 0.
- paper_evaluation_view (`/evaluasi/paper/`): the actual quantitative
  evaluation — 14 labeled ground-truth queries, Precision/Recall/Hit
  Rate/NDCG, averaged — the official numbers for the paper's Table II.
  Uses recommender/evaluation.py's run_evaluation(), the same function
  `python manage.py run_evaluation` uses, so the page and the CLI/report
  output can never drift apart.
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
    run_evaluation,
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

    if query:
        query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))

        products = load_products()
        total_scanned = len(products)

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


MAX_COMPARE_QUERIES = 10  # cap so a pasted wall of text can't stall the page


METRIC_METHODS = ('Okapi BM25', 'TF-IDF + Cosine Similarity')

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


def compare_view(request):
    """
    Live, filter-free BM25 vs TF-IDF comparison at /evaluasi/.

    Accepts multiple 'query' GET params (one per dynamically-added input
    box in the template — NOT one big textarea, so each query is its own
    field), up to MAX_COMPARE_QUERIES, and ranks each with both methods,
    computed fresh on every request — not limited to a fixed query set.

    For each query, recommender.evaluation.parse_query_constraints() tries
    to auto-detect structured attributes (variant/storage/platform/
    battery/region) directly from the typed text, matched against the
    real dataset. When that succeeds, ground truth is derived with the
    same AND-semantics as the 14 curated paper queries, so real
    Precision@10/Recall@10/Hit Rate@10/NDCG@10 can be shown for that
    query too — and averaged into a "Ringkasan" across every query that
    got ground truth. A query with no recognizable structured terms gets
    no metrics (flagged explicitly in the template, never a fabricated
    0). The 14-query official paper numbers still live separately at
    paper_evaluation_view (/evaluasi/paper/), linked from this page.
    """
    submitted_queries = [q.strip() for q in request.GET.getlist('query') if q.strip()]
    queries = submitted_queries[:MAX_COMPARE_QUERIES]

    total_scanned = 0
    query_results = []
    summary_totals = {method: Counter() for method in METRIC_METHODS}
    num_with_ground_truth = 0

    if queries:
        products = load_products()
        total_scanned = len(products)

        for query in queries:
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
                bm25_doc_ids = [p['doc_id'] for p, _ in bm25_results]
                tfidf_doc_ids = [p['doc_id'] for p, _ in tfidf_results]

                per_method = {
                    'Okapi BM25': bm25_doc_ids,
                    'TF-IDF + Cosine Similarity': tfidf_doc_ids,
                }
                metrics = {
                    'constraints_display': _format_constraints(constraints),
                    'num_relevant': len(relevant_ids),
                    'methods': {},
                }
                for method_name, doc_ids in per_method.items():
                    method_metrics = {
                        'precision_at_k': precision_at_k(doc_ids, relevant_ids),
                        'recall_at_k': recall_at_k(doc_ids, relevant_ids),
                        'hit_rate_at_k': hit_rate_at_k(doc_ids, relevant_ids),
                        'ndcg_at_k': ndcg_at_k(doc_ids, relevant_ids),
                    }
                    metrics['methods'][method_name] = method_metrics
                    for key, value in method_metrics.items():
                        summary_totals[method_name][key] += value

                num_with_ground_truth += 1

            query_results.append({
                'query': query,
                'bm25_results': bm25_results,
                'bm25_time': f"{bm25_time:.4f}",
                'tfidf_results': tfidf_results,
                'tfidf_time': f"{tfidf_time:.4f}",
                'metrics': metrics,
            })

    summary = None
    if num_with_ground_truth > 0:
        summary = {
            method: {
                key: summary_totals[method][key] / num_with_ground_truth
                for key in ('precision_at_k', 'recall_at_k', 'hit_rate_at_k', 'ndcg_at_k')
            }
            for method in METRIC_METHODS
        }

    context = {
        'submitted_queries': submitted_queries,
        'total_scanned': total_scanned,
        'query_results': query_results,
        'num_queries': len(queries),
        'num_with_ground_truth': num_with_ground_truth,
        'summary': summary,
        'max_queries': MAX_COMPARE_QUERIES,
    }
    return render(request, 'recommender/evaluation.html', context)


def paper_evaluation_view(request):
    """
    Official quantitative BM25 vs TF-IDF evaluation at /evaluasi/paper/.

    Runs recommender.evaluation.run_evaluation() — the 14 labeled
    ground-truth queries — fresh on every request. Same function
    `python manage.py run_evaluation` uses, so this page and the CLI
    report (eval/results.md) can never disagree. This is the source for
    the paper's Table II; see paper_evaluation.html for the relevance
    criteria used to build the ground truth.
    """
    result = run_evaluation()
    return render(request, 'recommender/paper_evaluation.html', {'result': result})
