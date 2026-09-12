(()=>{
'use strict';
const $=id=>document.getElementById(id);
const state={rows:[],page:1,size:20,lastKey:''};
const esc=v=>String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
const date=v=>String(v||'').slice(0,10);
function get(){
 const h=$('history'); if(!h||!h.classList.contains('active')) return null;
 const dates=[...h.querySelectorAll('input[type="date"]')].slice(0,2);
 const text=$('search')||h.querySelector('input[type="text"]');
 const sel=$('filterResult')||[...h.querySelectorAll('select')].find(x=>[...x.options].some(o=>/PASS|FAIL|All Result|전체/i.test(o.textContent||'')));
 const table=h.querySelector('table.table')||h.querySelector('table');
 const buttons=[...h.querySelectorAll('button')];
 const query=buttons.find(b=>/^(조회|검색|기간 조회)$/i.test((b.textContent||'').trim()));
 return {h,dates,text,sel,table,query};
}
function setCard(h,label,value,bad=false){
 const card=[...h.querySelectorAll('.card')].find(x=>(x.textContent||'').includes(label));
 if(!card)return; const n=card.querySelector('.num'); if(n){n.textContent=value;if(bad)n.classList.add('danger-text')}
}
function setSummary(c,from,to,rows){
 setCard(c.h,'검사 LOT 수',rows.length.toLocaleString());
 setCard(c.h,'검사 수량',rows.reduce((s,r)=>s+Number(r.test_qty||0),0).toLocaleString()+' pcs');
 setCard(c.h,'불량 수량',rows.reduce((s,r)=>s+Number(r.bad_qty||0),0).toLocaleString()+' pcs',true);
 const period=[...c.h.querySelectorAll('*')].find(x=>x.children.length===0&&(x.textContent||'').trim()==='기간');
 if(period){const b=period.parentElement?.querySelector('b');if(b)b.textContent=`${from} ~ ${to}`}
}
function render(c){
 const total=state.rows.length,pages=Math.max(1,Math.ceil(total/state.size));state.page=Math.min(state.page,pages);
 const start=(state.page-1)*state.size,end=Math.min(start+state.size,total),body=c.table?.tBodies[0];if(!body)return;
 body.innerHTML=state.rows.slice(start,end).map(r=>{const test=Number(r.test_qty||0),bad=Number(r.bad_qty||0),rate=test?(bad/test*100).toFixed(2):'0.00',res=String(r.result||'PASS').toUpperCase();return `<tr><td>${esc(date(r.inspection_date))}</td><td>${esc(r.customer)}</td><td>${esc(r.part_no)}</td><td>${esc(r.part_name)}</td><td>${esc(r.lot_no)}</td><td>${Number(r.in_qty||0).toLocaleString()}</td><td>${test.toLocaleString()}</td><td>${bad.toLocaleString()}</td><td>${rate}%</td><td><span class="badge ${res==='FAIL'?'fail':'pass'}">${res}</span></td><td>${esc(r.inspector||'-')}</td></tr>`}).join('')||'<tr><td colspan="11" class="empty">검색된 검사 이력이 없습니다.</td></tr>';
 let nav=c.table.parentElement.querySelector('.history-pagination');if(!nav){nav=document.createElement('div');nav.className='history-pagination';c.table.parentElement.appendChild(nav)}
 nav.innerHTML=`${total?start+1:0}-${end} / ${total}건`;
 const pagesBox=document.createElement('span');pagesBox.style.marginLeft='12px';
 for(let p=1;p<=pages;p++){if(p>7&&p<pages-1){if(p===8)pagesBox.append(' … ');continue}const b=document.createElement('button');b.type='button';b.textContent=p;b.className=p===state.page?'active':'';b.onclick=()=>{state.page=p;render(c)};pagesBox.appendChild(b)}
 nav.appendChild(pagesBox);nav.append('  페이지당 ');
 const s=document.createElement('select');[20,50,100].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v+'건';s.appendChild(o)});s.value=state.size;s.onchange=()=>{state.size=Number(s.value);state.page=1;render(c)};nav.appendChild(s);
 setSummary(c,state.from,state.to,state.rows);
}
async function load(force=true){
 const c=get();if(!c)return;
 const from=date(c.dates[0]?.value)||'0000-01-01',to=date(c.dates[1]?.value)||'9999-12-31',term=(c.text?.value||'').trim().toLowerCase(),rf=(c.sel?.value||'').trim().toUpperCase();
 const key=from+'|'+to+'|'+term+'|'+rf;if(!force&&key===state.lastKey)return;state.lastKey=key;
 const S=window.sb||(typeof sb!=='undefined'?sb:null);if(!S)return;
 const q=await S.from('daily_inspections').select('inspection_date,customer,part_no,part_name,lot_no,in_qty,test_qty,bad_qty,result,inspector').order('inspection_date',{ascending:false});
 if(q.error){console.error(q.error);return}
 state.from=from;state.to=to;
 state.rows=(q.data||[]).filter(r=>{const d=date(r.inspection_date),hay=[r.customer,r.part_no,r.part_name,r.lot_no].join(' ').toLowerCase(),ok=String(r.result||'').toUpperCase();return d>=from&&d<=to&&(!term||hay.includes(term))&&(!rf||rf==='ALL'||rf==='전체'||ok===rf)});
 state.page=1;render(c);
}
function buttonText(b){return (b?.textContent||'').replace(/\s+/g,' ').trim()}
function intercept(){
 document.addEventListener('click',e=>{
   if(!get())return; const b=e.target.closest?.('button');if(!b)return; const t=buttonText(b);
   if(t==='조회'||t==='검색'||t==='기간 조회'){e.preventDefault();e.stopImmediatePropagation();load(true);return}
   if(t==='오늘'||t==='최근 7일'||t==='이번 달'||t==='지난 달'){
     e.preventDefault();e.stopImmediatePropagation();const c=get(),now=new Date(),end=date(now);let a=new Date(now);
     if(t==='최근 7일')a.setDate(a.getDate()-6);
     else if(t==='이번 달')a=new Date(now.getFullYear(),now.getMonth(),1);
     else if(t==='지난 달'){a=new Date(now.getFullYear(),now.getMonth()-1,1);c.dates[1].value=date(new Date(now.getFullYear(),now.getMonth(),0))}
     c.dates[0].value=date(a);if(t!=='지난 달')c.dates[1].value=end;load(true);
   }
 },true);
}
function bindInputs(){const c=get();if(!c)return;c.dates.forEach(d=>{if(!d.dataset.histV5){d.dataset.histV5=1;d.addEventListener('change',()=>load(true))}});if(c.text&&!c.text.dataset.histV5){c.text.dataset.histV5=1;c.text.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();load(true)}})}if(c.sel&&!c.sel.dataset.histV5){c.sel.dataset.histV5=1;c.sel.addEventListener('change',()=>load(true))}}
intercept();
setInterval(()=>{bindInputs();if(get()&&!state.lastKey)load(true)},800);
document.addEventListener('click',e=>{if(e.target.closest?.('[data-page="history"]'))setTimeout(()=>{state.lastKey='';load(true)},250)},true);
setTimeout(()=>{state.lastKey='';load(true)},700);
})();