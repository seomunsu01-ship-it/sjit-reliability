from pathlib import Path
MARK='SJIT_PAGINATION_UI_V1'
JS=r'''<script>/* SJIT_PAGINATION_UI_V1 */(()=>{const vi=location.search.includes('vi');function fix(){const h=document.getElementById('history');if(!h||!h.classList.contains('active'))return;const n=h.querySelector('.history-pagination')||h.querySelector('.history-final-pagination');if(!n)return;n.style.cssText+=';position:sticky;bottom:0;z-index:20;display:flex;align-items:center;justify-content:center;gap:18px;padding:10px 12px;margin-top:10px;background:rgba(255,255,255,.97);border-top:1px solid #e2e8f0;box-shadow:0 -4px 14px rgba(15,23,42,.08);flex-wrap:wrap;';const s=n.querySelector('.history-pagination-size select')||n.querySelector('select');if(s){s.setAttribute('aria-label',vi?'Số mục mỗi trang':'페이지당 건수');if(![...s.options].some(o=>o.value==='20'))s.innerHTML='<option value="20">20</option><option value="50">50</option><option value="100">100</option>'}if(vi){const w=document.createTreeWalker(n,NodeFilter.SHOW_TEXT),a=[];let x;while(x=w.nextNode()){if(x.parentElement?.tagName==='SCRIPT'||x.parentElement?.tagName==='STYLE')continue;a.push(x)}a.forEach(t=>{t.nodeValue=t.nodeValue.replace(/페이지당/g,'Mục mỗi trang').replace(/(\d+)건/g,'$1 mục').replace(/검사 LOT 수/g,'Số LOT kiểm tra').replace(/검사 수량/g,'Số lượng kiểm tra').replace(/불량 수량/g,'Số lượng lỗi')})}}document.addEventListener('click',e=>{if(e.target.closest?.('[data-page="history"]'))setTimeout(fix,300)});setInterval(fix,700);setTimeout(fix,800)})();</script>'''
for name in ('daily-inspection/index.html','daily-inspection/vi.html'):
 p=Path(name)
 if p.exists():
  s=p.read_text(encoding='utf-8')
  if MARK not in s:
   s=s.replace('</body></html>',JS+'</body></html>') if '</body></html>' in s else s.replace('</body>',JS+'</body>')
   p.write_text(s,encoding='utf-8')
