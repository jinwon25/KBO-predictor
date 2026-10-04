'use strict';
let data;
const $ = selector => document.querySelector(selector);
const percent = value => value == null ? '—' : `${value.toFixed(1)}%`;
const reasons = {hit:'적중',miss:'실패',neutral:'50.00% · 실패',late:'마감 후 · 실패',missing:'미제출 · 실패',excluded:'평가 제외',pending:'결과 대기'};
const descriptions = {prediction:'예측 확률과 경기 결과를 한눈에 확인합니다.',statistics:'평가 분모와 적용 기간을 함께 확인합니다.',operations:'일정 확인부터 기록 검증까지 운영 흐름을 살펴봅니다.'};
document.querySelectorAll('[data-page]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.page').forEach(page => page.hidden = page.id !== button.dataset.page);
  document.querySelectorAll('[data-page]').forEach(item => {item.classList.toggle('active', item === button); item.removeAttribute('aria-current');});
  button.setAttribute('aria-current','page');
  $('#title').textContent = $('#breadcrumb').textContent = button.childNodes[0].textContent.trim();
  $('#description').textContent = descriptions[button.dataset.page];
}));
const tabs = [...document.querySelectorAll('[data-period]')];
tabs.forEach((button,index) => {
  button.addEventListener('click', () => {
    tabs.forEach(tab => {tab.setAttribute('aria-selected',String(tab === button)); tab.tabIndex = tab === button ? 0 : -1;});
    $('#chart').setAttribute('aria-labelledby',button.id);
    if(data) renderChart(button.dataset.period);
  });
  button.addEventListener('keydown', event => {
    if (!['ArrowRight','ArrowLeft','Home','End'].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === 'Home' ? tabs[0] : event.key === 'End' ? tabs[tabs.length-1] : tabs[(index+1)%tabs.length];
    next.focus(); next.click();
  });
});
function renderChart(period) {
  $('#chart').innerHTML = data[period].map(row => `<div class="chart-row"><span>${row.label}</span><div class="bar" aria-hidden="true"><i style="width:${row.accuracy ?? 0}%"></i></div><strong>${percent(row.accuracy)}</strong><small>${row.hits}/${row.eligible}경기 적중</small></div>`).join('');
}
async function init() {
  try {
    const response = await fetch('/api/demo');
    if (!response.ok) throw new Error('Unable to load demo');
    data = await response.json();
    const s = data.summary;
    $('#summary').innerHTML = [['예제 정확도',percent(s.accuracy),'미제출 포함 · 합성 수치'],['평가 대상',s.eligible,'취소·무승부·DH 2차전 제외'],['마감 내 제출',s.submitted,'평가 대상 중 유효 제출'],['예측 적중',s.hits,'공식 대회 실적 아님']].map(([label,value,note]) => `<div class="stat"><label>${label}</label><strong>${value}</strong><small>${note}</small></div>`).join('');
    $('#games').innerHTML = data.games.map(g => {
      const favored = g.probability != null && g.probability !== 50 ? (g.probability > 50 ? 'home' : 'away') : null;
      const color = favored ? g[`${favored}_color`] : '#73819b';
      const p = g.probability == null ? '미제출' : `${g.probability.toFixed(2)}%`;
      const close = g.probability != null && Math.abs(g.probability-50) < 3;
      return `<article class="game" style="--team:${color};--tint:${color}09"><div class="game-body"><div class="game-top"><span>${g.start_at.slice(0,10)} · 18:30</span><span>${g.model}</span></div><div class="teams"><div class="team">${g.away}<small>AWAY</small></div><span class="versus">VS</span><div class="team">${g.home}<small>HOME</small></div></div><div class="probability">${p}<small>홈팀 승리 확률</small></div><div class="meter" aria-hidden="true"><i style="width:${g.probability ?? 0}%"></i></div><p>실제 결과 예시: ${g.status === 'final' ? `${g[g.winner]} 승리` : (g.status === 'draw' ? '무승부' : '취소')}</p></div><div class="result ${g.outcome.reason}"><strong>${reasons[g.outcome.reason]}</strong>${close ? '<span class="badge">접전</span>' : '<span>합성 경기</span>'}</div></article>`;
    }).join('');
    $('#models').innerHTML = data.models.map(m => `<div class="model"><div><span class="model-name">${m.name}</span>${m.active ? '<span class="active-label">데모 활성</span>' : ''}<small>${m.period} · ${m.eligible}경기</small></div><div class="model-score">${percent(m.accuracy)}<small>${m.hits}/${m.eligible} 적중</small></div></div>`).join('');
    renderChart('monthly');
  } catch(error) { $('#error').hidden = false; console.error(error); }
}
init();
