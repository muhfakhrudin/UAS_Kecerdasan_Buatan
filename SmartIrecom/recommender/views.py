"""
Views for the Smart IRecom recommender application.

This module contains the main search view that handles user queries,
invokes the BM25 search engine, and renders the results template.
Includes performance metrics tracking and keyword highlighting logic.
"""

import re
import time

from django.shortcuts import render
from django.utils.safestring import mark_safe

from .search_engine import calculate_bm25_scores, load_products


def _highlight_keywords(text, query_tokens):
    """
    Wrap matching query keywords in a neon-styled HTML span.

    Performs case-insensitive matching of each query token against the text,
    wrapping matches in a <span> with neon cyan styling for visual emphasis.

    Args:
        text (str): The original product text to highlight.
        query_tokens (set[str]): Lowercased query tokens to match against.

    Returns:
        str: HTML-safe string with matched keywords wrapped in highlight spans.
    """
    if not text or not query_tokens:
        return text

    def replacer(match):
        word = match.group(0)
        if word.lower() in query_tokens:
            return f'<span class="text-cyan-400 font-bold">{word}</span>'
        return word

    # Split on word boundaries, preserving separators
    highlighted = re.sub(r'[A-Za-z0-9]+', replacer, str(text))
    return mark_safe(highlighted)


def search_view(request):
    """
    Handle the main search page and AI-powered product search.

    Processes GET requests with an optional 'q' query parameter.
    When a query is present, it loads all products from the CSV dataset,
    computes BM25 relevance scores, filters out zero-score results,
    and passes the ranked results along with performance metrics to the template.

    Args:
        request: Django HttpRequest object.

    Returns:
        HttpResponse: Rendered search.html template with context containing:
            - query (str): The user's search query
            - results (list[tuple[dict, float]]): Ranked (product, score) tuples
            - total_results (int): Number of matching products
            - total_scanned (int): Total products scanned in the database
            - execution_time (str): BM25 computation latency in seconds
            - max_score (float): Highest BM25 score for score bar normalization
            - query_tokens (list[str]): Tokenized query words for highlighting
    """
    query = request.GET.get('q', '').strip()
    results = []
    total_scanned = 0
    execution_time = 0.0
    query_tokens = set()

    if query:
        # Tokenize query for keyword highlighting
        query_tokens = set(re.findall(r'[a-z0-9]+', query.lower()))

        # ── Measure BM25 execution latency ──────────────────────────────
        start_time = time.time()

        products = load_products()
        total_scanned = len(products)

        scored_products = calculate_bm25_scores(query, products)
        results_raw = [(product, score) for product, score in scored_products if score > 0][:15]

        execution_time = time.time() - start_time
        # ────────────────────────────────────────────────────────────────

        # Apply keyword highlighting to product display fields
        results = []
        for product, score in results_raw:
            highlighted_product = dict(product)  # Shallow copy
            highlighted_product['kategori_varian_hl'] = _highlight_keywords(
                product['kategori_varian'], query_tokens
            )
            highlighted_product['kategori_seri_hl'] = _highlight_keywords(
                product['kategori_seri'], query_tokens
            )
            highlighted_product['penyimpanan_hl'] = _highlight_keywords(
                product['penyimpanan'], query_tokens
            )
            highlighted_product['toko_hl'] = _highlight_keywords(
                product['toko'], query_tokens
            )
            highlighted_product['wilayah_toko_hl'] = _highlight_keywords(
                product['wilayah_toko'], query_tokens
            )
            highlighted_product['platform_hl'] = _highlight_keywords(
                product['platform'], query_tokens
            )
            # Build a "matched specs snippet" showing which fields matched
            matched_fields = []
            for field_name, field_key in [
                ('Varian', 'kategori_varian'),
                ('Storage', 'penyimpanan'),
                ('Platform', 'platform'),
                ('Wilayah', 'wilayah_toko'),
                ('Toko', 'toko'),
                ('Battery', 'battery_health'),
            ]:
                field_val = product.get(field_key, '')
                if field_val:
                    field_tokens = set(re.findall(r'[a-z0-9]+', field_val.lower()))
                    if field_tokens & query_tokens:
                        matched_fields.append(field_name)
            highlighted_product['matched_fields'] = matched_fields

            results.append((highlighted_product, score))

    context = {
        'query': query,
        'results': results,
        'total_results': len(results),
        'total_scanned': total_scanned,
        'execution_time': f"{execution_time:.4f}",
        'max_score': results[0][1] if results else 0,
        'query_tokens': list(query_tokens),
    }

    return render(request, 'recommender/search.html', context)
