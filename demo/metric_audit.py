"""독립 합성 9경기로 예측 품질·접수 증거·채점 분모를 구분합니다.

실제 대회 자료를 읽지 않으며 공식 채점기를 재현하지 않습니다.
한 행은 경기 하나와 대조를 마친 최종 접수 상태입니다.
"""
import math

from demo.scoring import normalize_probability, score


def example_games():
    base = dict(status='final', winner='home', probability='60',
                start_at='2030-04-01T18:30:00+09:00',
                received_at='2030-04-01T18:00:00+09:00',
                receipt_evidence='complete')
    changes = [
        dict(id='A'),
        dict(id='B', winner='away'),
        dict(id='C', probability='50.001'),
        dict(id='D', probability='70', received_at='2030-04-01T18:16:00+09:00'),
        dict(id='E', probability=None, received_at=None),
        dict(id='F', probability='80', received_at=None, receipt_evidence='unknown'),
        dict(id='G', status='draw', winner=None),
        dict(id='H', status='cancelled', winner=None),
        dict(id='I', doubleheader=2),
    ]
    return [dict(base, **change) for change in changes]


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def audit(games):
    """완전 대조한 미접수와 접수 원장 미확인을 다른 상태로 유지합니다.

    probability는 경기 전 보존된 홈 승리 확률(0–100), complete는
    접수 원장 대조 완료를 뜻합니다. None만으로 실제 미제출을 추정하지 않습니다.
    """
    games = list(games)
    ids = [game['id'] for game in games]
    if len(ids) != len(set(ids)):
        raise ValueError('경기 식별자는 중복될 수 없습니다')
    counts = dict(total=len(games), eligible=0, excluded=0, pending=0,
                  predicted=0, prediction_hits=0, submitted=0,
                  confirmed_hits=0, unknown_receipts=0, late=0,
                  known_missing=0, neutral=0)
    brier_losses, log_losses = [], []
    for game in games:
        evidence = game.get('receipt_evidence')
        if evidence not in ('complete', 'unknown'):
            raise ValueError('접수 증거는 complete 또는 unknown이어야 합니다')
        if game.get('received_at') and (evidence == 'unknown' or game.get('probability') is None):
            raise ValueError('접수 시각이 있으면 확인된 접수 증거와 확률이 필요합니다')
        scored = score(game)
        if not scored['eligible']:
            counts['pending' if scored['reason'] == 'pending' else 'excluded'] += 1
            continue
        counts['eligible'] += 1
        if game.get('probability') is not None:
            probability = normalize_probability(game['probability'])
            p = float(probability / 100)
            y = int(game['winner'] == 'home')
            counts['predicted'] += 1
            counts['prediction_hits'] += int(probability != 50 and (p > 0.5) == bool(y))
            brier_losses.append((p - y) ** 2)
            actual_probability = p if y else 1 - p
            log_losses.append(-math.log(actual_probability) if actual_probability else math.inf)
        if evidence == 'unknown':
            counts['unknown_receipts'] += 1
            continue
        counts['submitted'] += int(scored['submitted'])
        counts['confirmed_hits'] += int(scored['hit'])
        if scored['reason'] in ('late', 'neutral'):
            counts[scored['reason']] += 1
        if scored['reason'] == 'missing':
            counts['known_missing'] += 1
    n = counts['eligible']
    hits = counts['confirmed_hits']
    unknown = counts['unknown_receipts']
    return dict(
        counts=counts,
        prediction_accuracy=ratio(counts['prediction_hits'], counts['predicted']),
        accepted_accuracy=ratio(hits, counts['submitted']),
        confirmed_receipt_rate=ratio(counts['submitted'], n),
        contest_style_accuracy=None if unknown else ratio(hits, n),
        possible_accuracy_bounds=(ratio(hits, n), ratio(hits + unknown, n)),
        brier=ratio(sum(brier_losses), len(brier_losses)),
        log_loss=ratio(sum(log_losses), len(log_losses)),
    )


def main():
    result = audit(example_games())
    counts = result['counts']
    print('독립 합성 9경기 | 실제 참가 성적 아님')
    print(f"전체 {counts['total']} / 채점 대상 {counts['eligible']} / 제외 {counts['excluded']}")
    print(f"보존 예측 적중률: {counts['prediction_hits']}/{counts['predicted']} = {result['prediction_accuracy']:.2%}")
    print(f"마감 전 접수 확인분 적중률: {counts['confirmed_hits']}/{counts['submitted']} = {result['accepted_accuracy']:.2%}")
    print(f"접수 확인 비율: {counts['submitted']}/{counts['eligible']} = {result['confirmed_receipt_rate']:.2%}")
    print(f"보존 예측 Brier: {result['brier']:.5f} / LogLoss: {result['log_loss']:.5f}")
    print(f"접수 미확인 {counts['unknown_receipts']}건: 대회식 적중률 확정 불가")
    lower, upper = result['possible_accuracy_bounds']
    print(f'접수 미확인에 따른 가능한 범위: {lower:.2%} ~ {upper:.2%} (신뢰구간 아님)')


if __name__ == '__main__':
    main()
