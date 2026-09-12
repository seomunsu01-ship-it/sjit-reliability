from pathlib import Path

MARK = "SJIT_HISTORY_QUERY_FINAL_V6"
JS = r'''<script id="SJIT_HISTORY_QUERY_FINAL_V6">
(function(){
  if(window.__SJIT_HISTORY_V6__) return;
  window.__SJIT_HISTORY_V6__=true;
  var state={rows:[],page:1,size:20,loading:false};
  function esc(v){return String(v==null?'':v).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]})}
  function get(){
    var h=document.getElementById('history'); if(!h) return null;
    var dates=h.querySelectorAll('input[type="date"]');
    var text=h.querySelector('#search')||h.querySelector('input[type="text"]');
    var selects=h.querySelectorAll('select'), result=null;
    for(var i=0;i<selects.length;i++){if(/PASS|FAIL|All Result|Tất cả kết quả|Tất cả/i.test(selects[i].innerText)){result=selects[i];break}}
    var table=h.querySelector('table.table')||h.querySelector('table');
    var buttons=h.querySelectorAll('button'), apply=null;
    for(var j=0;j<buttons.length;j++){var t=(buttons[j].innerText||'').trim();if(/^(조회|검색|Search|Tra cứu)$/i.test(t)){apply=buttons[j];break}}
    return {h:h,from:dates[0],to:dates[1],text:text,result:result,table:table,apply:apply};
  }
  function query(){
    var c=get(), sb=window.sb;
    if(!c||!c.table||!sb||state.loading) return;
    state.loading=true;
    var from=c.from&&c.from.value?c.from.value:'0000-01-01';
    var to=c.to&&c.to.value?c.to.value:'9999-12-31';
    sb.from('daily_inspections').select('*').order('inspection_date',{ascending:false}).then(function(res){
      if(res.error) throw res.error;
      var term=((c.text&&c.text.value)||'').trim().toLowerCase();
      var rv=((c.result&&c.result.value)||'').trim().toUpperCase();
      state.rows=(res.data||[]).filter(function(r){
        var d=String(r.inspection_date||'').slice(0,10);
        var hay=[r.customer,r.maker,r.part_no,r.part_name,r.material_name,r.lot_no].map(function(v){return String(v==null?'':v).toLowerCase()}).join(' ');
        var rr=String(r.result==null?'':r.result).toUpperCase();
        return d>=from&&d<=to&&(!term||hay.indexOf(term)>=0)&&(!rv||rv==='ALL'||rv==='전체'||rv==='TẤT CẢ'||rr===rv);
      });
      state.page=1; render(c,from,to);
    }).catch(function(e){console.error(e);state.rows=[];render(c,from,to);}).then(function(){state.loading=false});
  }
  function render(c,from,to){
    if(!c||!c.table)return;
    var body=c.table.tBodies[0]||c.table.createTBody();
    var total=state.rows.length, pages=Math.max(1,Math.ceil(total/state.size));
    var start=(state.page-1)*state.size,end=Math.min(start+state.size,total);
    body.innerHTML=state.rows.slice(start,end).map(function(r){
      var inq=Number(r.in_qty!=null?r.in_qty:(r.incoming_qty!=null?r.incoming_qty:0));
      var test=Number(r.test_qty!=null?r.test_qty:(r.inspection_qty!=null?r.inspection_qty:0));
      var bad=Number(r.bad_qty!=null?r.bad_qty:(r.defect_qty!=null?r.defect_qty:0));
      var rate=test?(bad/test*100).toFixed(2):'0.00';
      var result=String(r.result||'PASS').toUpperCase();
      return '<tr><td>'+esc(String(r.inspection_date||'').slice(0,10))+'</td><td>'+esc(r.customer!=null?r.customer:r.maker)+'</td><td>'+esc(r.part_no)+'</td><td>'+esc(r.part_name!=null?r.part_name:r.material_name)+'</td><td>'+esc(r.lot_no||'-')+'</td><td>'+inq.toLocaleString()+'</td><td>'+test.toLocaleString()+'</td><td>'+bad.toLocaleString()+'</td><td>'+rate+'%</td><td><span class="badge '+(result==='FAIL'?'fail':'pass')+'">'+esc(result)+'</span></td><td>'+esc(r.inspector||'-')+'</td></tr>';
    }).join('')||'<tr><td colspan="11" class="empty">검색된 검사 이력이 없습니다.</td></tr>';
    var old=c.h.querySelector('.history-final-v6');if(old)old.remove();
    var nav=document.createElement('div');nav.className='history-final-v6';nav.style.cssText='display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 2px;border-top:1px solid #e2e8f0';
    var info=document.createElement('span');info.textContent=(total?(start+1):0)+'-'+end+' / '+total+'건';
    var box=document.createElement('span');
    function btn(label,p,disabled){var b=document.createElement('button');b.type='button';b.textContent=label;b.disabled=disabled;b.onclick=function(){state.page=p;render(get(),from,to)};box.appendChild(b)}
    btn('‹',Math.max(1,state.page-1),state.page===1);
    for(var p=1;p<=pages;p++){if(p>6&&p<pages-1){if(p===7){var d=document.createElement('span');d.textContent=' … ';box.appendChild(d)}continue}var b=document.createElement('button');b.type='button';b.textContent=p;b.className=p===state.page?'active':'';b.onclick=(function(x){return function(){state.page=x;render(get(),from,to)}})(p);box.appendChild(b)}
    btn('›',Math.min(pages,state.page+1),state.page===pages);
    var label=document.createElement('label');label.textContent='페이지당 ';
    var sel=document.createElement('select');[20,50,100].forEach(function(n){var o=document.createElement('option');o.value=n;o.textContent=n;sel.appendChild(o)});sel.value=state.size;sel.onchange=function(){state.size=Number(this.value);state.page=1;render(get(),from,to)};label.appendChild(sel);label.appendChild(document.createTextNode('건'));
    nav.appendChild(info);nav.appendChild(box);nav.appendChild(label);c.table.parentElement.appendChild(nav);
    var sum=c.h.querySelector('.history-final-v6-summary');if(!sum){sum=document.createElement('div');sum.className='history-final-v6-summary';c.table.parentElement.parentElement.insertBefore(sum,c.table.parentElement)}
    var lots={};state.rows.forEach(function(r){lots[r.lot_no||r.part_no||r.inspection_date]=1});
    var tq=state.rows.reduce(function(a,r){return a+Number(r.test_qty!=null?r.test_qty:(r.inspection_qty||0))},0);
    var bq=state.rows.reduce(function(a,r){return a+Number(r.bad_qty!=null?r.bad_qty:(r.defect_qty||0))},0);
    sum.innerHTML='<div>기간<br><b>'+esc(from)+' ~ '+esc(to)+'</b></div><div>검사 LOT 수<br><b>'+Object.keys(lots).length+' LOT</b></div><div>검사 수량<br><b>'+tq.toLocaleString()+' PCS</b></div><div>불량 수량<br><b style="color:#dc2626">'+bq.toLocaleString()+' PCS</b></div>';
  }
  function bind(){
    var c=get();if(!c)return;
    if(c.apply&&!c.apply.dataset.historyV6){c.apply.dataset.historyV6='1';c.apply.addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();query()},true)}
    [c.from,c.to].forEach(function(x){if(x&&!x.dataset.historyV6){x.dataset.historyV6='1';x.addEventListener('change',query)}});
    if(c.text&&!c.text.dataset.historyV6){c.text.dataset.historyV6='1';c.text.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();query()}})}
  }
  function active(){var h=document.getElementById('history');return h&&h.classList.contains('active')}
  function start(){if(!active())return;bind();if(!document.querySelector('.history-final-v6'))query()}
  setInterval(function(){if(active())bind()},700);
  document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('[data-page="history"]'))setTimeout(start,400)});
  setTimeout(start,1200);
})();
</script>'''

for name in ("daily-inspection/index.html", "daily-inspection/vi.html"):
    p = Path(name)
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    if MARK not in text:
        pos = text.lower().rfind("</body>")
        if pos >= 0:
            text = text[:pos] + JS + text[pos:]
            p.write_text(text, encoding="utf-8")
