class UtilityCostCard extends HTMLElement {
  setConfig(config){this.config=config||{};this.period=this.period||"bill";if(!this.shadowRoot)this.attachShadow({mode:"open"});}
  set hass(h){this._h=h;this.render();}
  getCardSize(){return 8;}
  static getStubConfig(){return {};}
  findRole(period,role){return Object.values(this._h?.states||{}).find(x=>x.attributes?.period===period&&x.attributes?.utility_cost_role===role);}
  money(x){const n=Number(x?.state);return Number.isFinite(n)?new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD'}).format(n):'—';}
  kwh(n){n=Number(n);return Number.isFinite(n)?`${n.toFixed(n<10?2:1)} kWh`:'—';}
  render(){
    if(!this._h)return;
    const p=this.period, net=this.findRole(p,'net'), grid=this.findRole(p,'grid'), supply=this.findRole(p,'supply'), fit=this.findRole(p,'fit');
    const devices=Object.values(this._h.states).filter(x=>x.attributes?.source_entity&&x.attributes?.period===p).sort((a,b)=>Number(b.state)-Number(a.state));
    const since=net?.attributes?.data_since||devices[0]?.attributes?.data_since;
    const sinceText=since?new Date(since).toLocaleString('en-AU',{dateStyle:'medium',timeStyle:'short'}):'';
    this.shadowRoot.innerHTML=`<style>:host{display:block}.c{background:var(--ha-card-background,var(--card-background-color));border-radius:var(--ha-card-border-radius,12px);padding:20px;box-shadow:var(--ha-card-box-shadow)}.top{display:flex;justify-content:space-between;align-items:center}.tabs{display:flex;gap:6px;margin:16px 0;flex-wrap:wrap}.tab{padding:7px 10px;border-radius:18px;cursor:pointer;background:var(--secondary-background-color)}.tab.on{background:var(--primary-color);color:var(--text-primary-color)}.big{font-size:34px;font-weight:600}.muted{color:var(--secondary-text-color)}.row{display:grid;grid-template-columns:1fr auto auto;gap:16px;padding:9px 0;border-bottom:1px solid var(--divider-color);align-items:center}.cost{font-weight:600;text-align:right}.energy{color:var(--secondary-text-color);text-align:right;min-width:76px}h3{margin:18px 0 5px}.notice{margin-top:16px;padding:10px;border-radius:8px;background:var(--secondary-background-color);font-size:12px}</style><ha-card><div class="c"><div class="top"><div><b>Utility Cost</b><div class="muted">${net?.attributes?.plan||''}</div></div><ha-icon icon="mdi:cash-multiple"></ha-icon></div><div class="tabs">${['today','month','bill','year'].map(x=>`<span class="tab ${x===p?'on':''}" data-p="${x}">${x==='bill'?'Bill cycle':x[0].toUpperCase()+x.slice(1)}</span>`).join('')}</div><div class="muted">Estimated net cost</div><div class="big">${this.money(net)}</div><div class="muted">${net?.attributes?.period_key||''}</div><h3>Bill breakdown</h3><div class="row"><span>Grid import</span><span></span><span class="cost">${this.money(grid)}</span></div><div class="row"><span>Supply charge</span><span></span><span class="cost">${this.money(supply)}</span></div><div class="row"><span>Solar credit</span><span></span><span class="cost">−${this.money(fit)}</span></div><h3>Tracked devices</h3>${devices.length?devices.map(d=>`<div class="row"><span>${d.attributes.display_name||d.attributes.source_entity}</span><span class="energy">${this.kwh(d.attributes.energy_kwh)}</span><span class="cost">${this.money(d)}</span></div>`).join(''):'<div class="muted">No tracked devices configured.</div>'}${sinceText?`<div class="notice">Cost history is accumulated by Utility Cost from ${sinceText}. Earlier Home Assistant history is not back-filled.</div>`:''}<p class="muted">Change entities, rates and bill-cycle date in Settings → Devices & services → Utility Cost → Configure.</p></div></ha-card>`;
    this.shadowRoot.querySelectorAll('.tab').forEach(e=>e.onclick=()=>{this.period=e.dataset.p;this.render();});
  }
}
if(!customElements.get('utility-cost-card')) customElements.define('utility-cost-card',UtilityCostCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==='utility-cost-card')) window.customCards.push({type:'utility-cost-card',name:'Utility Cost',description:'Electricity bill and device cost dashboard'});
