from pathlib import Path

MARK = "SJIT_HISTORY_QUERY_SAFE_V7"
JS = """
<script id="SJIT_HISTORY_QUERY_SAFE_V7">
(function(){
  if(window.__SJIT_HISTORY_SAFE_V7__) return;
  window.__SJIT_HISTORY_SAFE_V7__ = true;
  function run(){
    var h=document.getElementById('history');
    var sb=window.sb;
    if(!h || !sb || !h.classList.contains('active')) return;
    var dates=h.querySelectorAll('input[type="date"]');
    var from=(dates[0]&&dates[0].value)||'0000-01-01';
    var to=(dates[1]&&dates[1].value)||'9999-12-31';
    var text=h.querySelector('#search')||h.querySelector('input[type="text"]');
    var term=((text&&text.value)||'').trim().toLowerCase();
    var sels=h.querySelectorAll('select');
    var result='';
    for(var i=0;i<sels.length;i++){
      if(/PASS|FAIL|All Result|Tất cả kết quả|Tất cả/i.test(sels[i].innerText||'')){result=(sels[i].value||'').toUpperCase();break;}
    }
    var table=h.querySelector('table.table')||h.querySelector('table');
    if(!table) return;
    sb.from('daily_inspections').select('*').order('inspection_date',{ascending:false}).then(function(res){
      if(res.error) throw res.error;
      var rows=(res.data||[]).filter(function(r){
        var d=String(r.inspection_date||'').slice(0,10);
        var hay=[r.customer,r.maker,r.part_no,r.part_name,r.material_name,r.lot_no].join(' ').toLowerCase();
        var rr=String(r.result||'').toUpperCase();
        return d>=from && d<=to && (!term || hay.indexOf(term)>=0) && (!result || result==='ALL' || result==='전체' || result==='TẤT CẢ' || rr===result);
      });
      var body=table.tBodies[0]||table.createTBody();
      body.innerHTML=rows.map(function(r){
        var test=Number(r.test_qty!=null?r.test_qty:(r.inspection_qty||0));
        var bad=Number(r.bad_qty!=null?r.bad_qty:(r.defect_qty||0));
        var inq=Number(r.in_qty!=null?r.in_qty:(r.incoming_qty||0));
        var rate=test?(bad/test*100).toFixed(2):'0.00';
        var rr=String(r.result||'PASS').toUpperCase();
        return '<tr><td>'+String(r.inspection_date||'').slice(0,10)+'</td><td>'+String(r.customer||r.maker||'')+'</td><td>'+String(r.part_no||'')+'</td><td>'+String(r.part_name||r.material_name||'')+'</td><td>'+String(r.lot_no||'-')+'</td><td>'+inq.toLocaleString()+'</td><td>'+test.toLocaleString()+'</td><td>'+bad.toLocaleString()+'</td><td>'+rate+'%</td><td>'+rr+'</td><td>'+String(r.inspector||'-')+'</td></tr>';
      }).join('') || '<tr><td colspan="11" class="empty">검색된 검사 이력이 없습니다.</td></tr>';
      var stat=h.querySelector('.history-period-summary');
      if(stat){
        var nums=stat.querySelectorAll('.hstat-value');
        if(nums.length>=3){nums[0].textContent=rows.length+' LOT';nums[1].textContent=rows.reduce(function(a,r){return a+Number(r.test_qty!=null?r.test_qty:(r.inspection_qty||0));},0).toLocaleString()+' PCS';nums[2].textContent=rows.reduce(function(a,r){return a+Number(r.bad_qty!=null?r.bad_qty:(r.defect_qty||0));},0).toLocaleString()+' PCS';}
      }
    }).catch(function(e){console.error('History query',e);});
  }
  function bind(){
    var h=document.getElementById('history'); if(!h) return;
    var dates=h.querySelectorAll('input[type="date"]');
    var buttons=h.querySelectorAll('button');
    for(var i=0;i<buttons.length;i++){
      var t=(buttons[i].innerText||'').trim();
      if(/^(조회|검색|Search|Tra cứu)$/i.test(t) && !buttons[i].dataset.safeQuery){
        buttons[i].dataset.safeQuery='1';
        buttons[i].addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();run();},true);
      }
    }
    for(var j=0;j<dates.length;j++) if(!dates[j].dataset.safeQuery){dates[j].dataset.safeQuery='1';dates[j].addEventListener('change',run);}
  }
  setInterval(bind,500);
  setTimeout(function(){bind();run();},1200);
})();
</script>
"""

for name in ("daily-inspection/index.html", "daily-inspection/vi.html"):
    p = Path(name)
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    if MARK not in text:
        pos = text.lower().rfind("</body>")
        if pos >= 0:
            p.write_text(text[:pos] + JS + text[pos:], encoding="utf-8")
