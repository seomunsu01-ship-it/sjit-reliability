/* SJIT_HISTORY_FIX_V4
   Single source of truth for inspection-history filters, summary, table and pagination.
*/
(()=>{
  'use strict';
  const state={rows:[],page:1,size:20,lastKey:null,bound:false};
  const esc=v=>String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  const $=id=>document.getElementById(id);
  function history(){return $('history')}
  function controls(){
    const h=history(); if(!h) return null;
    const dates=[...h.querySelectorAll('input[type="date"]')];
    const text=h.querySelector('#search')||h.querySelector('input[type="text"]');
    const selects=[...h.querySelectorAll('select')];
    const result=selects.find(s=>[...s.options].some(o=>/PASS|FAIL|All Result|전체|Tất cả/i.test(o.textContent||'')));
    const table=h.querySelector('table.table')||h.querySelector('table');
    const buttons=[...h.querySelectorAll('button')];
    const queryBtn=buttons.find(b=>/^(조회|검색|기간 조회|Tra cứu|Search)$/i.test((b.innerText||'').trim()));
    return {h,dates,text,result,table,queryBtn};
  }
  function normDate(v){return String(v||'').slice(0,10)}
  function value(r,k){return r?.[k]??''}
  function match(rows,c){
    const term=(c.text?.value||'').trim().toLowerCase();
    const rf=(c.result?.value||'').trim().toUpperCase();
    return rows.filter(r=>{
      const hay=[value(r,'customer'),value(r,'part_no'),value(r,'part_name'),value(r,'lot_no')].join(' ').toLowerCase();
      return (!term||hay.includes(term)) && (!rf||rf==='ALL'||rf==='전체'||rf==='TẤT CẢ'||rf==='TAT CA'||String(value(r,'result')).toUpperCase()===rf);
    });
  }
  async function fetchRows(c){
    const S=window.sb;
    if(!S) throw new Error('Supabase client window.sb not found');
    const from=normDate(c.dates[0]?.value)||'0000-01-01';
    const to=normDate(c.dates[1]?.value)||'9999-12-31';
    const q=await S.from('daily_inspections')
      .select('inspection_date,customer,part_no,part_name,lot_no,in_qty,test_qty,bad_qty,result,inspector')
      .order('inspection_date',{ascending:false});
    if(q.error) throw q.error;
    const raw=q.data||[];
    const period=raw.filter(r=>{const d=normDate(r.inspection_date);return d>=from&&d<=to});
    return {from,to,rows:match(period,c)};
  }
  function setSummary(c,totalRows){
    const box=c.h.querySelector('.history-period-summary');
    if(!box)return;
    const vals=[...box.querySelectorAll('.hstat-value')];
    // One daily_inspections row represents one inspection LOT. Keep this
    // consistent with the dashboard's inspection LOT count; do not collapse
    // rows by lot_no because duplicate/blank LOT labels are still inspections.
    const lots=totalRows.length;
    const test=totalRows.reduce((s,r)=>s+Number(r.test_qty||0),0);
    const bad=totalRows.reduce((s,r)=>s+Number(r.bad_qty||0),0);
    if(vals[0]) vals[0].textContent=`${state.from||''} ~ ${state.to||''}`;
    if(vals[1]) vals[1].textContent=`${lots.toLocaleString()} LOT`;
    if(vals[2]) vals[2].textContent=`${test.toLocaleString()} pcs`;
    if(vals[3]) vals[3].textContent=`${bad.toLocaleString()} pcs`;
  }
  function render(c){
    if(!c?.table)return;
    const total=state.rows.length;
    const pages=Math.max(1,Math.ceil(total/state.size));
    if(state.page>pages)state.page=pages;
    const start=(state.page-1)*state.size;
    const end=Math.min(start+state.size,total);
    let body=c.table.tBodies[0]; if(!body)body=c.table.createTBody();
    body.innerHTML=state.rows.slice(start,end).map(r=>{
      const test=Number(r.test_qty||0),bad=Number(r.bad_qty||0);
      const rate=test?(bad/test*100).toFixed(2):'0.00';
      const result=String(r.result||'PASS').toUpperCase();
      return `<tr><td>${esc(normDate(r.inspection_date))}</td><td>${esc(r.customer)}</td><td>${esc(r.part_no)}</td><td>${esc(r.part_name)}</td><td>${esc(r.lot_no)}</td><td>${Number(r.in_qty||0).toLocaleString()}</td><td>${test.toLocaleString()}</td><td>${bad.toLocaleString()}</td><td>${rate}%</td><td><span class="badge ${result==='FAIL'?'fail':'pass'}">${result}</span></td><td>${esc(r.inspector||'-')}</td></tr>`;
    }).join('')||'<tr><td colspan="11" class="empty">검색된 검사 이력이 없습니다.</td></tr>';
    let nav=c.table.parentElement.querySelector('.history-pagination');
    if(!nav){nav=document.createElement('div');nav.className='history-pagination';c.table.parentElement.appendChild(nav)}
    nav.innerHTML='';
    const info=document.createElement('div');info.className='history-pagination-info';info.textContent=`${total?start+1:0}-${end} / ${total}건`;
    const box=document.createElement('div');box.className='history-pagination-pages';
    const add=(txt,p,disabled,active)=>{const b=document.createElement('button');b.type='button';b.textContent=txt;b.disabled=disabled;if(active)b.className='active';b.onclick=()=>{state.page=p;render(c)};box.appendChild(b)};
    add('‹',Math.max(1,state.page-1),state.page===1,false);
    const list=[]; if(pages<=7){for(let p=1;p<=pages;p++)list.push(p)} else {list.push(1);if(state.page>4)list.push('…');for(let p=Math.max(2,state.page-1);p<=Math.min(pages-1,state.page+1);p++)list.push(p);if(state.page<pages-3)list.push('…');list.push(pages)}
    list.forEach(x=>x==='…'?box.insertAdjacentHTML('beforeend','<span class="dots">…</span>'):add(String(x),x,false,x===state.page));
    add('›',Math.min(pages,state.page+1),state.page===pages,false);
    const sz=document.createElement('div');sz.className='history-pagination-size';sz.innerHTML='페이지당 <select><option value="20">20</option><option value="50">50</option><option value="100">100</option></select>건';
    const sel=sz.querySelector('select');sel.value=String(state.size);sel.onchange=()=>{state.size=Number(sel.value)||20;state.page=1;render(c)};nav.append(info,box,sz);
    setSummary(c,state.rows);
  }
  async function load(force=false){
    const c=controls();if(!c||!c.h.classList.contains('active'))return;
    const from=normDate(c.dates[0]?.value)||'0000-01-01',to=normDate(c.dates[1]?.value)||'9999-12-31';
    const key=from+'|'+to+'|'+(c.text?.value||'')+'|'+(c.result?.value||'');
    if(!force&&key===state.lastKey)return;
    state.lastKey=key;
    try{const out=await fetchRows(c);state.from=out.from;state.to=out.to;state.rows=out.rows;state.page=1;render(c);}
    catch(e){console.error('[SJIT_HISTORY_FIX_V4]',e)}
  }
  function bind(){
    const c=controls();if(!c)return;
    if(c.queryBtn&&!c.queryBtn.dataset.histV4){c.queryBtn.dataset.histV4='1';c.queryBtn.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();load(true)},{capture:true})}
    c.dates.forEach(d=>{if(!d.dataset.histV4){d.dataset.histV4='1';d.addEventListener('change',()=>load(true))}});
    if(c.text&&!c.text.dataset.histV4){c.text.dataset.histV4='1';c.text.addEventListener('input',()=>{state.lastKey=null});c.text.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();load(true)}})}
    if(c.result&&!c.result.dataset.histV4){c.result.dataset.histV4='1';c.result.addEventListener('change',()=>load(true))}
  }
  function translateVietnamese(){
    if(window.top===window)return;
    const M={'Inspection History':'Lịch sử kiểm tra','검사 이력 조회 · Excel 일괄 업로드':'Tra cứu lịch sử kiểm tra · Tải Excel hàng loạt','Maker / Part / LOT':'Nhà cung cấp / Mã Part / Số LOT','All Result':'Tất cả kết quả','Excel 업로드':'Tải Excel','기간 조회':'Tra cứu theo thời gian','오늘':'Hôm nay','최근 7일':'7 ngày gần nhất','이번 달':'Tháng này','지난 달':'Tháng trước','조회':'Tra cứu','페이지당':'Mục mỗi trang','건':'mục','검사 이력 조회':'Tra cứu lịch sử kiểm tra','검사 이력 · Excel 일괄 업로드':'Lịch sử kiểm tra · Tải Excel hàng loạt','검사 LOT 수':'Số LOT kiểm tra','검사 수량':'Số lượng kiểm tra','불량 수량':'Số lượng lỗi','Date':'Ngày','Maker':'Nhà cung cấp','Part No.':'Mã Part','Part Name':'Tên Part','LOT':'Số LOT','In':'Nhập','Test':'Kiểm tra','Defect':'Lỗi','Rate(%)':'Tỷ lệ (%)','Result':'Kết quả','Inspector':'Nhân viên kiểm tra','초기화':'Đặt lại','전체':'Tất cả','PASS':'ĐẠT (PASS)','FAIL':'KHÔNG ĐẠT (FAIL)','검색된 검사 이력이 없습니다.':'Không tìm thấy lịch sử kiểm tra.','조회된 검사 이력이 없습니다.':'Không có lịch sử kiểm tra được tìm thấy.','대시보드':'Bảng điều khiển','일일검사 입력':'Nhập kiểm tra hàng ngày','검사 이력':'Lịch sử kiểm tra','통계':'Thống kê','부적합품 관리':'Quản lý sản phẩm không phù hợp','게시판':'Bảng thông báo','로그아웃':'Đăng xuất'};
    const d=document;const w=d.createTreeWalker(d.body,NodeFilter.SHOW_TEXT);const a=[];let n;while(n=w.nextNode()){const p=n.parentElement;if(!p||p.tagName==='SCRIPT'||p.tagName==='STYLE')continue;const raw=n.nodeValue.trim();if(M[raw])a.push([n,raw,M[raw]])}a.forEach(([n,r,o])=>n.nodeValue=n.nodeValue.replace(r,o));d.querySelectorAll('input,button,select').forEach(el=>['placeholder','title','aria-label'].forEach(k=>{const v=el.getAttribute(k);if(v&&M[v])el.setAttribute(k,M[v])}));d.documentElement.lang='vi';const b=$('langBtn');if(b){b.textContent='🇰🇷 한국어';b.onclick=()=>window.top.location.href='./index.html'}
  }
  function tick(){bind();if(history()?.classList.contains('active'))load();translateVietnamese()}
  document.addEventListener('click',e=>{if(e.target.closest?.('[data-page="history"]'))setTimeout(()=>load(true),300)});
  setInterval(tick,1200);setTimeout(tick,900);
})();
