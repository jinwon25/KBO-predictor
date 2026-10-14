# 참고 문헌과 적용 범위

대회 결산의 지표 정의·모델 비교·자료 점검과 공개 문서 구성에 참고한 자료입니다. 2026-10-13과 2026-10-14에 확인했으며, 외부 문헌은 이 프로젝트의 실제 성능을 입증하는 자료와 구분합니다.

[문서 목록](README.md) · [시즌 결산](season-review-2026.md)

## 참가 결과와 조건

| 자료 | 확인한 내용 |
| --- | --- |
| [중앙대학교 최강이조 팀 페이지](https://www.statiz.co.kr/prediction/?m=university_detail&ptt_idx=70) | 2026-10-14 공개 표기: 16위·54.6%·게임 참여수 689경기·ALL KILL 5회 |
| [2026-03-27 공식 대회 정책](https://statiz.co.kr/board/?b_code=10000&b_idx=4294959131&m=main&mode=view) | 채점·접수 마감·데이터 이용·자료 보존과 사후 제출 조건 |

공개 페이지의 성적을 모델 입력으로 수집하지 않았습니다. 별도 참가 서약·FAQ·사후 제출 공지 전체를 확보한 것은 아니며, [공개 정책](data-policy.md)에 확인 범위를 기록했습니다.

## 분석 방법과 해석

| 자료 | 결산에 참고한 내용 | 해석 범위 |
| --- | --- | --- |
| [Gneiting & Raftery (2007), Strictly Proper Scoring Rules, Prediction, and Estimation](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf) | Brier·LogLoss로 확률 예측을 평가하는 근거 | 적중률과 접수율을 대체하지 않음 |
| [Cawley & Talbot (2010), On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation](https://www.jmlr.org/papers/v11/cawley10a.html) | 후보 선택 과정의 과적합과 성능 평가 편향 | 이미 확인한 시즌의 회고 진단을 독립 검증으로 표현하지 않음 |
| [scikit-learn: Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) | 확률 보정·판별력의 구분, 보정 곡선 해석 | Brier 하나의 개선으로 보정 개선이나 모델 우월성을 확정하지 않음 |
| [scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | 전처리와 특성 구성의 자료 누출 | 경기 전 입력과 사후 재구성 자료를 구분하는 점검 원칙 |
| [scikit-learn: Permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html) | 상관 입력과 중요도의 해석 | 입력 중요도를 인과적 기여로 해석하지 않음 |
| [Government Data Quality Framework](https://www.gov.uk/government/publications/the-government-data-quality-framework/the-government-data-quality-framework) | 완전성·유일성·일관성·시의성 구분 | 경기번호 결합과 접수 미확인 처리에 적용한 일반 원칙이며 대회 준수 인증이 아님 |

scikit-learn 문서는 개념 설명을 참고했습니다. 문서 조회와 운영 환경 업그레이드는 별개이며, 이 결산을 위해 운영 패키지를 변경하지 않았습니다.

## 설명과 재현

| 자료 | 반영한 내용 |
| --- | --- |
| [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) | 루트에 문제·결과·실행 방법을 두고 상세 근거를 문서로 연결 |
| [GitHub Flavored Markdown 명세](https://github.github.com/gfm/) | 표·강조·링크의 렌더링 확인 |

논문 원문과 외부 야구 데이터를 재배포하지 않습니다. 분석 방법을 설명하는 공개 합성 예제와 실제 대회 원장·내부 진단 산출물의 범위는 [데이터 정책](data-policy.md)을 따릅니다.
