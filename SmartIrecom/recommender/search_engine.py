"""
Okapi BM25 Search Engine for iPhone Product Recommendation.

This module implements the BM25 (Best Matching 25) probabilistic ranking function
used by search engines to estimate the relevance of documents (iPhone products)
to a given search query.

Algorithm: Okapi BM25
    score(D, Q) = Σ IDF(qi) · [ f(qi, D) · (k1 + 1) ] / [ f(qi, D) + k1 · (1 - b + b · |D| / avgdl) ]

Parameters:
    k1 = 1.5 (term frequency saturation)
    b  = 0.75 (document length normalization)
"""

import csv
import math
import os
import statistics
from collections import Counter

from .preprocessing import preprocess


# ─── BM25 Hyperparameters ───────────────────────────────────────────────────────
K1 = 1.5   # Controls term frequency saturation
B = 0.75   # Controls document length normalization (0 = no normalization, 1 = full)


def _tokenize(text):
    """
    Run the shared preprocessing pipeline on a text string.

    Delegates to preprocessing.preprocess(): case folding, punctuation
    removal, tokenizing, stopword removal, stemming. This is the analyzer
    for both queries and documents, and is shared with the TF-IDF baseline
    so both methods see identical text handling.

    Args:
        text (str): The raw text to tokenize.

    Returns:
        list[str]: A list of processed tokens.
    """
    return preprocess(text)


def _build_search_content(row):
    """
    Construct a unified search content string from a product row.
    
    Concatenates all relevant fields into a single searchable text blob
    so that BM25 can match queries against any product attribute.
    
    Args:
        row (dict): A CSV row dictionary with product fields.
    
    Returns:
        str: A concatenated, space-separated string of all searchable fields.
    """
    fields = [
        row.get('Toko', ''),
        row.get('Platform', ''),
        row.get('Kategori Seri', ''),
        row.get('Kategori Varian', ''),
        row.get('penyimpanan', ''),
        f"battery {row.get('Battery Health', '')}%" if row.get('Battery Health') else '',
        row.get('Harga', ''),
        row.get('Pembayaran', ''),
        row.get('Wilayah Toko', ''),
        row.get('Kategori iPhone', ''),
    ]
    return ' '.join(f for f in fields if f)


def _parse_harga_raw(harga_str):
    """
    Parse an Indonesian Rupiah price string into an integer.
    
    Examples:
        'Rp2.050.000' -> 2050000
        'Rp15.500.000' -> 15500000
    
    Args:
        harga_str (str): The raw price string (e.g., 'Rp2.050.000').
    
    Returns:
        int: The numeric price value, or 0 if parsing fails.
    """
    if not harga_str:
        return 0
    try:
        cleaned = harga_str.replace('Rp', '').replace('.', '').replace(',', '').strip()
        return int(cleaned)
    except (ValueError, AttributeError):
        return 0


def load_products():
    """
    Load all iPhone products from the CSV dataset.
    
    Reads the CSV file located at the project root (one level above the Django
    project directory) and constructs a list of product dictionaries, each
    enriched with a 'search_content' field for BM25 indexing.
    
    Missing Battery Health values are imputed with the dataset's median
    (over the rows that do report a value), per the paper's data-cleaning
    plan (Bagian III.B). Imputed rows are flagged via battery_is_imputed
    so the UI can show them as an estimate rather than as seller-reported
    fact — the median is used for filtering/sorting/ranking, but callers
    must not present it as verified data.

    Returns:
        list[dict]: A list of product dictionaries with the following keys:
            - doc_id (int): Stable 0-based row index, used as the document
              identifier by the evaluation harness (eval/) and the TF-IDF
              baseline (tfidf_engine.py).
            - toko (str): Store name
            - platform (str): Marketplace platform
            - kategori_seri (str): iPhone series category
            - kategori_varian (str): iPhone variant
            - penyimpanan (str): Storage capacity
            - battery_health (str): Raw battery health string as reported in the
              CSV; empty string if the seller did not report one (even if
              battery_val below was imputed).
            - battery_val (float | None): Reported value, or the dataset median
              if imputed. None only if the corpus has no reported values at all.
            - battery_is_imputed (bool): True if battery_val came from median
              imputation rather than the seller's own listing.
            - battery_color (str): Tailwind CSS color class for battery badge
            - harga (str): Original price string
            - harga_raw (int): Numeric price value
            - pembayaran (str): Payment methods
            - wilayah_toko (str): Store region/city
            - kategori_iphone (str): iPhone category (Resmi/Inter)
            - search_content (str): Concatenated searchable text
    """
    # Use Django's BASE_DIR (where manage.py and dataset_iphone.csv live)
    from django.conf import settings
    csv_path = os.path.join(settings.BASE_DIR, 'dataset_iphone.csv')

    with open(csv_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    # First pass: compute the corpus median from rows that do report a value.
    reported_battery_vals = []
    for row in rows:
        raw = row.get('Battery Health', '').strip()
        if raw:
            try:
                reported_battery_vals.append(float(raw))
            except ValueError:
                pass
    battery_median = statistics.median(reported_battery_vals) if reported_battery_vals else None

    products = []
    for doc_id, row in enumerate(rows):
        battery_raw = row.get('Battery Health', '').strip()
        try:
            battery_val_reported = float(battery_raw) if battery_raw else None
        except ValueError:
            battery_val_reported = None

        battery_is_imputed = battery_val_reported is None and battery_median is not None
        battery_val = battery_val_reported if battery_val_reported is not None else battery_median

        # Pre-compute color class for template
        if battery_val is not None:
            if battery_val >= 90:
                battery_color = 'battery-good'
            elif battery_val >= 80:
                battery_color = 'battery-fair'
            else:
                battery_color = 'battery-low'
        else:
            battery_color = 'battery-na'

        product = {
            'doc_id': doc_id,
            'toko': row.get('Toko', '').strip(),
            'platform': row.get('Platform', '').strip(),
            'kategori_seri': row.get('Kategori Seri', '').strip(),
            'kategori_varian': row.get('Kategori Varian', '').strip(),
            'penyimpanan': row.get('penyimpanan', '').strip(),
            'battery_health': battery_raw,
            'battery_val': battery_val,
            'battery_is_imputed': battery_is_imputed,
            'battery_color': battery_color,
            'harga': row.get('Harga', '').strip(),
            'harga_raw': _parse_harga_raw(row.get('Harga', '')),
            'pembayaran': row.get('Pembayaran', '').strip(),
            'wilayah_toko': row.get('Wilayah Toko', '').strip(),
            'kategori_iphone': row.get('Kategori iPhone', '').strip(),
            'search_content': _build_search_content(row),
        }
        products.append(product)

    return products


def calculate_bm25_scores(query, products):
    """
    Calculate Okapi BM25 relevance scores for all products against a query.
    
    This is the core ranking function. For each term in the query, it computes:
        1. IDF (Inverse Document Frequency) — how rare/important the term is
        2. TF (Term Frequency) — how often the term appears in each document
        3. BM25 score — combining IDF and normalized TF
    
    The final score for a document is the sum of BM25 scores across all query terms.
    
    Args:
        query (str): The user's search query string.
        products (list[dict]): List of product dictionaries, each containing
                               a 'search_content' key.
    
    Returns:
        list[tuple[dict, float]]: A list of (product, score) tuples for all
                                   products, including those with score 0.
                                   Sorted by score descending.
    
    Algorithm Details:
        IDF(qi) = ln( (N - n(qi) + 0.5) / (n(qi) + 0.5) + 1 )
        
        score(D, Q) = Σ IDF(qi) · (f(qi,D) · (k1 + 1)) / (f(qi,D) + k1 · (1 - b + b · |D|/avgdl))
        
        Where:
            N      = total number of documents
            n(qi)  = number of documents containing term qi
            f(qi,D)= frequency of term qi in document D
            |D|    = length of document D (in tokens)
            avgdl  = average document length across the corpus
            k1     = 1.5 (term frequency saturation parameter)
            b      = 0.75 (length normalization parameter)
    """
    if not query or not products:
        return [(p, 0.0) for p in products]

    # ── Step 1: Tokenize the query ──────────────────────────────────────────
    query_tokens = _tokenize(query)
    if not query_tokens:
        return [(p, 0.0) for p in products]

    N = len(products)  # Total number of documents in the corpus

    # ── Step 2: Tokenize all documents and compute corpus statistics ────────
    doc_tokens_list = []      # Tokenized version of each document
    doc_lengths = []          # Length (token count) of each document

    for product in products:
        tokens = _tokenize(product['search_content'])
        doc_tokens_list.append(tokens)
        doc_lengths.append(len(tokens))

    # Average document length across the entire corpus
    avgdl = sum(doc_lengths) / N if N > 0 else 0

    # ── Step 3: Compute document frequency (DF) for each query term ─────────
    # df[term] = number of documents containing that term
    df = {}
    for qt in set(query_tokens):
        count = 0
        for doc_tokens in doc_tokens_list:
            if qt in doc_tokens:
                count += 1
        df[qt] = count

    # ── Step 4: Compute IDF for each query term ────────────────────────────
    # Using the standard BM25 IDF formula with +1 to avoid negative values
    idf = {}
    for qt in set(query_tokens):
        n_qi = df.get(qt, 0)
        idf[qt] = math.log((N - n_qi + 0.5) / (n_qi + 0.5) + 1)

    # ── Step 5: Compute BM25 score for each document ───────────────────────
    scores = []
    for i, product in enumerate(products):
        score = 0.0
        doc_len = doc_lengths[i]
        tf_counter = Counter(doc_tokens_list[i])

        for qt in query_tokens:
            f_qi = tf_counter.get(qt, 0)  # Term frequency of qi in document
            if f_qi == 0:
                continue

            # BM25 numerator: f(qi,D) * (k1 + 1)
            numerator = f_qi * (K1 + 1)

            # BM25 denominator: f(qi,D) + k1 * (1 - b + b * |D| / avgdl)
            denominator = f_qi + K1 * (1 - B + B * (doc_len / avgdl))

            # Accumulate the BM25 score contribution for this query term
            score += idf[qt] * (numerator / denominator)

        scores.append((product, round(score, 4)))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)

    return scores
