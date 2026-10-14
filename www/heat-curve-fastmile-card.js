class HeatCurveFastmileCard extends HTMLElement {
  setConfig(config) {
    this.config = config || {};
    this.attachShadow({mode:"open"});
  }
  set hass(hass) { this._hass=hass; this.render(); }
  getCardSize(){ return 10; }
  v(id, fallback="—"){ const s=this._hass?.states?.[id]; return s ? s.state : fallback; }
  a(id,key,fallback=null){ return this._hass?.states?.[id]?.attributes?.[key] ?? fallback; }
  esc(v){ return String(v??"—").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m])); }
  render(){
    if(!this.shadowRoot||!this._hass)return;
    const rec=this.v("sensor.recommendation","collecting"), adj=this.a("sensor.recommendation","recommended_adjustment_c",0);
    const conf=this.v("sensor.confidence","0"), cov=this.v("sensor.data_coverage","0");
    const zones=this.a("sensor.recommendation","zones",{})||{}, rooms=this.a("sensor.recommendation","room_diagnostics",{})||{};
    const hyd=this.a("sensor.recommendation","hydraulic_diagnostics",{})||{}, curve=this.a("sensor.recommendation","curve_shape_advice",{})||{};
    const profile=this.a("sensor.recommendation","house_profile",{})||{}, response=this.a("sensor.recommendation","estimated_response_hours",null);
    const reason=this.a("sensor.recommendation","reason",this.v("sensor.diagnostic_reason",""));
    const outside=this.a("sensor.recommendation","outdoor_average","—");
    const target=this.a("sensor.recommendation","target_average","—");
    const status=rec==="raise"?"Podnieś":rec==="lower"?"Obniż":rec==="no_change"?"Bez zmian":rec==="zone_conflict"?"Konflikt stref":rec;
    const roomRows=Object.entries(rooms.rooms||{}).map(([id,r])=>`<div class="row"><span>${this.esc(id.split(".").pop().replaceAll("_"," "))}</span><b>${this.esc(r.average)} °C</b><em class="${r.error>0.3?"bad":r.error<-.3?"warn":"ok"}">${r.error>0?"+":""}${this.esc(r.error)} °C</em></div>`).join("")||'<div class="muted">Dane pojawią się po zebraniu historii.</div>';
    const profileBars=Object.entries(profile).map(([k,p])=>{const e=Number(p.average_error||0),h=Math.min(46,8+Math.abs(e)*30);return `<div class="barwrap"><div class="bar ${e>0.3?"cold":e<-.3?"hot":"good"}" style="height:${h}px"></div><small>${this.esc(k)}</small><b>${e>0?"+":""}${e.toFixed(1)}</b></div>`}).join("");
    this.shadowRoot.innerHTML=`
<style>
:host{display:block;font-family:Inter,Roboto,Arial,sans-serif;color:#eaf2ff}.shell{background:linear-gradient(145deg,#08131f,#0b1b2b);border:1px solid #20364d;border-radius:22px;padding:22px;box-shadow:0 18px 50px #0007}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.brand{display:flex;gap:14px;align-items:center}.logo{font-size:26px;font-weight:900;letter-spacing:2px}.sub,.muted{color:#8fa5bc;font-size:13px}.weather{text-align:right;font-size:25px;font-weight:700}.grid{display:grid;grid-template-columns:1.05fr 1.15fr;gap:14px}.card{background:linear-gradient(145deg,#102235,#0c1928);border:1px solid #284059;border-radius:16px;padding:18px;min-width:0}.card h3{margin:0 0 14px;font-size:18px}.status{display:flex;align-items:center;gap:10px;color:#42e696;font-weight:700}.dot{width:12px;height:12px;border-radius:50%;background:#42e696;box-shadow:0 0 18px #42e696}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:15px}.metric{background:#0b1826;border-radius:12px;padding:12px}.metric b{display:block;font-size:22px;margin-top:5px}.recommend{display:grid;grid-template-columns:.8fr 1.2fr;gap:12px}.big{font-size:38px;font-weight:800;color:#5aa7ff}.btn{margin-top:13px;background:#0879ff;border:0;color:white;border-radius:10px;padding:13px 16px;width:100%;font-weight:700;cursor:pointer}.btn:disabled{opacity:.4;cursor:not-allowed}.lower{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}.row{display:grid;grid-template-columns:1fr auto auto;gap:14px;padding:9px 0;border-bottom:1px solid #23374a;text-transform:capitalize}.row em{font-style:normal}.ok{color:#43e58f}.warn{color:#ff9c45}.bad{color:#ff5f63}.bars{height:100px;display:flex;align-items:flex-end;gap:10px}.barwrap{height:92px;flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center}.bar{width:70%;min-width:16px;border-radius:5px 5px 2px 2px}.cold{background:#2479e8}.hot{background:#ff8a2b}.good{background:#38cf80}.barwrap small{font-size:9px;color:#91a8bf;margin-top:4px}.barwrap b{font-size:10px}.kv{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #23374a}.curve{font-size:22px;color:#62aaff;font-weight:800}@media(max-width:850px){.grid{grid-template-columns:1fr}.lower{grid-template-columns:1fr}.recommend{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr}.top{align-items:flex-start}.logo{font-size:21px}}
</style>
<div class="shell">
 <div class="top"><div class="brand"><ha-icon icon="mdi:home-thermometer-outline"></ha-icon><div><div class="logo">HEAT CURVE</div><div class="sub">FastMile style · inteligentny doradca ogrzewania</div></div></div><div class="weather">${this.esc(outside)} °C<div class="sub">na zewnątrz</div></div></div>
 <div class="grid">
  <section class="card"><h3>Stan systemu</h3><div class="status"><i class="dot"></i>${this.v("switch.data_collection")==="on"?"Zbieranie danych aktywne":"Zbieranie wstrzymane"}</div><div class="metrics"><div class="metric"><span>Pokrycie</span><b>${this.esc(cov)}%</b></div><div class="metric"><span>Pewność</span><b>${this.esc(conf)}%</b></div><div class="metric"><span>Cel</span><b>${this.esc(target)}°</b></div></div></section>
  <section class="card"><h3>Rekomendacja</h3><div class="recommend"><div><div class="big">${adj>0?"+":""}${this.esc(adj)} °C</div><div class="curve">${this.esc(status)}</div></div><div class="muted">${this.esc(reason)}</div></div><button class="btn" id="applied" ${!["raise","lower"].includes(rec)?"disabled":""}>✓ Zastosowałem rekomendację</button></section>
  <div class="lower">
   <section class="card"><h3>Pomieszczenia</h3>${roomRows}</section>
   <section class="card"><h3>Nauka budynku</h3><div class="kv"><span>Czas reakcji</span><b>${response??"uczę się"}${response?" h":""}</b></div><div class="kv"><span>Wniosek krzywej</span><b>${this.esc(curve.recommendation||"wait")}</b></div><div class="bars">${profileBars||'<span class="muted">Za mało danych profilu.</span>'}</div></section>
   <section class="card"><h3>Instalacja</h3><div class="kv"><span>Zasilanie</span><b>${this.esc(hyd.supply_average)} °C</b></div><div class="kv"><span>Powrót</span><b>${this.esc(hyd.return_average)} °C</b></div><div class="kv"><span>ΔT</span><b>${this.esc(hyd.delta_t_average)} °C</b></div><div class="kv"><span>Status hydrauliki</span><b>${this.esc(hyd.status||"—")}</b></div></section>
  </div>
 </div>
</div>`;
    this.shadowRoot.getElementById("applied")?.addEventListener("click",()=>this._hass.callService("button","press",{entity_id:this.config.applied_button||"button.i_applied_the_recommendation"}));
  }
}
customElements.define("heat-curve-fastmile-card",HeatCurveFastmileCard);
window.customCards=window.customCards||[];
window.customCards.push({type:"heat-curve-fastmile-card",name:"Heat Curve FastMile Card",description:"Nokia FastMile-inspired dashboard for Heat Curve Optimizer"});
