import math
import unittest

from demo.metric_audit import audit, example_games


class MetricAuditTests(unittest.TestCase):
    def test_denominators_and_probability_losses(self):
        result = audit(example_games())
        self.assertEqual(result['counts'], dict(
            total=9, eligible=6, excluded=3, pending=0, predicted=5,
            prediction_hits=3, submitted=3, confirmed_hits=1,
            unknown_receipts=1, late=1, known_missing=1, neutral=1))
        self.assertEqual(result['prediction_accuracy'], 3 / 5)
        self.assertEqual(result['accepted_accuracy'], 1 / 3)
        self.assertIsNone(result['contest_style_accuracy'])
        self.assertEqual(result['possible_accuracy_bounds'], (1 / 6, 2 / 6))
        self.assertAlmostEqual(result['brier'], 0.18)
        self.assertAlmostEqual(result['log_loss'], -math.log(.6 * .4 * .5 * .7 * .8) / 5)

    def test_unknown_receipt_is_not_known_non_submission(self):
        games = example_games()
        games[5]['receipt_evidence'] = 'complete'
        result = audit(games)
        self.assertEqual(result['contest_style_accuracy'], 1 / 6)
        self.assertEqual(result['counts']['known_missing'], 2)
        games[5]['received_at'] = '2030-04-01T18:00:00+09:00'
        result = audit(games)
        self.assertEqual(result['contest_style_accuracy'], 2 / 6)
        self.assertEqual(result['prediction_accuracy'], 3 / 5)

    def test_empty_and_only_excluded_are_not_zero_accuracy(self):
        for games in ([], example_games()[6:]):
            result = audit(games)
            for key in ('prediction_accuracy', 'accepted_accuracy',
                        'confirmed_receipt_rate', 'contest_style_accuracy', 'brier', 'log_loss'):
                self.assertIsNone(result[key])
        game = dict(example_games()[0], status='scheduled')
        self.assertEqual(audit([game])['counts']['pending'], 1)

    def test_duplicate_games_and_inconsistent_evidence_rejected(self):
        game = example_games()[0]
        for games in ([game, game], [dict(game, receipt_evidence='unknown')],
                      [dict(game, probability=None)], [dict(game, receipt_evidence='invalid')]):
            with self.subTest(games=games), self.assertRaises(ValueError):
                audit(games)

    def test_extreme_probabilities_preserve_infinite_log_loss(self):
        game = dict(example_games()[0], probability='0')
        result = audit([game])
        self.assertEqual(result['brier'], 1)
        self.assertEqual(result['log_loss'], math.inf)
        result = audit([dict(game, winner='away')])
        self.assertEqual(result['log_loss'], 0)


if __name__ == '__main__':
    unittest.main()
