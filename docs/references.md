# 참고 문헌과 적용 범위

2026년 10월 13일 논문 출판 페이지·저자 공개본·공식 문서를 확인했습니다. 각 자료가 뒷받침하는 방법과 이 프로젝트에서 검증해야 할 가설을 구분합니다. 논문 원문이나 외부 야구 데이터는 이 저장소에 재배포하지 않습니다.

[문서 목록](README.md) · [연구 고도화 계획](research-plan.md)

## 확률 예측과 검증

| 자료 | 참고할 내용 | 적용 제한 |
| --- | --- | --- |
| [Gneiting & Raftery (2007), Strictly Proper Scoring Rules, Prediction, and Estimation](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf) | 확률 예측을 Brier·LogLoss 같은 적정 점수 규칙으로 평가하는 근거 | 실제 KBO 성능의 증거가 아니며 적중률·제출률을 대체하지 않음 |
| [Cawley & Talbot (2010), On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation](https://www.jmlr.org/beta/papers/v11/cawley10a.html) | 후보 선택 과정도 과적합할 수 있다는 근거 | 이미 본 2026년 자료를 새 후보의 독립 최종 평가로 재사용하지 않음 |
| [Niculescu-Mizil & Caruana (2005), Predicting Good Probabilities With Supervised Learning](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf) | 학습 알고리즘의 확률 왜곡과 Platt·isotonic 보정 비교 | 다른 데이터의 보정 결과나 표본 기준을 KBO 보장치로 가져오지 않음 |
| [Guo et al. (2017), On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html) | 낮은 자유도의 온도 보정 개념 | 논문의 신경망 결과가 현재 LightGBM에서의 효과를 입증하지 않음 |
| [Politis & Romano (1994), The Stationary Bootstrap](https://www.tandfonline.com/doi/abs/10.1080/01621459.1994.10476870) | 약하게 의존하는 정상 관측의 재표집이라는 방법적 근거 | 출판 페이지의 초록을 확인한 범위. KBO 시즌의 정상성을 가정하거나 블록 길이의 최적값을 확정하지 않음 |
| [McElfresh et al. (2023), When Do Neural Nets Outperform Boosted Trees on Tabular Data?](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f06d5ebd4ff40b40dd97e30cee632123-Abstract-Datasets_and_Benchmarks.html) | 표 형식 자료의 특성과 튜닝 조건을 고려한 비교군 선택 | 일반 벤치마크 결과를 특정 KBO 모델 계열의 우월성으로 일반화하지 않음 |

## 정의와 구현을 점검할 공식 문서

| 자료 | 연결할 점검 |
| --- | --- |
| [scikit-learn: Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) | 기본 모델 학습과 보정 자료 분리, 보정 곡선과 판별력의 구분, 소표본 isotonic 위험 |
| [scikit-learn: TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html) | 미래 자료 누출과 행 간격 조건. 실제 실험에서는 경기 수 대신 날짜 경계를 명시 |
| [scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | 전처리·결측 처리·특성 선택을 학습 구간 안에서 수행 |
| [scikit-learn: Permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html) | 상관 입력의 중요도 왜곡과 그룹별 제거 실험 |
| [FanGraphs Library: Strikeout and Walk Rates](https://library.fangraphs.com/pitching/rate-stats/) | SO/TBF와 BB/TBF의 정의. MLB 평균·상수·선수 기록을 대회 입력에 사용하지 않음 |

scikit-learn의 조회 시점 stable 문서는 1.9.1입니다. 개념 설명을 참고했으며 운영 환경 업그레이드나 새 API의 적용을 실행하지 않았습니다. 실제 구현 때는 설치 버전과 동작을 확인합니다.

## 참가 결과와 조건의 출처

- [중앙대학교 최강이조 팀 페이지](https://www.statiz.co.kr/prediction/?m=university_detail&ptt_idx=70): 2026-10-14 재확인한 공개 표기인 16위·54.6%·게임 참여수 689경기·ALL KILL 5회 확인.
- [2026-03-27 공식 대회 정책](https://statiz.co.kr/board/?b_code=10000&b_idx=4294959131&m=main&mode=view): 채점·접수 마감·데이터 이용·사후 자료 제출 조건을 2026-10-14 재확인.

공개 결과 페이지를 모델 입력으로 수집하지 않았습니다. 별도 참가 서약·FAQ와 사후 제출 공지를 모두 확보한 것은 아니며, 자료의 추가 공개는 [공개 정책](data-policy.md)에서 확인 범위를 기록합니다.

## 결산을 분석 사례로 구성할 때 참고한 자료

2026-10-14에 아래 공식 문서와 원문을 추가로 확인했습니다. 서로 다른 분야의 지침을 이 프로젝트에 적용한 편집·분석 판단이며, 외부 문헌이 실제 KBO 성과를 입증하는 것은 아닙니다.

| 자료 | 이번 반영 | 적용 한계 |
| --- | --- | --- |
| [Government Data Quality Framework](https://www.gov.uk/government/publications/the-government-data-quality-framework/the-government-data-quality-framework) | 자료 완전성·유일성·일관성·시의성을 나누고, 접수 미확인과 미제출을 구분 | 정부 데이터 관리의 일반 원칙이며 이 대회의 준수 인증이 아님 |
| [scikit-learn: Probability calibration](https://scikit-learn.org/stable/modules/calibration.html) | 적중률·Brier·LogLoss의 평가 범위를 명시하고 작은 합성 예제로 분모를 대조 | 확률 품질 지표 하나로 보정 개선이나 모델 우월성을 확정하지 않음 |
| [Cawley & Talbot (2010)](https://www.jmlr.org/papers/v11/cawley10a.html) | 후보 선택에 사용한 시즌과 이후 최종 평가를 분리 | 이번 문서 보완이 새로운 독립 검증 결과를 만들지는 않음 |
| [NN/g: Stop Reporting UX Activity and Report Business Outcomes](https://www.nngroup.com/articles/reporting-ux-business-outcomes/) | 기능 목록을 관측·판단·다음 조치와 연결 | UX 보고 원칙만 참고. 측정하지 않은 시간 절감·비용 효과를 만들지 않음 |
| [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) | 루트에 문제·결과·실행 경로를 두고 상세 계산을 문서로 연결 | README 가독성 구성 근거이며 직무 평가 효과의 실증 결과가 아님 |
