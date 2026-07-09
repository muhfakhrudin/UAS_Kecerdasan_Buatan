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
import re
from collections import Counter


# ─── BM25 Hyperparameters ───────────────────────────────────────────────────────
K1 = 1.5   # Controls term frequency saturation
B = 0.75   # Controls document length normalization (0 = no normalization, 1 = full)


def _tokenize(text):
    """
    Tokenize and case-fold a text string.
    
    Splits on non-alphanumeric characters and converts to lowercase.
    This serves as the analyzer for both queries and documents.
    
    Args:
        text (str): The raw text to tokenize.
    
    Returns:
        list[str]: A list of lowercase tokens.
    """
    if not text:
        return []
    return re.findall(r'[a-z0-9]+', text.lower())


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
    
    Returns:
        list[dict]: A list of product dictionaries with the following keys:
            - toko (str): Store name
            - platform (str): Marketplace platform
            - kategori_seri (str): iPhone series category
            - kategori_varian (str): iPhone variant
            - penyimpanan (str): Storage capacity
            - battery_health (str): Battery health percentage
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

    products = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            battery_raw = row.get('Battery Health', '').strip()
            try:
                battery_val = float(battery_raw) if battery_raw else None
            except ValueError:
                battery_val = None

            # Pre-compute color class for template
            if battery_val is not None:
                if battery_val >= 90:
                    battery_color = 'text-green-400'
                elif battery_val >= 80:
                    battery_color = 'text-yellow-400'
                else:
                    battery_color = 'text-red-400'
            else:
                battery_color = 'text-gray-500'

            product = {
                'toko': row.get('Toko', '').strip(),
                'platform': row.get('Platform', '').strip(),
                'kategori_seri': row.get('Kategori Seri', '').strip(),
                'kategori_varian': row.get('Kategori Varian', '').strip(),
                'penyimpanan': row.get('penyimpanan', '').strip(),
                'battery_health': battery_raw,
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
