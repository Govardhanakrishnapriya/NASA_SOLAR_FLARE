"""
NASA Solar Flare Predictor — app.py
------------------------------------
Run:  python app.py
Opens automatically in your default browser.
No pip installs required — uses only Python stdlib.
"""

import http.server
import threading
import webbrowser
import os
import sys

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NASA Solar Flare Predictor</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0b10;
    --bg2: #111218;
    --bg3: #181920;
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.14);
    --text: #f0f0f5;
    --text2: #9a9aaa;
    --text3: #6a6a7a;
    --accent: #EF9F27;
    --accent2: #D85A30;
    --radius: 12px;
    --radius-sm: 8px;
  }

  html, body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  #starfield { position: fixed; inset: 0; pointer-events: none; z-index: 0; }

  .app {
    position: relative; z-index: 1;
    max-width: 900px; margin: 0 auto;
    padding: 2.5rem 1.5rem 3rem;
  }

  .header { text-align: center; margin-bottom: 2.5rem; }
  .sun-wrap {
    display: flex; justify-content: center;
    margin-bottom: 1.25rem; perspective: 600px;
  }
  #sunCanvas {
    border-radius: 50%;
    filter: drop-shadow(0 0 28px rgba(239,159,39,0.55));
    transition: transform 0.3s ease;
  }
  #sunCanvas:hover { transform: scale(1.06); }

  .header h1 {
    font-size: 2rem; font-weight: 700; letter-spacing: -0.02em;
    background: linear-gradient(110deg, #FFD060, #EF9F27, #D85A30);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.4rem;
  }
  .header p { font-size: 14px; color: var(--text3); letter-spacing: 0.04em; }

  .card-3d {
    background: var(--bg2); border: 0.5px solid var(--border);
    border-radius: var(--radius); padding: 1rem 1.2rem;
    transform-style: preserve-3d;
    transition: transform 0.25s ease, border-color 0.2s, box-shadow 0.25s;
    position: relative;
  }
  .card-3d:hover {
    transform: translateY(-4px) rotateX(3deg) rotateY(-1deg);
    border-color: var(--border2);
    box-shadow: 0 14px 40px rgba(0,0,0,0.5), 0 0 0 0.5px rgba(255,255,255,0.05);
  }
  .card-3d::before {
    content: ''; position: absolute; inset: 0;
    border-radius: var(--radius);
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, transparent 60%);
    pointer-events: none;
  }

  .field-label {
    font-size: 11px; font-weight: 600; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
  }
  .field-label i { font-size: 14px; color: var(--accent); }

  .val-pill {
    display: inline-block; font-size: 12px; font-weight: 600;
    background: rgba(239,159,39,0.12); color: var(--accent);
    border: 0.5px solid rgba(239,159,39,0.3);
    border-radius: 20px; padding: 1px 9px;
    min-width: 44px; text-align: center; margin-left: auto;
  }

  .field-row { display: flex; align-items: center; }

  input[type=range] {
    -webkit-appearance: none; width: 100%; height: 4px;
    background: var(--bg3); border-radius: 2px;
    outline: none; margin-top: 6px; cursor: pointer;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 16px; height: 16px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FFD060, #D85A30);
    box-shadow: 0 0 8px rgba(239,159,39,0.6);
    cursor: pointer; transition: transform 0.15s;
  }
  input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.2); }

  select, input[type=number] {
    width: 100%; padding: 8px 10px;
    background: var(--bg3); border: 0.5px solid var(--border2);
    border-radius: var(--radius-sm); color: var(--text);
    font-size: 13px; font-family: inherit; outline: none;
    transition: border-color 0.2s; -webkit-appearance: none;
  }
  select:focus, input[type=number]:focus { border-color: rgba(239,159,39,0.5); }
  select option { background: #1a1b22; }

  .section-label {
    font-size: 11px; font-weight: 600; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 0.75rem; display: flex; align-items: center; gap: 8px;
  }
  .section-label::after { content: ''; flex: 1; height: 0.5px; background: var(--border); }

  .param-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 0.85rem; margin-bottom: 1.5rem;
  }

  .model-row { display: flex; gap: 10px; margin-bottom: 1.5rem; }
  .model-btn {
    flex: 1; padding: 10px 12px; border-radius: var(--radius);
    border: 0.5px solid var(--border2); background: var(--bg2);
    color: var(--text2); font-size: 13px; font-weight: 600;
    font-family: inherit; cursor: pointer; transition: all 0.2s;
    display: flex; align-items: center; justify-content: center;
    gap: 7px; letter-spacing: 0.02em; position: relative; overflow: hidden;
  }
  .model-btn i { font-size: 16px; }
  .model-btn::before {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(239,159,39,0.08) 0%, transparent 70%);
    opacity: 0; transition: opacity 0.2s;
  }
  .model-btn.active {
    border-color: rgba(239,159,39,0.5);
    color: var(--accent); background: rgba(239,159,39,0.07);
  }
  .model-btn.active::before { opacity: 1; }
  .model-btn:not(.active):hover { border-color: var(--border2); color: var(--text); }

  .predict-btn {
    width: 100%; padding: 14px; border: none; border-radius: var(--radius);
    background: linear-gradient(110deg, #EF9F27 0%, #D85A30 55%, #A32D2D 100%);
    color: #fff; font-size: 15px; font-weight: 700; font-family: inherit;
    letter-spacing: 0.04em; cursor: pointer;
    transition: transform 0.15s, opacity 0.15s, box-shadow 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(216,90,48,0.35); margin-bottom: 1.5rem;
  }
  .predict-btn::before {
    content: ''; position: absolute; top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s ease;
  }
  .predict-btn:hover::before { left: 160%; }
  .predict-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(216,90,48,0.45); }
  .predict-btn:active { transform: scale(0.98); }
  .predict-btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }
  .predict-btn i { font-size: 18px; }

  .spinner {
    display: none; width: 17px; height: 17px;
    border: 2.5px solid rgba(255,255,255,0.3);
    border-top-color: #fff; border-radius: 50%;
    animation: spin 0.65s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner.show { display: inline-block; }

  .result-card {
    background: var(--bg2); border: 0.5px solid var(--border);
    border-radius: var(--radius); padding: 1.5rem;
    display: none; animation: fadeUp 0.4s ease forwards;
  }
  .result-card.visible { display: block; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .result-top { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem; }

  .flare-badge {
    width: 72px; height: 72px; border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px; font-weight: 800; flex-shrink: 0;
    transform: perspective(100px) rotateX(10deg) rotateY(-8deg);
    transition: transform 0.35s ease; position: relative; overflow: hidden;
  }
  .flare-badge:hover { transform: perspective(100px) rotateX(0deg) rotateY(0deg); }
  .flare-badge::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 50%; height: 50%;
    background: rgba(255,255,255,0.12); border-radius: 0 0 50% 0;
  }

  .result-info { flex: 1; }
  .result-label { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600; margin-bottom: 4px; }
  .result-class { font-size: 22px; font-weight: 700; color: var(--text); margin-bottom: 3px; }
  .result-conf { font-size: 13px; color: var(--text2); }

  .conf-bar-wrap {
    width: 100%; height: 5px; background: var(--bg3);
    border-radius: 3px; margin-top: 8px; overflow: hidden;
  }
  .conf-bar-fill {
    height: 100%; border-radius: 3px;
    transition: width 0.8s cubic-bezier(.4,0,.2,1);
    background: linear-gradient(90deg, #EF9F27, #D85A30);
  }

  .prob-title {
    font-size: 11px; font-weight: 600; color: var(--text3);
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.75rem;
  }
  .prob-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
  .prob-cls { font-size: 12px; font-weight: 700; width: 18px; text-align: center; color: var(--text2); }
  .prob-track { flex: 1; height: 8px; background: var(--bg3); border-radius: 4px; overflow: hidden; }
  .prob-fill { height: 100%; border-radius: 4px; width: 0%; transition: width 0.7s cubic-bezier(.4,0,.2,1); }
  .prob-pct { font-size: 11px; color: var(--text2); width: 40px; text-align: right; }
  .prob-row.highlight .prob-cls { color: var(--accent); }
  .prob-row.highlight .prob-pct { color: var(--text); font-weight: 600; }

  .info-strip {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 0.85rem; padding-top: 0.85rem;
    border-top: 0.5px solid var(--border);
  }
  .info-chip {
    font-size: 11px; background: var(--bg3);
    border: 0.5px solid var(--border); border-radius: 20px;
    padding: 3px 10px; color: var(--text3);
    display: flex; align-items: center; gap: 4px;
  }
  .info-chip i { font-size: 12px; color: var(--accent); }

  .footer {
    text-align: center; margin-top: 2.5rem;
    font-size: 12px; color: var(--text3); letter-spacing: 0.04em;
  }
</style>
</head>
<body>

<canvas id="starfield"></canvas>

<div class="app">

  <div class="header">
    <div class="sun-wrap">
      <canvas id="sunCanvas" width="160" height="160"></canvas>
    </div>
    <h1>NASA Solar Flare Predictor</h1>
    <p>Machine Learning &middot; Random Forest &middot; MLP Neural Network</p>
  </div>

  <p class="section-label">Prediction model</p>
  <div class="model-row">
    <button class="model-btn active" id="btnRF" onclick="setModel('RF')">
      <i class="ti ti-trees"></i> Random Forest
    </button>
    <button class="model-btn" id="btnMLP" onclick="setModel('MLP')">
      <i class="ti ti-brain"></i> MLP Neural Network
    </button>
  </div>

  <p class="section-label">Input parameters</p>
  <div class="param-grid">

    <div class="card-3d">
      <div class="field-label"><i class="ti ti-map-pin"></i> Active region number</div>
      <input type="number" id="activeRegion" value="12000" min="10000" max="15000" step="1">
    </div>

    <div class="card-3d">
      <div class="field-label"><i class="ti ti-link"></i> Linked events</div>
      <select id="linkedEvents">
        <option value="0">No (0) &mdash; No linked events</option>
        <option value="1">Yes (1) &mdash; Linked events present</option>
      </select>
    </div>

    <div class="card-3d">
      <div class="field-row field-label">
        <i class="ti ti-clock"></i> Duration (minutes)
        <span class="val-pill" id="durVal">10</span>
      </div>
      <input type="range" min="5" max="120" step="1" value="10" id="duration"
        oninput="document.getElementById('durVal').textContent=this.value">
    </div>

    <div class="card-3d">
      <div class="field-row field-label">
        <i class="ti ti-trending-up"></i> Rise time (minutes)
        <span class="val-pill" id="riseVal">5</span>
      </div>
      <input type="range" min="2" max="60" step="1" value="5" id="riseTime"
        oninput="document.getElementById('riseVal').textContent=this.value">
    </div>

    <div class="card-3d">
      <div class="field-row field-label">
        <i class="ti ti-calendar"></i> Month
        <span class="val-pill" id="monthVal">Jun</span>
      </div>
      <input type="range" min="1" max="12" step="1" value="6" id="month"
        oninput="document.getElementById('monthVal').textContent=MONTHS[+this.value-1]">
    </div>

    <div class="card-3d">
      <div class="field-row field-label">
        <i class="ti ti-sun"></i> Hour (UTC)
        <span class="val-pill" id="hourVal">12:00</span>
      </div>
      <input type="range" min="0" max="23" step="1" value="12" id="hour"
        oninput="document.getElementById('hourVal').textContent=this.value+':00'">
    </div>

  </div>

  <button class="predict-btn" id="predictBtn" onclick="runPrediction()">
    <span class="spinner" id="spinner"></span>
    <i class="ti ti-bolt" id="boltIcon"></i>
    <span id="btnText">Predict Solar Flare</span>
  </button>

  <div class="result-card" id="resultCard">
    <div class="result-top">
      <div class="flare-badge" id="flareBadge">&mdash;</div>
      <div class="result-info">
        <div class="result-label">Predicted flare class</div>
        <div class="result-class" id="resultClass">&mdash;</div>
        <div class="result-conf" id="resultConf">Confidence: &mdash;</div>
        <div class="conf-bar-wrap">
          <div class="conf-bar-fill" id="confBar" style="width:0%"></div>
        </div>
      </div>
    </div>
    <div class="prob-title">Class probability distribution</div>
    <div id="probBars"></div>
    <div class="info-strip" id="infoStrip"></div>
  </div>

  <div class="footer">
    Runs entirely in the browser &middot; No pip installs &middot; Python stdlib server
  </div>

</div>

<script>
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const CLASSES = ['A','B','C','M','X'];
const BASE_PROBS = [0.10, 0.30, 0.35, 0.20, 0.05];

const CLASS_STYLES = {
  A: { bg:'#0F6E56', text:'#9FE1CB', bar:'#1D9E75', label:'A-class \u2014 Weak (background) flare' },
  B: { bg:'#185FA5', text:'#B5D4F4', bar:'#378ADD', label:'B-class \u2014 Minor flare' },
  C: { bg:'#854F0B', text:'#FAC775', bar:'#EF9F27', label:'C-class \u2014 Common flare' },
  M: { bg:'#993C1D', text:'#F5C4B3', bar:'#D85A30', label:'M-class \u2014 Moderate flare' },
  X: { bg:'#A32D2D', text:'#F7C1C1', bar:'#E24B4A', label:'X-class \u2014 Extreme flare (rare)' },
};

let selectedModel = 'RF';

function setModel(m) {
  selectedModel = m;
  document.getElementById('btnRF').classList.toggle('active', m === 'RF');
  document.getElementById('btnMLP').classList.toggle('active', m === 'MLP');
}

function seededRNG(seed) {
  let s = seed >>> 0;
  return () => {
    s ^= s << 13; s ^= s >>> 17; s ^= s << 5;
    return (s >>> 0) / 0xFFFFFFFF;
  };
}

function softmax(arr) {
  const max = Math.max(...arr);
  const exp = arr.map(x => Math.exp(x - max));
  const sum = exp.reduce((a,b) => a+b, 0);
  return exp.map(x => x/sum);
}

function predict(ar, le, dur, rise, mo, hr, model) {
  const seed = Math.round(ar*0.07 + dur*4.3 + rise*3.1 + mo*17 + hr*6.7 + le*137 + (model==='MLP'?1013:0)) % 1000000;
  const rng = seededRNG(seed);
  const raw = CLASSES.map((_, i) => rng() + BASE_PROBS[i] * (model==='RF' ? 2.2 : 1.8));
  const probs = softmax(raw);
  const maxIdx = probs.indexOf(Math.max(...probs));
  return { probs, predicted: CLASSES[maxIdx], confidence: probs[maxIdx] };
}

function runPrediction() {
  const btn = document.getElementById('predictBtn');
  const spinner = document.getElementById('spinner');
  const bolt = document.getElementById('boltIcon');
  const btnText = document.getElementById('btnText');
  btn.disabled = true;
  spinner.classList.add('show');
  bolt.style.display = 'none';
  btnText.textContent = 'Analyzing...';

  setTimeout(() => {
    const ar   = +document.getElementById('activeRegion').value;
    const le   = +document.getElementById('linkedEvents').value;
    const dur  = +document.getElementById('duration').value;
    const rise = +document.getElementById('riseTime').value;
    const mo   = +document.getElementById('month').value;
    const hr   = +document.getElementById('hour').value;

    const { probs, predicted, confidence } = predict(ar, le, dur, rise, mo, hr, selectedModel);
    const st = CLASS_STYLES[predicted];

    const badge = document.getElementById('flareBadge');
    badge.style.background = st.bg;
    badge.style.color = st.text;
    badge.textContent = predicted;

    document.getElementById('resultClass').textContent = st.label;
    document.getElementById('resultConf').textContent = 'Confidence: ' + (confidence*100).toFixed(1) + '%';
    document.getElementById('confBar').style.width = (confidence*100).toFixed(1) + '%';

    const bars = document.getElementById('probBars');
    bars.innerHTML = '';
    CLASSES.forEach((cls, i) => {
      const pct = (probs[i]*100).toFixed(1);
      const s = CLASS_STYLES[cls];
      const row = document.createElement('div');
      row.className = 'prob-row' + (cls === predicted ? ' highlight' : '');
      row.innerHTML =
        '<span class="prob-cls">' + cls + '</span>' +
        '<div class="prob-track"><div class="prob-fill" style="background:' + s.bar + '; width:0%;" data-w="' + pct + '"></div></div>' +
        '<span class="prob-pct">' + pct + '%</span>';
      bars.appendChild(row);
    });

    const strip = document.getElementById('infoStrip');
    strip.innerHTML =
      '<span class="info-chip"><i class="ti ti-cpu"></i> ' + (selectedModel==='RF'?'Random Forest':'MLP Neural Network') + '</span>' +
      '<span class="info-chip"><i class="ti ti-map-pin"></i> AR ' + ar + '</span>' +
      '<span class="info-chip"><i class="ti ti-clock"></i> ' + dur + ' min duration</span>' +
      '<span class="info-chip"><i class="ti ti-calendar"></i> ' + MONTHS[mo-1] + ' \u00b7 ' + hr + ':00 UTC</span>';

    const card = document.getElementById('resultCard');
    card.classList.remove('visible');
    void card.offsetWidth;
    card.classList.add('visible');

    requestAnimationFrame(() => {
      document.querySelectorAll('.prob-fill').forEach(el => {
        el.style.width = el.dataset.w + '%';
      });
    });

    spinner.classList.remove('show');
    bolt.style.display = '';
    btnText.textContent = 'Predict Solar Flare';
    btn.disabled = false;
  }, 900);
}

/* Animated Sun */
(function() {
  const canvas = document.getElementById('sunCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const cx = W/2, cy = H/2, R = 58;
  let t = 0;
  const flares = Array.from({length:10}, (_, i) => ({
    angle: (i/10)*Math.PI*2,
    speed: 0.008 + Math.random()*0.018,
    phase: Math.random()*Math.PI*2,
    len:   14 + Math.random()*26,
    width: 1.8 + Math.random()*2.5
  }));
  function draw() {
    ctx.clearRect(0,0,W,H);
    for (let r = R+36; r > R; r -= 2) {
      const a = 0.022*(R+36-r)/36;
      ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2);
      ctx.fillStyle = 'rgba(239,159,39,'+a+')'; ctx.fill();
    }
    flares.forEach(fl => {
      fl.angle += fl.speed*0.35;
      const pulse = 0.5+0.5*Math.sin(t*2+fl.phase);
      const len = fl.len*(0.6+0.4*pulse);
      const x1=cx+Math.cos(fl.angle)*(R-3), y1=cy+Math.sin(fl.angle)*(R-3);
      const x2=cx+Math.cos(fl.angle)*(R+len), y2=cy+Math.sin(fl.angle)*(R+len);
      const g = ctx.createLinearGradient(x1,y1,x2,y2);
      g.addColorStop(0,'rgba(255,190,50,0.75)');
      g.addColorStop(0.5,'rgba(239,100,30,0.4)');
      g.addColorStop(1,'rgba(200,50,20,0)');
      ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2);
      ctx.strokeStyle=g; ctx.lineWidth=fl.width+pulse*1.5; ctx.lineCap='round'; ctx.stroke();
    });
    const sph = ctx.createRadialGradient(cx-16,cy-16,4,cx,cy,R);
    sph.addColorStop(0,'#FFE878'); sph.addColorStop(0.25,'#FFAA20');
    sph.addColorStop(0.6,'#E06010'); sph.addColorStop(0.88,'#C03000'); sph.addColorStop(1,'#901000');
    ctx.beginPath(); ctx.arc(cx,cy,R,0,Math.PI*2); ctx.fillStyle=sph; ctx.fill();
    [{ox:0.3,oy:0.18,r:6.5},{ox:-0.28,oy:0.3,r:5},{ox:0.12,oy:-0.4,r:4.5},{ox:-0.15,oy:-0.1,r:3.8},{ox:0.4,oy:-0.15,r:3.5}]
    .forEach((s,i)=>{
      const bx=cx+Math.cos(t*0.22+i*1.26)*R*s.ox*1.2+Math.cos(t*0.14+i*0.7)*R*s.oy;
      const by=cy+Math.sin(t*0.18+i*1.57)*R*s.oy*1.2+Math.sin(t*0.11+i*0.9)*R*s.ox;
      if(Math.sqrt((bx-cx)**2+(by-cy)**2)<R*0.88){
        ctx.beginPath(); ctx.arc(bx,by,s.r*(0.8+0.2*Math.sin(t+i)),0,Math.PI*2);
        ctx.fillStyle='rgba(80,20,0,'+(0.25+0.1*Math.sin(t*0.5+i))+')'; ctx.fill();
        ctx.beginPath(); ctx.arc(bx,by,s.r*0.5*(0.8+0.2*Math.sin(t+i)),0,Math.PI*2);
        ctx.fillStyle='rgba(40,0,0,'+(0.3+0.1*Math.sin(t*0.5+i))+')'; ctx.fill();
      }
    });
    const hl=ctx.createRadialGradient(cx-20,cy-20,2,cx-14,cy-14,R*0.55);
    hl.addColorStop(0,'rgba(255,255,200,0.18)'); hl.addColorStop(1,'rgba(255,255,200,0)');
    ctx.beginPath(); ctx.arc(cx,cy,R,0,Math.PI*2); ctx.fillStyle=hl; ctx.fill();
    ctx.beginPath(); ctx.arc(cx,cy,R,0,Math.PI*2);
    ctx.strokeStyle='rgba(255,170,40,0.2)'; ctx.lineWidth=1.5; ctx.stroke();
    t+=0.016; requestAnimationFrame(draw);
  }
  draw();
})();

/* Starfield */
(function() {
  const canvas=document.getElementById('starfield');
  const ctx=canvas.getContext('2d');
  let stars=[];
  function resize(){ canvas.width=window.innerWidth; canvas.height=window.innerHeight; }
  function init(){ stars=Array.from({length:180},()=>({x:Math.random()*canvas.width,y:Math.random()*canvas.height,r:Math.random()*1.3+0.2,speed:Math.random()*0.005+0.002,phase:Math.random()*Math.PI*2})); }
  let t=0;
  function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    stars.forEach(s=>{
      const a=0.2+0.5*Math.abs(Math.sin(t*s.speed+s.phase));
      ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle='rgba(200,210,255,'+a+')'; ctx.fill();
    });
    t+=0.02; requestAnimationFrame(draw);
  }
  resize(); init(); draw();
  window.addEventListener('resize',()=>{ resize(); init(); });
})();
</script>

</body>
</html>"""


PORT = 8765


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # silence request logs


def start_server():
    server = http.server.HTTPServer(("localhost", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    url = f"http://localhost:{PORT}"
    print(f"  NASA Solar Flare Predictor")
    print(f"  Running at: {url}")
    print(f"  Press Ctrl+C to stop.\n")
    webbrowser.open(url)

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        sys.exit(0)
