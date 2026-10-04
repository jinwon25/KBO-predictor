"""Illustrative contest scoring, independent of the private production code."""
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def normalize_probability(value):
    try:
        probability = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Probability must be numeric') from exc
    if not probability.is_finite() or not 0 <= probability <= 100:
        raise ValueError('Probability must be between 0 and 100')
    return probability.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def timestamp(value):
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() is None:
        raise ValueError('Timezone offset is required')
    return parsed


def score(game):
    if game['status'] in ('cancelled', 'draw') or game.get('doubleheader', 1) == 2:
        return dict(eligible=False, submitted=False, hit=False, reason='excluded')
    if game['status'] != 'final':
        return dict(eligible=False, submitted=False, hit=False, reason='pending')
    if game.get('winner') not in ('home', 'away'):
        raise ValueError('Final game must have a winner')
    if game.get('probability') is None or not game.get('received_at'):
        return dict(eligible=True, submitted=False, hit=False, reason='missing')
    probability = normalize_probability(game['probability'])
    if timestamp(game['received_at']) > timestamp(game['start_at']) - timedelta(minutes=15):
        return dict(eligible=True, submitted=False, hit=False, reason='late')
    hit = probability != 50 and ('home' if probability > 50 else 'away') == game['winner']
    return dict(eligible=True, submitted=True, hit=hit,
                reason='neutral' if probability == 50 else ('hit' if hit else 'miss'))


def summarize(games):
    scored = [score(game) for game in games]
    eligible = sum(item['eligible'] for item in scored)
    submitted = sum(item['submitted'] for item in scored)
    hits = sum(item['hit'] for item in scored)
    return dict(eligible=eligible, submitted=submitted, hits=hits,
                accuracy=round(100 * hits / eligible, 2) if eligible else None)
