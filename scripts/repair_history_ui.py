from pathlib import Path

MARK = 'SJIT_HISTORY_QUERY_FINAL_V5'
JS = r'''<script id="SJIT_HISTORY_QUERY_FINAL_V5">/* SJIT_HISTORY_QUERY_FINAL_V5 */
(()=>{
  const state={rows:[],page:1,size:20,busy:false};
  const $=id=>document.getElementById(id);
  const esc=v=>String(v==null?'':v).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  const active=()=>!!$('history')?.classList.contains('active');
  function controls(){
    const h=$('history'); if(!h)return null;
    const dates=[...h.querySelectorAll('input[type=date]')];
    const text=h.querySelector('#search')||h.querySelector('input[type=text]');
    const selects=[...h.querySelectorAll('select')];
    const result=selects.find(s=>[...s.options].some(o=>/PASS|FAIL|All Result|Tất cả kết quả|Tất cả/i.test(o.textContent||'')));
    const table=h.querySelector('table.table')||h.querySelector('table');
    const apply=[...h.querySelectorAll('button')].find(b=>/조회|검색|Search|Tìm kiếm|Tra cứu/i.test((b.innerText||'').trim())&&!/Excel|CSV|초기화|Xóa|Đặt lại/i.test(b.innerText||''));
    return {h,dates,text,result,table,apply};
  }
  function hideOld(c){
    c.h.querySelectorAll('.history-pagination,.history-final-pagination,.history-final-summary,.history-final-v4,.history-final-v4-summary').forEach(n=>{if(!n.classList.contains('history-final-v5'))n.style.display='none'});
  }
  async function load(){
    const c=controls(),S=window.sb; if(!c||!S||state.busy)return;
    state.busy=true;
    try{
      const from=c.dates[0]?.value||'0000-01-01', to=c.dates[1]?.value||'9999-12-31';
      const q=await S.from('daily_inspections').select('*').order('inspection_date',{ascending:false});
      if(q.error)throw q.error;
      let rows=q.data||[];
      rows=rows.filter(r=>{const d=String(r.inspection_date||'').slice(0,10);return d>=from&&d<=to});
      const term=(c.text?.value||'').trim().toLowerCase();
      const rv=(c.result?.value||'').trim().toUpperCase();
      rows=rows.filter(r=>{
        const hay=[r.customer,r.maker,r.part_no,r.part_name,r.material_name,r.lot_no].map(v=>String(v==null?'':v).toLowerCase()).join(' ');
        const okText=!term||hay.includes(term);
        const rr=String(r.result==null?'':r.result).toUpperCase();
        const okResult=!rv||rv==='ALL'||rv==='전체'||rv==='TẤT CẢ'||rr===rv;
        return okText&&okResult;
      });
      state.rows=rows;state.page=1;render(c,from,to);
    }catch(e){
      console.error('SJIT history query',e);state.rows=[];render(c,'','');
      let err=c?.h.querySelector('.history-query-error');
      if(!err){err=document.createElement('div');err.className='history-query-error';c?.h.querySelector('.table-wrap')?.appendChild(err)}
      if(err)err.textContent='DB 조회 오류: '+(e?.message||e);
    }finally{state.busy=false}
  }
  function render(c,from,to){
    if(!c?.table)return;
    hideOld(c);
    const body=c.table.tBodies[0]||c.table.createTBody();
    const total=state.rows.length,pages=Math.max(1,Math.ceil(total/state.size));
    state.page=Math.min(state.page,pages);
    const start=(state.page-1)*state.size,end=Math.min(start+state.size,total);
    body.innerHTML=state.rows.slice(start,end).map(r=>{
      const inq=Number(r.in_qty??r.incoming_qty??r.input_qty??0),test=Number(r.test_qty??r.inspection_qty??0),bad=Number(r.bad_qty??r.defect_qty??0);
      const rate=test?(bad/test*100).toFixed(2):'0.00',res=String(r.result??'PASS').toUpperCase();
      return `<tr><td>${esc(String(r.inspection_date||'').slice(0,10))}</td><td>${esc(r.customer??r.maker)}</td><td>${esc(r.part_no)}</td><td>${esc(r.part_name??r.material_name)}</td><td>${esc(r.lot_no??'-')}</td><td>${inq.toLocaleString()}</td><td>${test.toLocaleString()}</td><td>${bad.toLocaleString()}</td><td>${rate}%</td><td><span class="badge ${res==='FAIL'?'fail':'pass'}">${res}</span></td><td>${esc(r.inspector??'-')}</td></tr>`;
    }).join('')||'<tr><td colspan="11" class="empty">검색된 검사 이력이 없습니다.</td></tr>';
    let nav=c.h.querySelector('.history-final-v5');
    if(!nav){nav=document.createElement('div');nav.className='history-final-v5';c.table.parentElement.appendChild(nav)}
    nav.innerHTML='';
    const info=document.createElement('span');info.textContent=`${total?start+1:0}-${end} / ${total}건`;
    const box=document.createElement('span');box.style.cssText='display:inline-flex;gap:5px;align-items:center;flex-wrap:wrap';
    const add=(txt,p,disabled,act)=>{const b=document.createElement('button');b.type='button';b.textContent=txt;b.disabled=!!disabled;if(act)b.className='active';b.onclick=()=>{state.page=p;render(controls(),from,to)};box.appendChild(b)};
    add('‹',Math.max(1,state.page-1),state.page===1,false);
    for(let p=1;p<=pages;p++){if(p>7&&p<pages-1){if(p===8){const d=document.createElement('span');d.textContent='…';box.appendChild(d)}continue}add(String(p),p,false,p===state.page)}
    add('›',Math.min(pages,state.page+1),state.page===pages,false);
    const size=document.createElement('label');size.innerHTML='페이지당 <select><option value="20">20</option><option value="50">50</option><option value="100">100</option></select>건';
    const sel=size.querySelector('select');sel.value=String(state.size);sel.onchange=()=>{state.size=Number(sel.value)||20;state.page=1;render(controls(),from,to)};
    nav.append(info,box,size);nav.style.cssText='display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 2px;background:#fff;border-top:1px solid #e2e8f0';
    let summary=c.h.querySelector('.history-final-v5-summary');
    if(!summary){summary=document.createElement('div');summary.className='history-final-v5-summary';(c.h.querySelector('.month-summary')||c.h.querySelector('.history-period-tools')||c.table.parentElement).insertAdjacentElement('afterend',summary)}
    const lots=new Set(state.rows.map(r=>r.lot_no||r.part_no||r.inspection_date));
    const test=state.rows.reduce((a,r)=>a+Number(r.test_qty??r.inspection_qty??0),0),bad=state.rows.reduce((a,r)=>a+Number(r.bad_qty??r.defect_qty??0),0);
    summary.innerHTML=`<div>기간<br><b>${esc(from||'전체')} ~ ${esc(to||'전체')}</b></div><div>검사 LOT 수<br><b>${lots.size} LOT</b></div><div>검사 수량<br><b>${test.toLocaleString()} PCS</b></div><div>불량 수량<br><b style="color:#dc2626">${bad.toLocaleString()} PCS</b></div>`;
  }
  function bind(){
    const c=controls();if(!c)return;hideOld(c);
    if(c.apply&&!c.apply.dataset.v5){c.apply.dataset.v5='1';c.apply.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();load()},{capture:true})}
    c.dates.forEach(x=>{if(!x.dataset.v5){x.dataset.v5='1';x.addEventListener('change',load)}});
    if(c.text&&!c.text.dataset.v5){c.text.dataset.v5='1';c.text.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();load()}})}
  }
  function tick(){if(active()){bind();if(!document.querySelector('.history-final-v5'))load()}}
  document.addEventListener('click',e=>{if(e.target.closest?.('[data-page="history"]'))setTimeout(tick,300)});
  setInterval(()=>{if(active())bind()},500);setTimeout(tick,900);
})();</script>'''

for name in ('daily-inspection/index.html','daily-inspection/vi.html'):
    p=Path(name)
    if not p.exists():
        continue
    s=p.read_text(encoding='utf-8')
    if MARK not in s:
        s=s.replace('</body></html>',JS+'</body></html>') if '</body></html>' in s else s.replace('</body>',JS+'</body>')
        p.write_text(s,encoding='utf-8')
