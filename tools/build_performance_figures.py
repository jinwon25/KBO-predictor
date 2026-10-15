"""공개 성능 문서의 집계 표로 두 차트를 재생성합니다. 원천 경기 데이터는 읽지 않습니다."""
from pathlib import Path
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "docs/prediction-performance.md").read_text(encoding="utf-8")
OUT = ROOT / "docs/images"

def rows_between(start, end):
    section = TEXT.split(start, 1)[1].split(end, 1)[0]
    return [[cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in section.splitlines() if line.startswith("|")]

def count(value):
    match = re.search(r"(\d+)/(\d+)", value)
    if not match:
        raise ValueError(f"적중/경기 형식 아님: {value}")
    return tuple(map(int, match.groups()))

def pct(value):
    return float(value.rstrip("%"))

def configure():
    installed = {font.name for font in font_manager.fontManager.ttflist}
    for name in ("Malgun Gothic", "Noto Sans CJK KR", "NanumGothic", "AppleGothic"):
        if name in installed:
            plt.rcParams["font.family"] = name
            break
    else:
        raise RuntimeError("한국어 글꼴을 설치하세요: Noto Sans CJK KR 또는 맑은 고딕")
    plt.rcParams.update({"axes.unicode_minus": False, "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.edgecolor": "#CBD5E1",
                         "text.color": "#1E293B", "axes.labelcolor": "#475569",
                         "xtick.color": "#475569", "ytick.color": "#475569"})

def build():
    configure()
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = [r for r in rows_between("### 전체 보존 예측의 월별 성적", "### 최종 모델만의 월별 성적") if r[0].startswith("2026-")]
    teams = [r for r in rows_between("| 참가 팀 |", "![최종 모델의 팀별") if len(r) == 5 and re.search(r"\d+/\d+", r[1])]
    confidence = [r for r in rows_between("| 예측 강도 |", "55–60% 구간은") if len(r) == 5 and re.search(r"\d+/\d+", r[1])]
    assert len(monthly) == 7 and len(teams) == 10 and len(confidence) == 4
    assert tuple(sum(count(r[1])[i] for r in monthly) for i in (0, 1)) == (356, 639)
    assert tuple(sum(count(r[1])[i] for r in teams) for i in (0, 1)) == (338, 600)
    assert tuple(sum(count(r[1])[i] for r in confidence) for i in (0, 1)) == (169, 300)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.7), gridspec_kw={"width_ratios": [1.15, 1]})
    fig.subplots_adjust(left=.06, right=.97, top=.76, bottom=.21, wspace=.25)
    fig.suptitle("2026 시즌 예측 성능 | 전체 평균 안에 숨은 편차", x=.06, y=.96, ha="left", fontsize=19, fontweight="bold")
    fig.text(.06,.875,"실제 보존 예측의 내부 평가 · 공식 팀 성적 54.6%와 분모가 다릅니다",fontsize=11,color="#64748B")
    ax=axes[0]
    vals=[pct(r[2]) for r in monthly]
    ax.bar(range(7), vals, width=.64, color="#2563EB", zorder=3)
    ax.set(xticks=range(7), xticklabels=[str(int(r[0][-2:]))+"월" for r in monthly],
           ylim=(0,90), ylabel="적중률 (%)", title="전체 운영 639경기 · 모델 변경 포함")
    ax.grid(axis="y",alpha=.18,zorder=0)
    ax.axhline(55.71205,color="#334155",ls="--",lw=1,label="전체 55.71%")
    for i,r in enumerate(monthly):
        ax.text(i,vals[i]+2,f"{r[2]}\n{r[1]}",ha="center",fontsize=9, bbox={"facecolor":"white","edgecolor":"none","pad":0.4})
    ax.legend(frameon=False,loc="upper left",fontsize=9)
    ax=axes[1]
    x=range(4)
    ax.plot(x,[pct(r[2]) for r in confidence],"o--",color="#64748B",label="평균 예측 확률",lw=1.7)
    ax.plot(x,[pct(r[3]) for r in confidence],"s-",color="#D97706",label="실제 적중률",lw=2)
    ax.set(xticks=list(x),xticklabels=[r[0].replace("% 이상","%+") for r in confidence],
           ylim=(30,90),ylabel="확률 / 적중률 (%)",title="최종 모델 300경기 · 예측 강도 구간")
    ax.grid(axis="y",alpha=.18)
    for i,r in enumerate(confidence):
        ax.annotate(r[1],(i,pct(r[3])),xytext=(0,-20),textcoords="offset points",ha="center",fontsize=10)
    ax.legend(frameon=False,loc="upper left",fontsize=9)
    fig.text(.06,.065,"막대·점 아래 숫자: 적중/경기. 10월 39경기, 70% 이상 10경기는 소표본입니다.\n집계: 2026-10-13 결산 · 2026-10-15 재대조 | 근거와 전체 표: docs/prediction-performance.md",fontsize=10,color="#64748B")
    fig.savefig(OUT/"season-performance-2026.png",dpi=160,facecolor="white")
    plt.close(fig)
    fig, ax=plt.subplots(figsize=(12.8,7.5))
    fig.subplots_adjust(left=.09,right=.78,top=.78,bottom=.18)
    fig.suptitle("최종 모델 | 팀별 홈·원정 경기에서의 예측 성적",x=.07,y=.96,ha="left",fontsize=19,fontweight="bold")
    fig.text(.07,.885,"2026-07-07–10-12 · 같은 300경기 · 해당 팀 참가 경기의 승자를 맞힌 비율",fontsize=11,color="#64748B")
    for i,r in enumerate(teams):
        hk,hn=count(r[2]); ak,an=count(r[3])
        ax.plot([100*hk/hn,100*ak/an],[i,i],color="#CBD5E1",lw=2,zorder=1)
        ax.scatter(100*hk/hn,i,color="#2563EB",s=65,zorder=3,label="홈 경기" if i==0 else None)
        ax.scatter(100*ak/an,i,color="#D97706",s=60,marker="s",zorder=3,label="원정 경기" if i==0 else None)
        ax.text(1.02,i,f"{hk}/{hn}   ·   {ak}/{an}",transform=ax.get_yaxis_transform(),va="center",fontsize=10)
    ax.set(yticks=range(10),yticklabels=[r[0] for r in teams],xlim=(0,100),xlabel="적중률 (%)")
    ax.invert_yaxis()
    ax.grid(axis="x",alpha=.18)
    ax.axvline(56.33333,color="#475569",ls="--",lw=1)
    ax.text(1.02,1.06,"적중/경기: 홈 · 원정",transform=ax.transAxes,fontsize=10,fontweight="bold")
    ax.legend(frameon=False,loc="upper left",bbox_to_anchor=(0,1.14),ncol=2)
    fig.text(.07,.06,"점선: 최종 모델 전체 56.33%. 팀의 실제 승률이 아니라 경기 승자 예측의 적중률입니다.\n한 경기가 양 팀에 포함되므로 팀별 분모 합 600건 = 독립 300경기. 팀별 대진·시점 차이를 통제한 비교는 아닙니다.",fontsize=10,color="#64748B")
    fig.savefig(OUT/"team-performance-2026.png",dpi=160,facecolor="white")
    plt.close(fig)
    print("공개 집계 표 검증 및 성능 차트 2개 생성 완료")

if __name__ == "__main__":
    build()
