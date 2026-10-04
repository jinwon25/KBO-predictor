import unittest
from decimal import Decimal
from demo.fixtures import dashboard, games
from demo.scoring import normalize_probability, score, summarize


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.game = dict(status='final', winner='home', probability='60',
                         start_at='2030-04-01T18:30:00+09:00',
                         received_at='2030-04-01T18:00:00+09:00')

    def test_probability_validation(self):
        for value in ['NaN', 'Infinity', '-0.001', '100.001', None, True, 'hello']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_probability(value)
        self.assertEqual(normalize_probability('0'), Decimal('0.00'))
        self.assertEqual(normalize_probability('100'), Decimal('100.00'))

    def test_rounding_to_neutral(self):
        for value in ('50', '50.001', '49.999'):
            result = score(dict(self.game, probability=value))
            self.assertEqual(result['reason'], 'neutral')
            self.assertTrue(result['submitted'])
            self.assertFalse(result['hit'])
        self.assertEqual(normalize_probability('50.005'), Decimal('50.01'))

    def test_both_directions(self):
        self.assertTrue(score(self.game)['hit'])
        self.assertTrue(score(dict(self.game, probability=40, winner='away'))['hit'])
        self.assertFalse(score(dict(self.game, probability=40))['hit'])

    def test_cutoff(self):
        self.assertTrue(score(dict(self.game, received_at='2030-04-01T18:15:00+09:00'))['hit'])
        self.assertEqual(score(dict(self.game, received_at='2030-04-01T18:15:00.001+09:00'))['reason'], 'late')
        self.assertTrue(score(dict(self.game, received_at='2030-04-01T09:15:00+00:00'))['hit'])
        with self.assertRaises(ValueError):
            score(dict(self.game, received_at='2030-04-01T18:00:00'))

    def test_exclusions(self):
        for change in [dict(status='cancelled'), dict(status='draw'), dict(doubleheader=2), dict(status='scheduled')]:
            self.assertFalse(score(dict(self.game, **change))['eligible'])

    def test_missing_in_denominator(self):
        result = summarize([self.game, dict(self.game, probability=None), dict(self.game, status='draw')])
        self.assertEqual(result, dict(eligible=2, submitted=1, hits=1, accuracy=50.0))
        self.assertIsNone(summarize([])['accuracy'])

    def test_fixture_aggregate_consistency(self):
        data = dashboard()
        self.assertTrue(data['synthetic'])
        for key in ['monthly', 'weekdays', 'models']:
            for field in ['eligible', 'submitted', 'hits']:
                self.assertEqual(sum(row[field] for row in data[key]), data['summary'][field])
        self.assertEqual(games(), games())


if __name__ == '__main__':
    unittest.main()
