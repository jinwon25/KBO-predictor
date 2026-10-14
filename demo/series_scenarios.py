"""가정한 경기 확률을 시리즈 확률·예상 경기 수로 변환하는 독립 예제.

실제 팀·모델·원천 자료를 사용하지 않습니다. best_of는 무승부 없는
가상 시리즈입니다. 각 차전 확률은 이전 결과와 무관하게 고정합니다.
"""
import math
from numbers import Real


def probability(value):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError('확률은 0부터 1 사이의 유한한 수여야 합니다')
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError('확률은 0부터 1 사이의 유한한 수여야 합니다')
    return float(value)


def best_of(win_probabilities):
    """A팀 기준 차전별 승률로 과반 선승의 모든 도달 가능한 상태를 합산.

    길이 5는 3선승, 길이 7은 4선승입니다. 미래 차전의 확률은 그
    경기가 열리는 경우의 가정이며, 앞선 승패에 따른 변화는 없습니다.
    """
    probabilities = tuple(probability(p) for p in win_probabilities)
    maximum = len(probabilities)
    if not maximum or maximum % 2 == 0:
        raise ValueError('무승부 없는 홀수 최대 경기 수가 필요합니다')
    target = maximum // 2 + 1
    states = {(0, 0): 1.0}
    length_distribution = {}
    advance_probability = 0.0
    for game_number, p in enumerate(probabilities, 1):
        following = {}
        for (wins, losses), mass in states.items():
            for a_wins, outcome_probability in ((True, p), (False, 1 - p)):
                weight = mass * outcome_probability
                if weight == 0:
                    continue
                w, l = wins + int(a_wins), losses + int(not a_wins)
                if w == target or l == target:
                    length_distribution[game_number] = length_distribution.get(game_number, 0.0) + weight
                    if w == target:
                        advance_probability += weight
                else:
                    following[w, l] = following.get((w, l), 0.0) + weight
        states = following
    return dict(advance_probability=advance_probability,
                expected_games=sum(n * mass for n, mass in length_distribution.items()),
                length_distribution=length_distribution)


def wildcard_fourth_seed(first_game, second_game):
    """4위팀 기준 (승리, 무승부) 확률. 2차전 값은 1차전 패배 조건부.

    4위팀이 한 번 이기거나 비기면 진출하는 최대 2경기 구조입니다.
    first_game과 second_game의 나머지 확률은 4위팀 패배입니다.
    """
    losses = []
    for game in (first_game, second_game):
        if len(game) != 2:
            raise ValueError('각 경기에 승리·무승부 확률 두 개가 필요합니다')
        win, draw = (probability(p) for p in game)
        if win + draw > 1:
            raise ValueError('승리와 무승부 확률의 합은 1 이하여야 합니다')
        losses.append(1 - win - draw)
    return dict(advance_probability=1 - losses[0] * losses[1],
                expected_games=1 + losses[0],
                length_distribution={1: 1 - losses[0], 2: losses[0]})


def main():
    print('독립 합성 시나리오 | 실제 KBO 팀의 예측 아님')
    print('가정한 매 경기 승률 | 5전3선승 진출 | 7전4선승 진출 | 7전 예상 경기 수')
    for p in (.45, .50, .55, .60):
        five, seven = best_of([p] * 5), best_of([p] * 7)
        print(f"{p:.0%} | {five['advance_probability']:.2%} | {seven['advance_probability']:.2%} | {seven['expected_games']:.3f}")
    print('와일드카드 4위팀: 각 경기 승리 50%, 무승부 0% 가정')
    result = wildcard_fourth_seed((.5, 0), (.5, 0))
    print(f"진출 {result['advance_probability']:.2%} | 예상 경기 수 {result['expected_games']:.3f}")
    print('와일드카드 4위팀: 각 경기 승리 48%, 무승부 4% 가정')
    result = wildcard_fourth_seed((.48, .04), (.48, .04))
    print(f"진출 {result['advance_probability']:.2%} | 예상 경기 수 {result['expected_games']:.3f}")
    print('시나리오 범위는 추정 신뢰구간이 아니며, 경기 확률 자체를 학습하지 않습니다.')


if __name__ == '__main__':
    main()
