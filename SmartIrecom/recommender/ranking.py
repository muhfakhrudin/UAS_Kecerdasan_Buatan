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
    """Wrap matching query keywords in a neon-styled HTML span (case-insensitive)."""
    if not text or not query_tokens:
        return text

    def replacer(match):
        word = match.group(0)
        if word.lower() in query_tokens:
            return f'<span class="hl-keyword">{word}</span>'
        return word

    highlighted = re.sub(r'[A-Za-z0-9]+', replacer, str(text))
    return mark_safe(highlighted)


def _apply_relevance_threshold(scored_products):
    """Keep only matches scoring above 10% of the top score (drops low-quality universal matches)."""
    max_score = scored_products[0][1] if scored_products else 0
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
    """Attach keyword-highlighted display fields and matched-field badges to each ranked product."""
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
    scored_products = score_fn(query, products)
    all_matched = _apply_relevance_threshold(scored_products)
    filtered_matched = _apply_hard_filters(all_matched, min_price, max_price, min_battery, category, platform)
    filtered_matched = _apply_sort(filtered_matched, sort_by)
    total_found = len(filtered_matched)
    results_raw = filtered_matched[:top_n]
    return _build_highlighted_results(results_raw, query_tokens), total_found
