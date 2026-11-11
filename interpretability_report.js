(function () {
  'use strict';
  const data = window.INTERPRETABILITY_DATA;
  const model = window.InterpretabilityModel;
  const byId = Object.fromEntries(data.sources.map(s => [s.id, s]));
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pct = (v, digits=1) => `${(100*v).toLocaleString('en-US',{maximumFractionDigits:digits})}%`;
  const precisePct = v => v > 0 && v < 0.000001 ? `${(v*100).toExponential(2)}%` : pct(v,5);
  const colors = {purple:'#4a3aa7',blue:'#2876b9',amber:'#9b6505',red:'#b12c2c',gray:'#777'};
  const color = row => row.method === 'Activation oracle' ? colors.amber : /Self-report|Text monitor/.test(row.method) ? colors.blue : colors.purple;
  const link = row => `${byId[row.source].url}${row.source === 'fibs2026' ? '#A5.T12' : ''}`;
  const svgStart = (w,h,title) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(title)}"><title>${esc(title)}</title>`;
  const txt = (x,y,text,opts='') => `<text x="${x}" y="${y}" ${opts}>${esc(text)}</text>`;
  const line = (x1,y1,x2,y2,stroke='#ddd',opts='') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" ${opts}/>`;

  function renderEvidence() {
    const family = $('evidence-family').value;
    const rows = data.observations.filter(r => family === 'auroc' ? r.metric === 'auroc' : r.metric === 'recall' && (family === 'hidden-goal' ? r.scope === 'hidden-goal' : r.scope !== 'hidden-goal'));
    const notes = {
      operational:'Nominal 1% FPR, different negative distributions: Alpaca dialogue, low-stakes interactions, or ordinary tool steps. These rows are examples, not a shared leaderboard. Detection is not prevention.',
      'hidden-goal':'All eight conditions, one study and one 27B base-model family. Nominal 2% FPR; realised 0.7–1.8%. Count-derived recall on selected hidden-goal denials. This is a readout stress test, not an agentic-action benchmark.',
      auroc:'AUROC measures ranking, not the fraction caught at a deployment threshold. The sleeper-agent observation is a strict lower bound (>99%), not an exact score.'
    };
    $('evidence-note').textContent = notes[family];
    const W=1040, left=360, right=70, top=42, rowH=family==='hidden-goal'?31:60;
    const H=top+rows.length*rowH+50, plot=W-left-right, x=v=>left+v*plot;
    let svg=svgStart(W,H,family==='auroc'?'Reported AUROC by experiment':'Reported recall by experiment');
    for(let t=0;t<=1.001;t+=.2){svg+=line(x(t),top-15,x(t),H-35);svg+=txt(x(t),H-14,pct(t,0),'text-anchor="middle" fill="#65625c"');}
    svg+=txt(left,20,family==='auroc'?'AUROC (higher is better)':'Recall (higher is better)');
    rows.forEach((r,i)=>{
      const y=top+i*rowH;
      let label=family==='hidden-goal'?`${r.task} · ${r.method}`:`${r.task} · ${r.method}`;
      const value=(r.precision==='strict lower bound'?'>':['count-derived','reported'].includes(r.precision)?'':'≈')+pct(r.value,1);
      const title=`${r.task}: ${r.method}, ${value}; ${r.model}; ${r.date}; ${r.locator}`;
      svg+=`<a href="${esc(link(r))}" tabindex="0" aria-label="${esc(title)}"><title>${esc(title)}</title>`;
      svg+=txt(left-12,y+14,label,'text-anchor="end" font-size="11"');
      if(family!=='hidden-goal')svg+=txt(left-12,y+32,`${r.date} · ${r.scope==='sabotage'?'model unspecified':r.model_parameters_b ? r.model_parameters_b+'B target' : 'text baseline'}`,'text-anchor="end" font-size="10" fill="#777"');
      svg+=`<rect x="${left}" y="${y}" width="${Math.max(1,r.value*plot)}" height="19" fill="${color(r)}" rx="2"/>`;
      svg+=txt(x(r.value)+7,y+14,value,'font-size="11"');
      svg+='</a>';
    });
    $('evidence-chart').innerHTML=svg+'</svg>';
    $('evidence-table').innerHTML='<table><caption>Source-level observations for the selected family</caption><thead><tr><th>Task / method</th><th>Result</th><th>Model / unit</th><th>Threshold reference</th><th>Verify</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${esc(r.task)}<small>${esc(r.method)}</small></td><td>${r.precision==='strict lower bound'?'&gt;':['count-derived','reported'].includes(r.precision)?'':'≈'}${pct(r.value,2)}${r.caught!==null?`<small>${r.caught} / ${r.n_positive}</small>`:''}</td><td>${esc(r.model)}<small>Per ${esc(r.unit)}</small></td><td>${r.fpr ? pct(r.fpr)+' FPR; '+esc(r.negative_reference):'AUROC; no fixed threshold'}</td><td><a href="${esc(link(r))}">${esc(r.locator)}</a><small>${r.date} · ${esc(r.date_basis)}</small></td></tr>`).join('')+'</tbody></table>';
  }

  function renderHistory() {
    const W=1040,H=385,left=300,right=60,top=55,rowH=28,x=y=>left+(y-2019)/(2026-2019)*(W-left-right);
    let svg=svgStart(W,H,'Selected evidence from 2019 to 2026; no annual performance trend');
    for(let y=2019;y<=2026;y++){svg+=line(x(y),35,x(y),H-15);svg+=txt(x(y),20,y,'text-anchor="middle"');}
    data.history.forEach((r,i)=>{
      const y=top+i*rowH,c=r.type==='stress'?colors.red:r.type==='context'?colors.gray:colors.purple;
      svg+=txt(left-14,y+4,r.label,'text-anchor="end"');
      svg+=`<a href="${esc(byId[r.source].url)}" tabindex="0" aria-label="${esc(r.year+' '+r.label+': '+r.detail)}"><title>${esc(r.detail)}</title><circle cx="${x(r.year)}" cy="${y}" r="6" fill="${c}"/></a>`;
    });
    $('history-chart').innerHTML=svg+'</svg>';
    $('history-list').innerHTML=data.history.map(r=>`<div class="history-entry"><b>${r.year} · <a href="${esc(byId[r.source].url)}">${esc(r.label)}</a></b><p>${esc(r.detail)}</p></div>`).join('');
  }

  const anchors=data.observations.filter(r=>r.metric==='recall' && (['shade-recall','apollo-recall','stakes-probe','stakes-baseline'].includes(r.id) || r.method==='Axial probe'));
  anchors.sort((a,b)=>a.id==='shade-recall'?-1:b.id==='shade-recall'?1:0);
  $('anchor').innerHTML=anchors.map(r=>`<option value="${r.id}">${esc(r.task)} · ${pct(r.value,1)} recall · ${pct(r.fpr,0)} FPR · ${esc(r.method)}</option>`).join('');
  function inputs() {
    const fields=['target','transfer','persistent','max-checks','budget','checkpoint-cost','review-cost','setup-cost','volume'];
    const v={};
    for(const id of fields){v[id]=Number($(id).value);if($(id).value==='' || !Number.isFinite(v[id]) || !$(id).checkValidity())return null;}
    return {r:anchors.find(r=>r.id===$('anchor').value),t:v.transfer/100,z:v.persistent/100,max:v['max-checks'],target:v.target,budget:v.budget/100,c:v['checkpoint-cost']/100,h:v['review-cost'],A:v['setup-cost'],N:v.volume};
  }
  function renderScenario() {
    $('transfer-value').textContent=$('transfer').value+'%';
    $('persistent-value').textContent=$('persistent').value+'%';
    const p=inputs();
    if(!p){$('scenario-status').textContent='Enter valid values in every cost and checkpoint field to calculate the scenario.';$('scenario-chart').innerHTML='';$('scenario-table').innerHTML='';return;}
    const {r,t,z,max,target,budget,c,h,A,N}=p, m=1-r.value*t, floor=m*z;
    const E=(k,persistence=z)=>model.residual(r.value,t,persistence,k);
    const C=k=>model.cost(k,c,r.fpr,h,A,N);
    const k=model.required(r.value,t,z,target,max);
    const fit=k!==null && C(k)<=budget;
    const floorBlocks=floor>=target && E(max)>target;
    const explanation = k===null ? (floorBlocks?`The persistent floor (${precisePct(floor)}) prevents reaching the target.`:`The target is not reached within ${max} available checkpoints.`) : `${k} effective checkpoints reach ${precisePct(E(k))} escaped, costing ${pct(C(k),3)} of one reference pass. ${fit?'Within':'Above'} the selected ${pct(budget,2)} budget.`;
    $('scenario-status').className='status'+(fit?'':' failure');
    $('scenario-status').innerHTML=`<b>${fit?'Passes the chosen scenario screen.':'Does not pass the chosen scenario screen.'}</b> ${esc(explanation)} <span class="muted">This is conditional arithmetic, not validated prevention.</span>`;
    $('anchor-note').innerHTML=`Anchor: <a href="${esc(link(r))}">${esc(r.locator)}</a>. ${esc(r.note)} Nominal FPR: ${pct(r.fpr)} on ${esc(r.negative_reference)}. Scored unit: ${esc(r.unit)}. No ROC curve is assumed between thresholds.`;
    const W=1040,H=385,left=85,right=25,top=30,bottom=62;
    const maxCost=Math.max(C(max),budget*1.08,1e-8),x=v=>left+v/maxCost*(W-left-right),y=v=>top+(0-Math.log10(Math.max(v,1e-6)))/6*(H-top-bottom);
    let svg=svgStart(W,H,'Conditional escaped fraction versus normalized monitoring cost');
    for(let j=0;j<=6;j++){const v=10**(-j);svg+=line(left,y(v),W-right,y(v));svg+=txt(left-10,y(v)+4,precisePct(v),'text-anchor="end"');}
    for(let j=0;j<=5;j++){const v=maxCost*j/5;svg+=line(x(v),top,x(v),H-bottom);svg+=txt(x(v),H-bottom+22,pct(v,2),'text-anchor="middle"');}
    svg+=txt(left,15,'Escaped fraction · log scale');
    svg+=txt((left+W-right)/2,H-8,'Monitoring cost as % of one reference text-monitor pass','text-anchor="middle"');
    svg+=line(x(budget),top,x(budget),H-bottom,'#888','stroke-width="2"');
    svg+=txt(Math.min(x(budget)+5,W-90),top+15,'Budget','fill="#666"');
    svg+=line(left,y(target),W-right,y(target),colors.red,'stroke-dasharray="5 4"');
    for(const [persist,stroke,dash] of [[0,colors.blue,'stroke-dasharray="6 4"'],[z,colors.purple,'']]){
      const points=Array.from({length:max},(_,i)=>`${x(C(i+1))},${y(E(i+1,persist))}`).join(' ');
      svg+=`<polyline points="${points}" fill="none" stroke="${stroke}" stroke-width="2.5" ${dash}/>`;
    }
    for(let j=1;j<=max;j++){
      if(max>30 && j%5!==0 && j!==1 && j!==k)continue;
      svg+=`<circle cx="${x(C(j))}" cy="${y(E(j))}" r="${j===k?5:2.5}" fill="${colors.purple}"><title>${j} checks; ${precisePct(E(j))} escaped; ${pct(C(j),3)} reference cost</title></circle>`;
    }
    svg+=txt(left,H-bottom+42,'Values below 0.0001% are drawn at the chart floor.','font-size="10" fill="#777"');
    $('scenario-chart').innerHTML=svg+'</svg>';
    $('scenario-table').innerHTML='<table><caption>Cost to reach each coverage target under these assumptions</caption><thead><tr><th>Coverage</th><th>Effective checkpoints</th><th>Normalized cost</th><th>Within selected budget?</th></tr></thead><tbody>'+[.01,.001,.0001].map(e=>{
      const n=model.required(r.value,t,z,e,max);
      return `<tr><td>${pct(1-e,2)}</td><td>${n===null?'Not reached':n}</td><td>${n===null?'—':pct(C(n),3)}</td><td>${n===null?'Not reached':C(n)<=budget?'Yes, in scenario':'No'}</td></tr>`;
    }).join('')+'</tbody></table>';
  }

  function renderSources() {
    $('archive-summary').textContent=`${data.observations.length} numerical observations; ${data.sources.length} primary sources reviewed; ${data.history.length} historical/context entries. This is a curated review, not an exhaustive survey.`;
    $('source-list').innerHTML=data.sources.map(s=>`<li id="source-${s.id}"><a href="${esc(s.url)}">${esc(s.title)}</a>${s.code?` · <a href="${esc(s.code)}">Code</a>`:''}<small>${esc(s.locator)}</small>${esc(s.summary)}</li>`).join('');
    const c=data.cost,S=c.sequence_length,ratio=c.probe_coefficient*S/(c.reference_linear_coefficient*S+c.reference_quadratic_coefficient*S*S);
    $('cost-example').textContent=`At S = ${S.toLocaleString()} tokens, those formulas imply a head-only ratio of ${ratio.toExponential(2)}: approximately ${(1/ratio).toLocaleString('en-US',{maximumFractionDigits:0})}× less arithmetic than a separate 8B reference pass. The actor remains 70B. This illustrates why actor size alone need not make internal checks unaffordable.`;
  }
  $('evidence-family').addEventListener('change',renderEvidence);
  for(const id of ['anchor','target','transfer','persistent','max-checks','budget','checkpoint-cost','review-cost','setup-cost','volume'])$(id).addEventListener('input',renderScenario);
  $('optimistic').addEventListener('click',()=>{
    const defaults={anchor:'shade-recall',target:'.001',transfer:100,persistent:0,'max-checks':20,budget:10,'checkpoint-cost':.1,'review-cost':1,'setup-cost':0,volume:1000000};
    for(const [id,v] of Object.entries(defaults))$(id).value=id==='target'?'0.001':v;
    renderScenario();
  });
  $('small-blindspot').addEventListener('click',()=>{$('persistent').value=1;renderScenario();});
  $('one-chance').addEventListener('click',()=>{$('max-checks').value=1;renderScenario();});
  renderEvidence();renderHistory();renderSources();renderScenario();
})();
