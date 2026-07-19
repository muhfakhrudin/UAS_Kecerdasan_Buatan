"""
Shared text preprocessing pipeline for iRecom Master's search algorithms.

Used identically by both the BM25 engine (search_engine.py) and the TF-IDF
baseline (tfidf_engine.py) so that ranking differences between the two
methods reflect the ranking algorithm itself, not divergent text handling.

Pipeline (5 stages, per project spec): case folding -> punctuation removal
-> tokenizing -> stopword removal -> stemming.

Pure Python standard library only (re) — no third-party NLP/ML packages
(e.g. Sastrawi, NLTK) are used, to keep BM25 compliant with the project's
"stdlib-only" non-functional requirement, since this module is imported
directly inside the BM25 pipeline.

The stemmer below is a lightweight, rule-based Indonesian suffix/prefix
stripper — NOT a full Nazief-Adriani implementation like Sastrawi. It is
intentionally conservative (short tokens and a protected domain-term list
are left untouched) to avoid mangling product/brand terms such as
"iphone", "shopee", or "resmi".
"""

import re

_PUNCT_RE = re.compile(r'[^\w\s]', re.UNICODE)
_TOKEN_RE = re.compile(r'[a-z0-9]+')

# Common Indonesian function words, plus a handful of English ones that may
# appear in user-typed queries. Hand-written literal list (stdlib-only).
STOPWORDS = frozenset({
    'yang', 'untuk', 'dengan', 'dari', 'pada', 'ke', 'di', 'dan', 'atau',
    'ini', 'itu', 'adalah', 'akan', 'juga', 'tidak', 'ada', 'dalam', 'oleh',
    'sebagai', 'secara', 'saat', 'jika', 'maka', 'agar', 'karena', 'namun',
    'tetapi', 'serta', 'antara', 'hingga', 'sampai', 'masih', 'sudah',
    'belum', 'sedang', 'telah', 'dapat', 'bisa', 'harus', 'perlu', 'ingin',
    'mau', 'saja', 'hanya', 'begitu', 'seperti', 'yaitu', 'yakni', 'bahwa',
    'tersebut', 'tsb', 'kami', 'kita', 'saya', 'aku', 'anda', 'dia',
    'mereka', 'ia', 'apa', 'apakah', 'bagaimana', 'kenapa', 'mengapa',
    'kapan', 'dimana', 'siapa', 'para', 'yg', 'dg', 'dgn', 'utk', 'nya',
    'lah', 'kah', 'pun', 'per', 'ya', 'nih', 'deh', 'dong', 'sih', 'kok',
    'lagi', 'lah', 'jadi', 'gak', 'ga', 'nggak', 'engga', 'the', 'a', 'an',
    'of', 'in', 'on', 'for', 'with', 'and', 'or', 'is', 'are', 'to',
})

# Domain terms exempt from stemming — stripping affixes would corrupt them.
_PROTECTED_TERMS = frozenset({
    'iphone', 'shopee', 'tokopedia', 'resmi', 'inter', 'beacukai',
    'battery', 'wallet', 'jakarta', 'bandung', 'bekasi', 'bogor', 'depok',
})

# Longest-suffix-first so e.g. "kannya" is stripped before "nya" alone.
_SUFFIXES = (
    'kannya', 'nnya', 'nya', 'kan', 'lah', 'kah', 'pun', 'ku', 'mu',
    'isasi', 'isme', 'wan', 'wati',
)

# Longest-prefix-first for the same reason ("meng" before "me").
_PREFIXES = (
    'mengeng', 'menge', 'meng', 'meny', 'men', 'mem', 'me',
    'pengeng', 'penge', 'peng', 'peny', 'pen', 'pem', 'pe',
    'ber', 'be', 'ter', 'di', 'ke', 'se',
)

_MIN_STEM_LEN = 5  # tokens at/under this length are left untouched


def case_fold(text):
    """Lowercase the input text (stage 1)."""
    return text.lower() if text else ''


def remove_punctuation(text):
    """Strip punctuation/symbols, keeping letters, digits and whitespace (stage 2)."""
    return _PUNCT_RE.sub(' ', text) if text else ''


def tokenize(text):
    """Split cleaned text into alphanumeric tokens (stage 3)."""
    if not text:
        return []
    return _TOKEN_RE.findall(text)


def remove_stopwords(tokens):
    """Drop tokens present in the stopword list (stage 4)."""
    return [t for t in tokens if t not in STOPWORDS]


def stem_token(token):
    """Strip one known suffix then one known prefix from a single token (stage 5)."""
    if len(token) <= _MIN_STEM_LEN or token in _PROTECTED_TERMS:
        return token

    stemmed = token
    for suf in _SUFFIXES:
        if stemmed.endswith(suf) and len(stemmed) - len(suf) >= 3:
            stemmed = stemmed[:-len(suf)]
            break

    for pre in _PREFIXES:
        if stemmed.startswith(pre) and len(stemmed) - len(pre) >= 3:
            stemmed = stemmed[len(pre):]
            break

    return stemmed


def stem(tokens):
    """Apply stem_token to every token in the list."""
    return [stem_token(t) for t in tokens]


def preprocess(text):
    """
    Run the full 5-stage pipeline on a raw text string.

    case_fold -> remove_punctuation -> tokenize -> remove_stopwords -> stem

    Returns:
        list[str]: the final list of stemmed, stopword-free tokens.
    """
    folded = case_fold(text)
    cleaned = remove_punctuation(folded)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    tokens = stem(tokens)
    return tokens
