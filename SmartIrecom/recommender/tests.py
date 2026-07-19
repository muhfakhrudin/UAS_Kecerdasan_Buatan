"""
Tests for catalog query validation (recommender/evaluation.py's
validate_catalog_query) — guards against BM25 surfacing near-zero-score
matches for models/storage that don't exist in the dataset at all (e.g.
"iPhone 16" partially matching on the generic shared token "iphone") —
and for the relevance floor / price-phrase parsing in recommender/ranking.py
that guards against the same kind of near-zero-score phantom matches for
vague queries with no real distinguishing signal (e.g. "iphone second
murah").
"""

from django.test import TestCase
from django.urls import reverse

from .evaluation import validate_catalog_query
from .ranking import parse_price_constraints
from .search_engine import load_products


class ValidateCatalogQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.products = load_products()

    def test_nonexistent_model_is_invalid(self):
        result = validate_catalog_query('iPhone 16', self.products)
        self.assertFalse(result['valid'])
        self.assertIn('iPhone 16', result['message'])

    def test_existing_model_is_valid(self):
        result = validate_catalog_query('iPhone 11', self.products)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['message'])

    def test_nonexistent_storage_for_existing_model_is_invalid(self):
        result = validate_catalog_query('iPhone 12 1TB', self.products)
        self.assertFalse(result['valid'])
        self.assertIn('iPhone 12', result['message'])
        self.assertIn('1TB', result['message'])

    def test_extra_free_text_does_not_block_valid_model(self):
        result = validate_catalog_query('iPhone 11 murah', self.products)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['message'])

    def test_generic_iphone_query_is_valid(self):
        result = validate_catalog_query('iPhone', self.products)
        self.assertTrue(result['valid'])


class SearchViewCatalogValidationTests(TestCase):
    """End-to-end: the main search page (`/`) never shows fake BM25/TF-IDF hits."""

    def test_nonexistent_model_returns_zero_results_on_both_methods(self):
        response = self.client.get(reverse('recommender:search'), {'q': 'iPhone 16'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_results'], 0)
        self.assertEqual(response.context['tfidf_total_results'], 0)
        self.assertEqual(list(response.context['results']), [])
        self.assertIsNotNone(response.context['validation_message'])

    def test_existing_model_returns_results(self):
        response = self.client.get(reverse('recommender:search'), {'q': 'iPhone 11'})
        self.assertGreater(response.context['total_results'], 0)
        self.assertIsNone(response.context['validation_message'])

    def test_nonexistent_storage_combo_returns_zero_results(self):
        response = self.client.get(reverse('recommender:search'), {'q': 'iPhone 12 1TB'})
        self.assertEqual(response.context['total_results'], 0)
        self.assertEqual(response.context['tfidf_total_results'], 0)
        self.assertIsNotNone(response.context['validation_message'])

    def test_extra_free_text_still_returns_results(self):
        response = self.client.get(reverse('recommender:search'), {'q': 'iPhone 11 murah'})
        self.assertGreater(response.context['total_results'], 0)
        self.assertIsNone(response.context['validation_message'])

    def test_vague_query_with_no_real_signal_returns_zero_results(self):
        """"iphone" matches 100% of the catalog with a near-zero BM25 score
        and no other query term matches anything — should be 0 results,
        not the entire catalog in meaningless order."""
        response = self.client.get(reverse('recommender:search'), {'q': 'iphone second murah'})
        self.assertEqual(response.context['total_results'], 0)
        self.assertEqual(response.context['tfidf_total_results'], 0)

    def test_price_phrase_in_query_text_filters_by_price(self):
        response = self.client.get(reverse('recommender:search'), {'q': 'iphone second dibawah 3 juta'})
        self.assertGreater(response.context['total_results'], 0)
        self.assertEqual(response.context['detected_price_notice'], 'maksimal Rp3.000.000')
        for product, _ in response.context['results']:
            self.assertLessEqual(product['harga_raw'], 3_000_000)

    def test_explicit_price_field_wins_over_detected_price_phrase(self):
        response = self.client.get(reverse('recommender:search'), {
            'q': 'iphone dibawah 3 juta',
            'max_price': '5000000',
        })
        # The explicit field (5jt) should be used, not the phrase in the query (3jt).
        self.assertIsNone(response.context['detected_price_notice'])
        for product, _ in response.context['results']:
            self.assertLessEqual(product['harga_raw'], 5_000_000)


class ParsePriceConstraintsTests(TestCase):
    def test_detects_under_price_in_juta(self):
        self.assertEqual(parse_price_constraints('iphone dibawah 3 juta'), (3_000_000, None))

    def test_detects_over_price_in_ribu(self):
        self.assertEqual(parse_price_constraints('iphone di atas 500 ribu'), (None, 500_000))

    def test_ignores_unrelated_numbers_without_a_price_unit(self):
        # "128GB" and "90%" must never be misread as a price.
        self.assertEqual(parse_price_constraints('iPhone 12 128GB battery 90'), (None, None))

    def test_no_price_phrase_returns_none_none(self):
        self.assertEqual(parse_price_constraints('iphone second murah'), (None, None))


class CompareViewCatalogValidationTests(TestCase):
    """Single-query demo page (`/evaluasi/`) skips ranking for unavailable products."""

    def test_nonexistent_model_returns_zero_results(self):
        response = self.client.get(reverse('recommender:compare'), {'query': 'iPhone 16'})
        result = response.context['result']
        self.assertEqual(result['bm25_results'], [])
        self.assertEqual(result['tfidf_results'], [])
        self.assertIsNotNone(result['validation_message'])

    def test_existing_model_returns_results(self):
        response = self.client.get(reverse('recommender:compare'), {'query': 'iPhone 11'})
        result = response.context['result']
        self.assertGreater(len(result['bm25_results']), 0)
        self.assertIsNone(result['validation_message'])


class MultiQueryEvaluationCatalogValidationTests(TestCase):
    """Multi-query demo page excludes unavailable queries from every average."""

    def test_mixed_queries_exclude_unavailable_from_all_averages(self):
        response = self.client.get(reverse('recommender:multi_query_evaluation'), {
            'submitted': '1',
            'query1': 'iPhone 16',
            'query2': 'iPhone 11 64GB',
            'query3': 'iPhone 12 128GB Shopee',
            'query4': 'iPhone 12 1TB',
            'query5': 'iPhone 11 murah',
        })
        result = response.context['result']

        by_query = {qr['query']: qr for qr in result['query_results']}
        self.assertIsNotNone(by_query['iPhone 16']['validation_message'])
        self.assertEqual(by_query['iPhone 16']['bm25_results'], [])
        self.assertIsNotNone(by_query['iPhone 12 1TB']['validation_message'])
        self.assertEqual(by_query['iPhone 12 1TB']['bm25_results'], [])

        self.assertIsNone(by_query['iPhone 11 64GB']['validation_message'])
        self.assertIsNone(by_query['iPhone 11 murah']['validation_message'])

        # 2 of 5 queries are unavailable -> only 3 ranked queries feed avg_time_ms.
        self.assertEqual(result['num_valid'], 3)
