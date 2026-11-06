/* Automatic, control-free report. The optional explorer remains below it. */
(() => {
'use strict';
const NS='http://www.w3.org/2000/svg',purple='#4a3aa7',red='#b03a32',muted='#65625c';
const palette=['#4a3aa7','#bb5816','#167954','#a33768','#267c9c','#716b18','#795548','#5f6f87','#853c9a','#24704a','#b03a32','#427bb0','#8a6626'];
const el=id=>document.getElementById(id),pct=v=>`${(100*v).toFixed(1)}%`,pp=v=>`${(100*v).toFixed(1)} percentage points`;
const eventLabel=m=>({safety:'Unsafe outcome',recall:'Missed attack',blocked_episode:'Episode not prevented'})[m]||m;
const raw=o=>o.reported_value??o.value;
const sigmoid=x=>x>=0?1/(1+Math.exp(-x)):Math.exp(x)/(1+Math.exp(x));
const quant=(v,p)=>{const a=v.slice().sort((a,b)=>a-b),i=(a.length-1)*p,j=Math.floor(i);return a[j]+(a[Math.min(j+1,a.length-1)]-a[j])*(i-j);};
const interval=a=>[.05,.5,.95].map(p=>quant(a,p));
function svg(tag,attrs,parent,text){const n=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs||{}))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;parent.appendChild(n);return n;}
function group(root,text,id){const g=svg('g',{tabindex:0,role:'img','aria-label':text,...(id?{'data-observation':id}:{})},root);svg('title',{},g,text);return g;}
function chart(id,title){el(id).replaceChildren();const root=svg('svg',{viewBox:'0 0 760 365',role:'img','aria-label':title},el(id));svg('title',{},root,title);return root;}
function axes(root,x,y,xt,yt,xlabel,ylabel){for(const[v,t]of xt){svg('line',{x1:x(v),x2:x(v),y1:30,y2:285,stroke:'#eceae5'},root);svg('text',{x:x(v),y:305,'text-anchor':'middle',fill:muted,'font-size':11},root,t);}for(const[v,t]of yt){svg('line',{x1:75,x2:725,y1:y(v),y2:y(v),stroke:'#eceae5'},root);svg('text',{x:64,y:y(v)+4,'text-anchor':'end',fill:muted,'font-size':11},root,t);}svg('text',{x:400,y:345,'text-anchor':'middle',fill:muted},root,xlabel);svg('text',{x:18,y:160,transform:'rotate(-90 18 160)','text-anchor':'middle',fill:muted},root,ylabel);}
function mark(root,metric,x,y,color,r=4){if(metric==='recall')svg('rect',{x:x-r,y:y-r,width:2*r,height:2*r,fill:color,'fill-opacity':.7},root);else if(metric==='blocked_episode')svg('path',{d:`M${x},${y-r-1} L${x+r+1},${y+r} L${x-r-1},${y+r} Z`,fill:color,'fill-opacity':.7},root);else svg('circle',{cx:x,cy:y,r,fill:color,'fill-opacity':.7},root);}
const ticks=[0,.25,.5,.75,1].map(v=>[v,pct(v)]);
const path=points=>points.map(([x,y],i)=>`${i?'L':'M'}${x},${y}`).join(' ');
document.addEventListener('DOMContentLoaded',()=>{
const D=window.AI_CONTROL_SIMPLE,m=D?.models?.unified;if(!m||!el('report-collapse-chart'))return;
const observations=new Map(D.observations.map(o=>[o.id,o])),protocols=new Map(m.protocols.map(p=>[p.id,p])),sources=new Map(D.sources.map((s,i)=>[s.id,{...s,color:palette[i%palette.length]}]));
function collapsedFit(){
 const rows=m.observation_ids.map(id=>observations.get(id)).map(o=>{
  const p=protocols.get(o.protocol);
  return {o,p,z:o.ln_attacker-o.ln_monitor-p.alpha/m.slope};
 });
 const low=Math.floor(Math.min(...rows.map(r=>r.z))/Math.LN10)*Math.LN10;
 const high=Math.ceil(Math.max(...rows.map(r=>r.z))/Math.LN10)*Math.LN10;
 const x=z=>75+(z-low)/(high-low)*650,y=f=>285-f*255;
 const root=chart('report-collapse-chart','All model-eligible observations after factoring out fitted protocol strength');
 const xticks=[];
 for(let power=Math.round(low/Math.LN10);power<=Math.round(high/Math.LN10);power++){
  const value=10**power;
  xticks.push([power*Math.LN10,value<1?value.toFixed(-power):value.toLocaleString('en')]);
 }
 axes(root,x,y,xticks,ticks,'Normalized capability ratio x = R / R50,p (log scale)','Reported failure proxy');
 const curve=Array.from({length:141},(_,j)=>{
  const z=low+(high-low)*j/140;
  const range=interval(m.slope_draws.map(k=>sigmoid(k*z)));
  return {x:x(z),low:y(range[0]),high:y(range[2]),mean:y(sigmoid(m.slope*z))};
 });
 svg('path',{d:path(curve.map(p=>[p.x,p.low]))+' '+curve.slice().reverse().map(p=>`L${p.x},${p.high}`).join(' ')+' Z',fill:purple,opacity:.12},root);
 svg('path',{d:path(curve.map(p=>[p.x,p.mean])),fill:'none',stroke:purple,'stroke-width':3},root);
 for(const {o,p,z} of rows){
  const xx=x(z),color=sources.get(o.study).color;
  const point=o.value!==undefined;
  const description=point?`reported failure ${pct(1-raw(o))}`:o.lower!==undefined&&o.upper!==undefined?`failure interval ${pct(1-o.upper)}–${pct(1-o.lower)}`:o.upper!==undefined?`failure at least ${pct(1-o.upper)}`:`failure at most ${pct(1-o.lower)}`;
  const g=group(root,`${sources.get(o.study).title}; ${p.label}; ${eventLabel(o.metric)}; ${o.attacker} → ${o.monitor}; normalized ratio ${Number(Math.exp(z).toPrecision(4))}; ${description}; fitted failure ${pct(sigmoid(m.slope*z))}. ${o.condition||o.source_location||''}`,o.id);
  g.setAttribute('data-protocol',p.id);g.setAttribute('data-outcome',o.metric);
  g.setAttribute('data-normalized-log-ratio',z);
  g.setAttribute('data-kind',point?'point':o.lower!==undefined&&o.upper!==undefined?'interval':o.upper!==undefined?'lower-bound':'upper-bound');
  if(point){mark(g,o.metric,xx,y(1-raw(o)),color,3.3);}
  else if(o.lower!==undefined&&o.upper!==undefined){
   const top=y(1-o.lower),bottom=y(1-o.upper);
   svg('line',{x1:xx,x2:xx,y1:top,y2:bottom,stroke:color,'stroke-width':1.5,'stroke-opacity':.65},g);
   for(const yy of [top,bottom])svg('line',{x1:xx-3,x2:xx+3,y1:yy,y2:yy,stroke:color,'stroke-opacity':.65},g);
  }else{
   const f=1-(o.upper??o.lower),yy=y(f),direction=o.upper!==undefined?-1:1;
   svg('path',{d:`M${xx},${yy+direction*8} L${xx-4},${yy} L${xx+4},${yy} Z`,fill:color,'fill-opacity':.75},g);
  }
 }
 const points=rows.filter(r=>r.o.value!==undefined).length;
 el('report-collapse-summary').textContent=`All ${rows.length} model-eligible observations from ${m.protocols.length} protocols and ${m.study_count} studies: ${points} point outcomes and ${rows.length-points} bounds or extraction intervals. One shared curve, k = ${Number(m.slope.toPrecision(3))}. ${D.observations.length-rows.length} other archive records cannot be normalized under this fit, including unplaced capabilities, human attacks and baselines without trusted review.`;
 const legend=el('report-collapse-legend');legend.replaceChildren();
 for(const [metric,shape]of [['safety','●'],['recall','■'],['blocked_episode','▲']]){const span=document.createElement('span');span.textContent=`${shape} ${eventLabel(metric)}`;legend.appendChild(span);}
 for(const source of sources.values())if(rows.some(r=>r.o.study===source.id)){
  const span=document.createElement('span'),dot=document.createElement('i');
  dot.style.cssText=`display:inline-block;width:10px;height:10px;border-radius:50%;background:${source.color}`;
  span.append(dot,document.createTextNode(source.title));legend.appendChild(span);
 }
}
collapsedFit();

function horizonLabel(logHours){
 const hours=Math.exp(logHours);
 if(hours<1/3600)return `${Number((hours*3600000).toPrecision(2))} ms`;
 if(hours<1/60)return `${Number((hours*3600).toPrecision(2))} sec`;
 if(hours<1)return `${Number((hours*60).toPrecision(2))} min`;
 if(hours<10000)return `${Number(hours.toPrecision(3)).toLocaleString('en')} h`;
 return `${hours.toExponential(1)} h`;
}
function drawTimeline(){
 const monitor=Number(el('timeline-monitor').value),ceiling=Number(el('timeline-failure').value);
 if(!el('timeline-monitor').validity.valid||!Number.isFinite(monitor))return;
 const adjustment=Math.log(ceiling/(1-ceiling)),logMonitor=Math.log(monitor);
 const ps=m.protocols,dates=[...new Set(ps.map(p=>p.date))].sort();
 const frontier=D.frontier||[],lastEvidence=Date.parse(dates.at(-1));
 const firstDate=Math.min(Date.parse(dates[0]),...frontier.map(p=>Date.parse(p.date)));
 const carryEnd=Math.max(lastEvidence,...frontier.map(p=>Date.parse(p.date)));
 const start=firstDate-35*86400000,end=carryEnd+35*86400000;
 const values=new Map(ps.map(p=>[p.id,p.alpha_draws.map((a,i)=>logMonitor+(a+adjustment)/m.slope_draws[i])]));
 const ranges=new Map(ps.map(p=>[p.id,interval(values.get(p.id))]));
 const best=new Array(m.slope_draws.length).fill(-Infinity),envelope=[];
 for(const date of dates){
  for(const p of ps.filter(p=>p.date===date)){const a=values.get(p.id);for(let i=0;i<best.length;i++)best[i]=Math.max(best[i],a[i]);}
  envelope.push({date,range:interval(best)});
 }
 const logs=ps.flatMap(p=>ranges.get(p.id)).concat(frontier.flatMap(p=>[Math.log(p.lo/60),Math.log(p.hi/60)]));
 const lower=Math.floor(Math.min(...logs)/Math.LN10)*Math.LN10,upper=Math.ceil(Math.max(...logs)/Math.LN10)*Math.LN10;
 const x=t=>90+(t-start)/(end-start)*980,y=v=>425-(v-lower)/(upper-lower)*395;
 el('report-timeline-chart').replaceChildren();
 const root=svg('svg',{viewBox:'0 0 1100 500',role:'img','aria-label':`Controllable attacker task horizon over time with a fixed ${monitor}-hour trusted model at ${pct(ceiling)} reported failure`},el('report-timeline-chart'));
 svg('title',{},root,'Simple-model controllable attacker capability versus frontier capability');
 for(let i=0;i<7;i++){
  const t=start+(end-start)*i/6;
  svg('line',{x1:x(t),x2:x(t),y1:30,y2:425,stroke:'#eceae5'},root);
  svg('text',{x:x(t),y:450,'text-anchor':'middle',fill:muted,'font-size':12},root,new Date(t).toLocaleDateString('en-GB',{month:'short',year:'numeric',timeZone:'UTC'}));
 }
 const tickStep=Math.max(1,Math.ceil((upper-lower)/Math.LN10/8));
 for(let power=Math.round(lower/Math.LN10);power<=Math.round(upper/Math.LN10);power+=tickStep){
  const v=power*Math.LN10;
  svg('line',{x1:90,x2:1070,y1:y(v),y2:y(v),stroke:'#eceae5'},root);
  svg('text',{x:80,y:y(v)+4,'text-anchor':'end',fill:muted,'font-size':12},root,horizonLabel(v));
 }
 svg('text',{x:580,y:485,'text-anchor':'middle',fill:muted},root,'Date');
 svg('text',{x:20,y:230,transform:'rotate(-90 20 230)','text-anchor':'middle',fill:muted},root,'Attacker task horizon at selected failure ceiling (log scale)');
 const steps=[];
 envelope.forEach((point,i)=>{const xx=x(Date.parse(point.date));if(i)steps.push({...envelope[i-1],x:xx});steps.push({...point,x:xx});});
 if(carryEnd>lastEvidence)steps.push({...envelope.at(-1),x:x(carryEnd)});
 svg('path',{d:path(steps.map(p=>[p.x,y(p.range[0])]))+' '+steps.slice().reverse().map(p=>`L${p.x},${y(p.range[2])}`).join(' ')+' Z',fill:purple,opacity:.12},root);
 const solid=steps.filter(p=>p.x<=x(lastEvidence));
 svg('path',{d:path(solid.map(p=>[p.x,y(p.range[1])])),fill:'none',stroke:purple,'stroke-width':3,'data-control-envelope':'true'},root);
 if(carryEnd>lastEvidence)svg('path',{d:`M${x(lastEvidence)},${y(envelope.at(-1).range[1])} L${x(carryEnd)},${y(envelope.at(-1).range[1])}`,fill:'none',stroke:purple,'stroke-width':3,'stroke-dasharray':'6 4',opacity:.5},root);
 for(const point of envelope){
  const label=`${point.date}: best available controllable attacker ${horizonLabel(point.range[1])}, 90% interval ${horizonLabel(point.range[0])} to ${horizonLabel(point.range[2])}; fixed trusted model ${monitor} hours; reported failure ceiling ${pct(ceiling)}.`;
  const g=group(root,label);g.setAttribute('data-control-date',point.date);g.setAttribute('data-control-log-hours',point.range[1]);
  svg('circle',{cx:x(Date.parse(point.date)),cy:y(point.range[1]),r:4,fill:purple},g);
 }
 for(const p of ps){
  const range=ranges.get(p.id),o=observations.get(p.observation_ids[0]),xx=x(Date.parse(p.date));
  const g=group(root,`${p.label}; ${sources.get(p.study).title}; ${eventLabel(o.metric)}; implied controllable attacker ${horizonLabel(range[1])}; 90% interval ${horizonLabel(range[0])} to ${horizonLabel(range[2])}.`);
  g.setAttribute('class','timeline-protocol');g.setAttribute('data-protocol',p.id);
  svg('line',{x1:xx,x2:xx,y1:y(range[0]),y2:y(range[2]),stroke:'#777','stroke-width':1,'class':'timeline-range'},g);
  mark(g,o.metric,xx,y(range[1]),'#76736f',3.5);
 }
 for(const p of frontier){
  const xx=x(Date.parse(p.date)),mid=Math.log(p.p50/60),label=`${p.name}, ${p.date}: task horizon ${horizonLabel(mid)}; ${p.estimated?'estimated capability range':'METR 95% interval'} ${horizonLabel(Math.log(p.lo/60))} to ${horizonLabel(Math.log(p.hi/60))}.`;
  const g=group(root,label);g.setAttribute('class','timeline-frontier');g.setAttribute('data-frontier',p.name);
  svg('line',{x1:xx,x2:xx,y1:y(Math.log(p.lo/60)),y2:y(Math.log(p.hi/60)),stroke:'#2a78d6','stroke-width':1.5,'class':'timeline-range'},g);
  svg('circle',{cx:xx,cy:y(mid),r:5,fill:p.estimated?'#fcfcfb':'#2a78d6',stroke:p.estimated?'#2a78d6':'#fcfcfb','stroke-width':2},g);
 }
 const latest=envelope.at(-1).range;
 el('report-timeline-summary').textContent=`At the latest evaluation (${dates.at(-1)}), the best-available modeled attacker horizon is ${horizonLabel(latest[1])} (90% interval ${horizonLabel(latest[0])}–${horizonLabel(latest[2])}), using a trusted model fixed at ${monitor} hours and a ${pct(ceiling)} reported failure ceiling. The timeline uses all ${ps.length} fitted protocols and the same posterior as the normalized scatterplot.`;
}
el('timeline-monitor').addEventListener('input',drawTimeline);
el('timeline-failure').addEventListener('change',drawTimeline);
drawTimeline();
el('report-model-diagnostics').textContent=`The model uses four chains with 5,000 retained and 2,500 warmup draws each. Maximum split R-hat ${m.max_rhat.toFixed(3)}, minimum effective sample size ${Math.round(m.min_ess)}. Numerical convergence does not validate the outcome unification or cross-benchmark normalization.`;
});
})();
