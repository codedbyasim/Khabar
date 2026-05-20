"""
dashboard_server.py — KHABAR Real-Time Web Dashboard
FR-23: Before/after state | FR-24: P1-P5 queue | FR-25: Agent trace | FR-26: Auto-refresh
Run: python dashboard_server.py  →  http://127.0.0.1:8001
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="KHABAR Dashboard")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KHABAR — Crisis Intelligence Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0a0f1e;color:#e2e8f0;min-height:100vh}
:root{--teal:#00d4aa;--red:#ff4757;--orange:#ffa502;--green:#2ed573;--blue:#1e90ff;--dark:#0a0f1e;--card:#111827;--border:#1f2937}
header{background:linear-gradient(135deg,#0d1b2a,#1a2744);padding:16px 24px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,var(--teal),#0099aa);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo h1{font-size:20px;font-weight:800;background:linear-gradient(135deg,var(--teal),#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.logo p{font-size:11px;color:#64748b;margin-top:1px}
.status-bar{display:flex;align-items:center;gap:20px}
.live-dot{width:8px;height:8px;background:var(--green);border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.3)}}
.live-text{font-size:12px;color:var(--green);font-weight:600}
.refresh-info{font-size:11px;color:#64748b}
.main{padding:24px;display:grid;grid-template-columns:1fr 1fr;gap:20px;max-width:1400px;margin:0 auto}
.full-width{grid-column:1/-1}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between}
.card-title{font-size:14px;font-weight:700;color:#f1f5f9;display:flex;align-items:center;gap:8px}
.card-title .icon{font-size:16px}
.card-body{padding:20px}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;text-align:center}
.stat-val{font-size:28px;font-weight:800;margin-bottom:4px}
.stat-label{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.p1{color:var(--red)}.p2{color:var(--orange)}.p3{color:#facc15}.p4{color:var(--blue)}.p5{color:var(--green)}
.priority-badge{display:inline-flex;align-items:center;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700}
.badge-p1{background:rgba(255,71,87,.15);color:var(--red);border:1px solid rgba(255,71,87,.3)}
.badge-p2{background:rgba(255,165,2,.15);color:var(--orange);border:1px solid rgba(255,165,2,.3)}
.badge-p3{background:rgba(250,204,21,.15);color:#facc15;border:1px solid rgba(250,204,21,.3)}
.badge-p4{background:rgba(30,144,255,.15);color:var(--blue);border:1px solid rgba(30,144,255,.3)}
.badge-p5{background:rgba(46,213,115,.15);color:var(--green);border:1px solid rgba(46,213,115,.3)}
.badge-proc{background:rgba(0,212,170,.15);color:var(--teal);border:1px solid rgba(0,212,170,.3)}
.incident-item{background:#0d1520;border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:12px;cursor:pointer;transition:border-color .2s,transform .2s}
.incident-item:hover{border-color:var(--teal);transform:translateY(-1px)}
.incident-item.active-item{border-color:var(--teal);box-shadow:0 0 0 1px var(--teal)}
.inc-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.inc-id{font-family:'Courier New',monospace;font-size:13px;font-weight:700;color:var(--teal)}
.inc-type{font-size:12px;color:#94a3b8;margin-bottom:6px;text-transform:capitalize}
.inc-location{font-size:11px;color:#64748b;display:flex;align-items:center;gap:4px}
.status-chip{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600}
.chip-processing{background:rgba(0,212,170,.1);color:var(--teal)}
.chip-complete{background:rgba(46,213,115,.1);color:var(--green)}
.chip-manual{background:rgba(255,71,87,.1);color:var(--red)}
.chip-open{background:rgba(100,116,139,.1);color:#94a3b8}
.trace-list{max-height:280px;overflow-y:auto;display:flex;flex-direction:column;gap:6px}
.trace-item{background:#0d1520;border-left:3px solid var(--border);padding:8px 12px;border-radius:0 8px 8px 0;font-size:11px;font-family:'Courier New',monospace;line-height:1.5;color:#94a3b8}
.trace-item.trace-detection{border-left-color:#60a5fa}
.trace-item.trace-analysis{border-left-color:#a78bfa}
.trace-item.trace-planning{border-left-color:#34d399}
.trace-item.trace-execution{border-left-color:var(--teal)}
.trace-item.trace-pipeline{border-left-color:var(--green)}
.trace-item.trace-error{border-left-color:var(--red)}
.trace-item.trace-ingestion{border-left-color:#94a3b8}
.trace-phase{font-weight:700;margin-right:6px}
.before-after{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center}
.state-box{background:#0d1520;border:1px solid var(--border);border-radius:12px;padding:14px}
.state-box h4{font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;margin-bottom:10px}
.state-box.before h4{color:#94a3b8}
.state-box.after h4{color:var(--green)}
.state-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid rgba(31,41,55,.5);font-size:12px}
.state-row:last-child{border:none}
.state-key{color:#64748b}.state-val{font-weight:600;color:#e2e8f0}
.state-val.changed{color:var(--green)}
.arrow-icon{font-size:24px;color:var(--teal)}
.resource-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.res-item{background:#0d1520;border:1px solid var(--border);border-radius:10px;padding:12px}
.res-name{font-size:12px;color:#94a3b8;margin-bottom:4px}
.res-count{font-size:22px;font-weight:800;color:var(--teal)}
.res-status{font-size:11px;color:#64748b;margin-top:2px}
.agent-pipeline{display:flex;align-items:center;gap:8px;padding:16px 0}
.agent-step{flex:1;text-align:center}
.agent-circle{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;margin:0 auto 8px;transition:all .3s}
.agent-circle.done{background:linear-gradient(135deg,var(--teal),#0099aa);box-shadow:0 0 16px rgba(0,212,170,.4)}
.agent-circle.waiting{background:#1f2937;border:2px solid var(--border)}
.agent-circle.active{background:#1a2744;border:2px solid var(--teal);animation:spin-glow 2s infinite}
@keyframes spin-glow{0%,100%{box-shadow:0 0 8px rgba(0,212,170,.3)}50%{box-shadow:0 0 20px rgba(0,212,170,.6)}}
.agent-label{font-size:11px;color:#64748b;font-weight:500}
.agent-connector{width:20px;height:2px;background:var(--border)}
.agent-connector.done{background:var(--teal)}
.empty-state{text-align:center;padding:40px;color:#475569}
.empty-state .icon{font-size:40px;margin-bottom:12px}
.empty-state p{font-size:13px}
.alert-hist{max-height:200px;overflow-y:auto}
.alert-item{display:flex;justify-content:space-between;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--border);gap:12px}
.alert-item:last-child{border:none}
.alert-msg{font-size:12px;color:#e2e8f0;flex:1;line-height:1.4}
.alert-count{font-size:11px;color:var(--teal);white-space:nowrap;font-weight:600}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:#334155;border-radius:2px}
.no-data{color:#475569;font-size:12px;text-align:center;padding:20px}
.injector-grid{display:grid;grid-template-columns:repeat(5, 1fr);gap:12px;padding:16px}
.inject-btn{border:none;border-radius:10px;padding:12px;color:#fff;font-weight:700;font-size:11px;cursor:pointer;transition:all 0.2s;text-align:left;display:flex;flex-direction:column;gap:4px;box-shadow:0 4px 6px rgba(0,0,0,0.15);width:100%}
.inject-btn:hover{transform:translateY(-2px);box-shadow:0 6px 12px rgba(0,0,0,0.25)}
.inject-btn .priority{font-size:9px;padding:2px 6px;border-radius:4px;width:max-content;font-weight:800}
.inject-btn.btn-p1{background:linear-gradient(135deg, #e74c3c, #c0392b)}
.inject-btn.btn-p1 .priority{background:rgba(255,255,255,0.2);color:#fff}
.inject-btn.btn-p2{background:linear-gradient(135deg, #e67e22, #d35400)}
.inject-btn.btn-p2 .priority{background:rgba(255,255,255,0.2);color:#fff}
.inject-btn.btn-p3{background:linear-gradient(135deg, #f1c40f, #f39c12);color:#111}
.inject-btn.btn-p3 .priority{background:rgba(0,0,0,0.15);color:#111}
.inject-btn .sc-title{font-size:11px;font-weight:700;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.inject-btn .sc-desc{font-size:9px;opacity:0.8;font-weight:400;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
</style>
</head>
<body>
<header>
  <div class="logo">
    <div class="logo-icon">🚨</div>
    <div>
      <h1>KHABAR Dashboard</h1>
      <p>Crisis Intelligence & Response Orchestrator — Google Gemini 2.5 Flash</p>
    </div>
  </div>
  <div class="status-bar">
    <div class="live-dot"></div>
    <span class="live-text">LIVE</span>
    <span class="refresh-info" id="refresh-timer">Auto-refresh in 5s</span>
  </div>
</header>

<div class="main">
  <!-- Demo Scenarios Quick-Inject -->
  <div class="card full-width">
    <div class="card-header">
      <span class="card-title"><span class="icon">🎯</span> Appendix B: Demo Scenario Injector</span>
      <span style="font-size:11px;color:#64748b">1-Click to trigger live 4-agent pipeline</span>
    </div>
    <div class="injector-grid">
      <button class="inject-btn btn-p1" onclick="injectScenario(1)">
        <span class="priority">P1 CRITICAL</span>
        <span class="sc-title">G-10 Islamabad Flood</span>
        <span class="sc-desc">"Pani bhar gaya hai, gaariyan phans..."</span>
      </button>
      <button class="inject-btn btn-p1" onclick="injectScenario(2)">
        <span class="priority">P1 CRITICAL</span>
        <span class="sc-title">F-7 Plaza Collapse</span>
        <span class="sc-desc">Photo Damage Assessment (Collapse)</span>
      </button>
      <button class="inject-btn btn-p2" onclick="injectScenario(3)">
        <span class="priority">P2 HIGH</span>
        <span class="sc-title">Murree Road Accident</span>
        <span class="sc-desc">Photo Pile-up Accident Scene</span>
      </button>
      <button class="inject-btn btn-p2" onclick="injectScenario(4)">
        <span class="priority">P2 HIGH</span>
        <span class="sc-title">DHA Lahore Heatwave</span>
        <span class="sc-desc">Weather Alert: 47°C Extreme Temp</span>
      </button>
      <button class="inject-btn btn-p3" onclick="injectScenario(5)">
        <span class="priority">P3 STANDARD</span>
        <span class="sc-title">IJP Road Blockage</span>
        <span class="sc-desc">"Sadak band hai, pipe toot gayi"</span>
      </button>
    </div>
  </div>

  <!-- Stats Row -->
  <div class="stat-grid full-width" id="stats-row">
    <div class="stat-card"><div class="stat-val p1" id="cnt-p1">—</div><div class="stat-label">P1 Critical</div></div>
    <div class="stat-card"><div class="stat-val p2" id="cnt-p2">—</div><div class="stat-label">P2 High</div></div>
    <div class="stat-card"><div class="stat-val p3" id="cnt-total">—</div><div class="stat-label">Total Incidents</div></div>
    <div class="stat-card"><div class="stat-val" style="color:var(--teal)" id="cnt-alerts">—</div><div class="stat-label">Alerts Sent</div></div>
  </div>

  <!-- Incident Queue -->
  <div class="card">
    <div class="card-header">
      <span class="card-title"><span class="icon">📋</span> Incident Queue (P1→P5)</span>
      <span id="queue-count" style="font-size:12px;color:#64748b"></span>
    </div>
    <div class="card-body" style="max-height:520px;overflow-y:auto;" id="incident-list">
      <div class="empty-state"><div class="icon">📡</div><p>Waiting for incidents...</p></div>
    </div>
  </div>

  <!-- Agent Pipeline + Trace -->
  <div class="card">
    <div class="card-header">
      <span class="card-title"><span class="icon">🤖</span> Agent Trace</span>
      <span id="selected-inc-id" style="font-size:11px;color:var(--teal);font-family:monospace"></span>
    </div>
    <div class="card-body">
      <div class="agent-pipeline" id="agent-pipeline">
        <div class="agent-step"><div class="agent-circle waiting">🔍</div><div class="agent-label">Detection</div></div>
        <div class="agent-connector"></div>
        <div class="agent-step"><div class="agent-circle waiting">📊</div><div class="agent-label">Analysis</div></div>
        <div class="agent-connector"></div>
        <div class="agent-step"><div class="agent-circle waiting">💡</div><div class="agent-label">Planning</div></div>
        <div class="agent-connector"></div>
        <div class="agent-step"><div class="agent-circle waiting">⚡</div><div class="agent-label">Execution</div></div>
      </div>
      <div class="trace-list" id="trace-list">
        <div class="no-data">Select an incident to view trace</div>
      </div>
    </div>
  </div>

  <!-- Before / After State -->
  <div class="card full-width" id="before-after-card" style="display:none">
    <div class="card-header">
      <span class="card-title"><span class="icon">🔄</span> Before → After State Comparison</span>
      <span style="font-size:11px;color:var(--green);font-weight:600">✅ Simulation Complete</span>
    </div>
    <div class="card-body">
      <div class="before-after" id="before-after-content"></div>
    </div>
  </div>

  <!-- Resources -->
  <div class="card">
    <div class="card-header"><span class="card-title"><span class="icon">🚑</span> Resource Inventory</span></div>
    <div class="card-body">
      <div class="resource-grid" id="resource-grid">
        <div class="no-data">Loading resources...</div>
      </div>
    </div>
  </div>

  <!-- Alert History -->
  <div class="card">
    <div class="card-header"><span class="card-title"><span class="icon">📢</span> Alert Broadcast Log</span></div>
    <div class="card-body">
      <div class="alert-hist" id="alert-hist">
        <div class="no-data">No alerts sent yet</div>
      </div>
    </div>
  </div>
</div>

<script>
const API = 'http://127.0.0.1:8000';
let selectedId = null;
let countdown = 5;
let allIncidents = [];

async function injectScenario(id){
  let payload = {};
  if (id === 1) {
    payload = { text: "G-10 Islamabad mein pani bhar gaya hai, gaariyan doob rahi hain aur log phans gaye hain!", lat: 33.6938, lng: 73.0551 };
  } else if (id === 2) {
    payload = { text: "[PHOTO REPORT] F-7 Markaz Plaza structural collapse. Heavy debris blocking main market and people trapped under debris.", lat: 33.7245, lng: 73.0629 };
  } else if (id === 3) {
    payload = { text: "[PHOTO REPORT] Massive multi-vehicle pile-up accident on Murree Road involving a bus and two cars. Road completely blocked, traffic halted.", lat: 33.6105, lng: 73.0783 };
  } else if (id === 4) {
    payload = { text: "DHA Lahore Heatwave alert issued. Local temperatures rising rapidly to 47 degrees Celsius.", lat: 31.4697, lng: 74.4082 };
  } else if (id === 5) {
    payload = { text: "IJP Road Rawalpindi block hai, road par bada gas pipeline blast ya main pipe toot gayi hai.", lat: 33.6392, lng: 73.0844 };
  }
  
  try {
    const btn = event.currentTarget;
    const oldText = btn.innerHTML;
    btn.innerHTML = `<span class="priority">SENDING...</span><span class="sc-title">Injecting...</span><span class="sc-desc">Running Agent Chain</span>`;
    btn.disabled = true;

    const r = await fetch(`${API}/report/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    
    setTimeout(() => {
      btn.innerHTML = oldText;
      btn.disabled = false;
    }, 1500);

    if (d.success) {
      selectedId = d.incident_id;
      tick();
    }
  } catch(e) {
    console.error("Failed to inject scenario:", e);
    alert("Error triggering scenario. Make sure your api_server is running on http://127.0.0.1:8000");
  }
}

const PHASE_COLORS = {
  DETECTION:'trace-detection', ANALYSIS:'trace-analysis',
  PLANNING:'trace-planning', EXECUTION:'trace-execution',
  PIPELINE_COMPLETE:'trace-pipeline', INGESTION:'trace-ingestion',
  FALLBACK:'trace-error', DETECTION_ERROR:'trace-error',
  ANALYSIS_ERROR:'trace-error', PLANNING_ERROR:'trace-error', EXECUTION_ERROR:'trace-error'
};

function getPriorityBadge(p){
  return `<span class="priority-badge badge-${(p||'p5').toLowerCase()}">${p||'—'}</span>`;
}
function getStatusChip(s){
  const map={'PROCESSING':'chip-processing','PIPELINE_COMPLETE':'chip-complete','MANUAL_REVIEW_REQUIRED':'chip-manual','OPEN':'chip-open'};
  const cls = map[s]||'chip-open';
  return `<span class="status-chip ${cls}">${s||'UNKNOWN'}</span>`;
}

async function fetchIncidents(){
  try{
    const r = await fetch(`${API}/incidents`);
    const d = await r.json();
    allIncidents = d.incidents||[];
    renderQueue(allIncidents);
    updateStats(allIncidents, d.resource_summary);
    if(selectedId){
      const found = allIncidents.find(i=>i.incident_id===selectedId);
      if(found) renderDetail(found);
    }
  }catch(e){ console.error('Fetch incidents failed',e); }
}

async function fetchResources(){
  try{
    const r = await fetch(`${API}/resources`);
    const d = await r.json();
    renderResources(d.summary, d.resources);
  }catch(e){}
}

function updateStats(incidents, resourceSummary){
  const p1 = incidents.filter(i=>i.priority==='P1').length;
  const p2 = incidents.filter(i=>i.priority==='P2').length;
  const totalAlerts = incidents.reduce((sum,i)=>sum+(i.public_alerts_sent||0),0);
  document.getElementById('cnt-p1').textContent = p1;
  document.getElementById('cnt-p2').textContent = p2;
  document.getElementById('cnt-total').textContent = incidents.length;
  document.getElementById('cnt-alerts').textContent = totalAlerts;
}

function renderQueue(incidents){
  const el = document.getElementById('incident-list');
  document.getElementById('queue-count').textContent = `${incidents.length} incidents`;
  if(!incidents.length){
    el.innerHTML='<div class="empty-state"><div class="icon">📡</div><p>No incidents yet. Submit a report via the Flutter app or POST /report/text</p></div>';
    return;
  }
  el.innerHTML = incidents.map(inc=>{
    const loc = inc.location ? `${inc.location.area||''} ${inc.location.city||''}`.trim() : (inc.lat ? `${inc.lat?.toFixed(4)},${inc.lng?.toFixed(4)}` : 'Unknown');
    const isActive = inc.incident_id === selectedId;
    return `<div class="incident-item${isActive?' active-item':''}" onclick="selectIncident('${inc.incident_id}')">
      <div class="inc-header">
        <span class="inc-id">${inc.incident_id}</span>
        <div style="display:flex;gap:6px;align-items:center">
          ${getPriorityBadge(inc.priority)}
          ${getStatusChip(inc.status)}
        </div>
      </div>
      <div class="inc-type">🔥 ${(inc.incident_type||inc.source||'Unknown').replace(/_/g,' ')}</div>
      <div class="inc-location">📍 ${loc} ${inc.confidence ? `• Confidence: ${Math.round(inc.confidence*100)}%` : ''}</div>
    </div>`;
  }).join('');
}

function selectIncident(id){
  selectedId = id;
  document.getElementById('selected-inc-id').textContent = id;
  document.querySelectorAll('.incident-item').forEach(el=>el.classList.remove('active-item'));
  event.currentTarget.classList.add('active-item');
  const inc = allIncidents.find(i=>i.incident_id===id);
  if(inc) renderDetail(inc);
}

function renderDetail(inc){
  // Agent pipeline status
  const traces = inc.traces || [];
  const phases = traces.map(t=>{const m=t.match(/\[(.*?)\]/g);return m&&m[1]?m[1].replace(/[\[\]]/g,''):'';});
  const hasDet = phases.some(p=>p==='DETECTION');
  const hasAna = phases.some(p=>p==='ANALYSIS');
  const hasPlan = phases.some(p=>p==='PLANNING');
  const hasExec = phases.some(p=>p==='EXECUTION'||p==='PIPELINE_COMPLETE');
  const isProc = inc.status==='PROCESSING'||phases.some(p=>p.includes('Attempt'));

  const steps = [
    {icon:'🔍',label:'Detection',done:hasDet},
    {icon:'📊',label:'Analysis',done:hasAna},
    {icon:'💡',label:'Planning',done:hasPlan},
    {icon:'⚡',label:'Execution',done:hasExec},
  ];
  document.getElementById('agent-pipeline').innerHTML = steps.map((s,i)=>`
    <div class="agent-step">
      <div class="agent-circle ${s.done?'done':(isProc&&!s.done&&steps[i-1]?.done)?'active':'waiting'}">${s.icon}</div>
      <div class="agent-label">${s.label}</div>
    </div>
    ${i<steps.length-1?`<div class="agent-connector ${s.done?'done':''}"></div>`:''}
  `).join('');

  // Traces
  const traceEl = document.getElementById('trace-list');
  if(!traces.length){
    traceEl.innerHTML='<div class="no-data">No traces yet</div>';
  }else{
    traceEl.innerHTML = traces.slice().reverse().map(t=>{
      const m = t.match(/\[.*?\] \[(.*?)\] (.*)/);
      const phase = m?m[1]:'SYSTEM';
      const msg = m?m[2]:t;
      const ts = t.match(/\[(.*?)\]/)?.[1]?.split('T')[1]?.split('.')[0]||'';
      const cls = PHASE_COLORS[phase]||'';
      return `<div class="trace-item ${cls}"><span class="trace-phase">[${phase}]</span><span style="color:#475569;margin-right:6px">${ts}</span>${msg}</div>`;
    }).join('');
    traceEl.scrollTop = 0;
  }

  // Before / After
  const baCard = document.getElementById('before-after-card');
  if(inc.before_state && inc.after_state){
    baCard.style.display='block';
    const b = inc.before_state, a = inc.after_state;
    const diff = inc.state_diff?.changed_keys||[];
    const rows = (obj, isBefore)=> Object.entries({
      'Status': obj.status||'—',
      'Active Units': Object.keys(obj.active_units||{}).length > 0 ? JSON.stringify(obj.active_units) : '0',
      'Alerts Sent': obj.public_alerts_sent||0,
      'Roads Closed': (obj.closed_roads||[]).length,
      'Tickets': (obj.tickets||[]).length,
    }).map(([k,v])=>`<div class="state-row"><span class="state-key">${k}</span><span class="state-val ${!isBefore&&diff.includes(k.toLowerCase().replace(' ','_'))?'changed':''}">${v}</span></div>`).join('');

    document.getElementById('before-after-content').innerHTML = `
      <div class="state-box before"><h4>⬛ Before Response</h4>${rows(b,true)}</div>
      <div class="arrow-icon">→</div>
      <div class="state-box after"><h4>✅ After Response</h4>${rows(a,false)}</div>`;
  }else{
    baCard.style.display='none';
  }
}

function renderResources(summary, resources){
  const el = document.getElementById('resource-grid');
  if(!summary){el.innerHTML='<div class="no-data">No data</div>';return;}
  el.innerHTML = `
    <div class="res-item"><div class="res-name">🚒 Rescue Teams</div><div class="res-count">${summary.rescue_teams?.available||0}</div><div class="res-status">Available | ${summary.rescue_teams?.en_route||0} en route</div></div>
    <div class="res-item"><div class="res-name">🚑 Ambulances</div><div class="res-count">${summary.ambulances?.available||0}</div><div class="res-status">Available | ${summary.ambulances?.en_route||0} dispatched</div></div>
    <div class="res-item"><div class="res-name">💧 Dewatering Pumps</div><div class="res-count">${summary.dewatering_pumps?.available||0}</div><div class="res-status">WASA Depot</div></div>
    <div class="res-item"><div class="res-name">🧰 Medical Kits</div><div class="res-count">${summary.medical_kits?.available||0}</div><div class="res-status">Central Depot</div></div>`;
}

async function tick(){
  await fetchIncidents();
  await fetchResources();
  countdown = 5;
}

setInterval(()=>{
  countdown--;
  document.getElementById('refresh-timer').textContent = `Auto-refresh in ${countdown}s`;
  if(countdown<=0) tick();
},1000);

tick();
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  KHABAR Web Dashboard")
    print("  Open: http://127.0.0.1:8001")
    print("="*55 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
