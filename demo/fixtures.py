"""Deterministic invented examples, not anonymized competition records."""
from datetime import datetime, timedelta, timezone
from .scoring import normalize_probability, score, summarize

TEAMS = [('Aster', '#4864db'), ('Coral', '#c65362'), ('Forest', '#28836d'),
         ('Amber', '#a36a17'), ('Violet', '#8956bc'), ('Ocean', '#247ea0')]


def games():
    result = []
    for index in range(84):
        start = datetime(2030, 4, 1, 18, 30, tzinfo=timezone(timedelta(hours=9))) + timedelta(days=index)
        home = TEAMS[index % 6]
        away = TEAMS[(index + 1) % 6]
        probability = [61.2, 46.3, 57.1, 49.1, 50.001, 68.4, 43.8][index % 7]
        result.append(dict(id=f'demo-{index:03}', home=home[0], away=away[0],
                           home_color=home[1], away_color=away[1],
                           start_at=start.isoformat(),
                           received_at=(start - timedelta(minutes=10 if index % 17 == 0 else 30)).isoformat(),
                           probability=None if index % 19 == 0 else probability,
                           winner='home' if index % 5 < 3 else 'away',
                           status='cancelled' if index % 23 == 0 else ('draw' if index % 29 == 0 else 'final'),
                           doubleheader=2 if index % 31 == 0 else 1,
                           model='demo-v2' if index >= 28 else 'demo-v1'))
    return result


def dashboard():
    records = games()
    monthly = []
    for month in sorted({g['start_at'][:7] for g in records}, reverse=True):
        monthly.append(dict(label=month, **summarize([g for g in records if g['start_at'].startswith(month)])))
    weekdays = []
    for day, label in enumerate(['월', '화', '수', '목', '금', '토', '일']):
        weekdays.append(dict(label=label, **summarize([g for g in records if datetime.fromisoformat(g['start_at']).weekday() == day])))
    models = []
    for model in ('demo-v2', 'demo-v1'):
        subset = [g for g in records if g['model'] == model]
        models.append(dict(name=model, active=model == 'demo-v2',
                           period=f"{subset[0]['start_at'][:10]} ~ {subset[-1]['start_at'][:10]}", **summarize(subset)))
    return dict(synthetic=True, summary=summarize(records), monthly=monthly,
                weekdays=weekdays, models=models,
                games=[dict(g, probability=float(normalize_probability(g['probability']))
                            if g['probability'] is not None else None,
                            outcome=score(g)) for g in reversed(records[-6:])])
