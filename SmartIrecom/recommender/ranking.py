"""
Shared ranking pipeline: relevance threshold -> hard filters -> sort ->
top-N -> keyword highlighting. Used by both the main search view
(views.search_view) and the live BM25-vs-TF-IDF comparison view
(views.compare_view), so the two ranking methods are only ever compared
on their ranking math, never on divergent filtering/highlighting logic.
"""

import re

from django.utils.safestring import mark_safe


def _highlight_keywords(text, query_tokens):
    """Wrap matching query keywords in a highlighted HTML span (case-insensitive)."""
    if not text or not query_tokens:
        return text

    def replacer(match):
        word = match.group(0)
        if word.lower() in query_tokens:
            return f'<span class="hl-keyword">{word}</span>'
        return word

    highlighted = re.sub(r'[A-Za-z0-9]+', replacer, str(text))
    return mark_safe(highlighted)


# Below this raw score, the top match is driven purely by a term that's
# common to nearly the whole corpus (e.g. "iphone" itself, which appears in
# 100% of products) rather than any real distinguishing signal — see
# recommender/evaluation.py's docs for the IDF math behind this. Verified
# against real queries: the 5 official test queries score 2.9-5.5 (BM25)
# and 0.27-0.46 (TF-IDF); a query with no real match scores ~0.0016.
MIN_ABSOLUTE_SCORE = 0.05


_PRICE_UNIT_MULTIPLIERS = {'juta': 1_000_000, 'jt': 1_000_000, 'ribu': 1_000, 'rb': 1_000}
_PRICE_UNDER_RE = re.compile(
    r'\b(?:di\s*bawah|kurang\s*dari|maksimal|maks\.?)\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(juta|jt|ribu|rb)\b',
    re.IGNORECASE,
)
_PRICE_OVER_RE = re.compile(
    r'\b(?:di\s*atas|lebih\s*dari|minimal|min\.?)\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(juta|jt|ribu|rb)\b',
    re.IGNORECASE,
)


def parse_price_constraints(query):
    """
    Detect simple Indonesian price phrases in a free-text query — "dibawah
    3 juta", "di atas 500 ribu", "maksimal 2jt" — and translate them into
    an actual Rupiah max/min price, the same kind of hard filter the
    explicit price fields already apply.

    Only fires on a number immediately followed by a "juta"/"jt"/"ribu"/"rb"
    unit, so it never misfires on unrelated numbers in the query (storage
    like "128GB", battery like "90%", etc. never match this pattern).

    Returns:
        tuple[int | None, int | None]: (max_price, min_price) in Rupiah,
            each None when that phrase wasn't found.
    """
    max_price = None
    min_price = None

    under_match = _PRICE_UNDER_RE.search(query)
    if under_match:
        value = float(under_match.group(1).replace(',', '.'))
        max_price = int(value * _PRICE_UNIT_MULTIPLIERS[under_match.group(2).lower()])

    over_match = _PRICE_OVER_RE.search(query)
    if over_match:
        value = float(over_match.group(1).replace(',', '.'))
        min_price = int(value * _PRICE_UNIT_MULTIPLIERS[over_match.group(2).lower()])

    return max_price, min_price


def _apply_relevance_threshold(scored_products, skip_absolute_floor=False):
    """
    Keep only matches scoring above 10% of the top score (drops
    low-quality universal matches).

    Also requires the top score to clear MIN_ABSOLUTE_SCORE — unless
    skip_absolute_floor is set, which callers do whenever a hard filter
    (price/battery/category/platform, explicit or auto-detected from the
    query text) is already narrowing the result set. In that case a weak
    text-relevance signal is fine; the filter is doing the real work, so
    products shouldn't be discarded just because "iphone"-style universal
    terms produce a small score.
    """
    max_score = scored_products[0][1] if scored_products else 0
    if not skip_absolute_floor and max_score < MIN_ABSOLUTE_SCORE:
        return []
    threshold = max_score * 0.1
    return [(product, score) for product, score in scored_products if score > threshold and score > 0]


def _apply_hard_filters(matches, min_price, max_price, min_battery, category, platform):
    """Apply price/battery/category/platform hard filters shared by every ranking method."""
    filtered = []
    for product, score in matches:
        try:
            if min_price and product.get('harga_raw', 0) < int(min_price):
                continue
            if max_price and product.get('harga_raw', float('inf')) > int(max_price):
                continue
        except ValueError:
            pass

        try:
            if min_battery:
                batt_val = product.get('battery_val')
                if batt_val is None or batt_val < int(min_battery):
                    continue
        except ValueError:
            pass

        if category and category.lower() != 'all':
            if product.get('kategori_iphone', '').lower() != category.lower():
                continue

        if platform and platform.lower() != 'all':
            if product.get('platform', '').lower() != platform.lower():
                continue

        filtered.append((product, score))
    return filtered


def _apply_sort(matches, sort_by):
    """Sort matches per the requested mode; 'relevance' keeps the ranking method's own order."""
    if sort_by == 'price_asc':
        matches.sort(key=lambda x: x[0].get('harga_raw', float('inf')))
    elif sort_by == 'price_desc':
        matches.sort(key=lambda x: x[0].get('harga_raw', 0), reverse=True)
    elif sort_by == 'battery_desc':
        matches.sort(key=lambda x: x[0].get('battery_val') or 0, reverse=True)
    return matches


def _build_highlighted_results(results_raw, query_tokens):
    """Attach keyword-highlighted display fields to each ranked product."""
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

        results.append((highlighted_product, score))
    return results


def rank_products(score_fn, query, products, query_tokens,
                   min_price='', max_price='', min_battery='', category='all', platform='all',
                   sort_by='relevance', top_n=15):
    """
    Run one ranking method (BM25 or TF-IDF) through the identical
    threshold -> hard-filter -> sort -> top-N -> highlight pipeline.

    Returns:
        tuple: (highlighted_results, total_found)
    """
    has_hard_filter = bool(
        min_price or max_price or min_battery
        or (category and category.lower() != 'all')
        or (platform and platform.lower() != 'all')
    )
    scored_products = score_fn(query, products)
    all_matched = _apply_relevance_threshold(scored_products, skip_absolute_floor=has_hard_filter)
    filtered_matched = _apply_hard_filters(all_matched, min_price, max_price, min_battery, category, platform)
    filtered_matched = _apply_sort(filtered_matched, sort_by)
    total_found = len(filtered_matched)
    results_raw = filtered_matched[:top_n]
    return _build_highlighted_results(results_raw, query_tokens), total_found
