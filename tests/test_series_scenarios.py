from itertools import product
import math
import unittest

from demo.series_scenarios import best_of, wildcard_fourth_seed


class SeriesScenarioTests(unittest.TestCase):
    def test_fair_series_and_length_distribution(self):
        result = best_of([.5] * 5)
        self.assertAlmostEqual(result['advance_probability'], .5)
        self.assertEqual(result['length_distribution'], {3: .25, 4: .375, 5: .375})
        self.assertAlmostEqual(result['expected_games'], 4.125)
        self.assertAlmostEqual(best_of([.5] * 7)['expected_games'], 5.8125)

    def test_deterministic_series_stop_at_clinching_game(self):
        for p in (0, 1):
            result = best_of([p] * 7)
            self.assertEqual(result['advance_probability'], p)
            self.assertEqual(result['length_distribution'], {4: 1})
            self.assertEqual(result['expected_games'], 4)

    def test_variable_probabilities_against_full_sequence_enumeration(self):
        probabilities = [.61, .43, .57, .48, .52]
        expected = 0
        for outcomes in product((0, 1), repeat=5):
            weight = math.prod(p if y else 1 - p for p, y in zip(probabilities, outcomes))
            expected += weight * (sum(outcomes) >= 3)
        result = best_of(probabilities)
        self.assertAlmostEqual(result['advance_probability'], expected)
        self.assertAlmostEqual(sum(result['length_distribution'].values()), 1)
        opposite = best_of([1 - p for p in probabilities])
        self.assertAlmostEqual(result['advance_probability'] + opposite['advance_probability'], 1)

    def test_fixed_probability_order_preserves_advancement_not_length(self):
        probabilities = [.9, .9, .1, .1, .5]
        forward, backward = best_of(probabilities), best_of(reversed(probabilities))
        self.assertAlmostEqual(forward['advance_probability'], backward['advance_probability'])
        self.assertGreater(abs(forward['expected_games'] - backward['expected_games']), .01)

    def test_wildcard_draw_and_conditional_second_game(self):
        result = wildcard_fourth_seed((.5, 0), (.5, 0))
        self.assertEqual(result['advance_probability'], .75)
        self.assertEqual(result['expected_games'], 1.5)
        self.assertEqual(wildcard_fourth_seed((0, 1), (0, 0))['advance_probability'], 1)
        result = wildcard_fourth_seed((.2, .1), (.6, .2))
        self.assertAlmostEqual(result['advance_probability'], .86)
        self.assertAlmostEqual(result['expected_games'], 1.7)

    def test_probability_and_format_validation(self):
        for values in ([], [.5, .5], [math.nan], [math.inf], [-.01], [1.01], [True], ['.5']):
            with self.subTest(values=values), self.assertRaises(ValueError):
                best_of(values)
        for first in ((.8, .3), (.5,), (-.1, .2), (math.nan, 0)):
            with self.subTest(first=first), self.assertRaises(ValueError):
                wildcard_fourth_seed(first, (.5, 0))


if __name__ == '__main__':
    unittest.main()
