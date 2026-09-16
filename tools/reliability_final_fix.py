import re
from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
original=s

# 1) Ensure a real per-report delete control exists in the report modal.
if 'id="deleteReportLink"' not in s:
    anchors=[
        '<button class="btn danger" id="deleteTestItemLink"',
        '<input type="file" id="reportFileInput"',
    ]
    inserted=False
    for anchor in anchors:
        if anchor in s:
            s=s.replace(anchor,'<button class="btn danger" id="deleteReportLink" type="button" style="display:none">첨부파일 삭제</button>\n'+anchor,1)
            inserted=True
            break

# 2) Replace report upload with strict row-id based storage and DB update.
a=s.find('async function uploadReportV16(rowId,file){')
b=s.find('async function makeSignedReportUrlV16',a)
if a>=0 and b>a:
    fn='''async function uploadReportV16(rowId,file){\n  const targetNo=Number(rowId);\n  if(!targetNo||!file)throw new Error('Report 파일과 시험 항목을 확인하세요.');\n  const old=await getReportInfoV16(targetNo).catch(()=>null);\n  const row=DATA.find(r=>Number(r.No)===targetNo);\n  if(!row)throw new Error('선택한 시험 항목을 찾을 수 없습니다.');\n  const ext=((file.name||'').match(/\\.([A-Za-z0-9]+)$/)||['','bin'])[1].toLowerCase();\n  const token=(crypto.randomUUID?crypto.randomUUID().replace(/-/g,''):String(Date.now())+Math.random().toString(36).slice(2));\n  const path=`reports/${targetNo}/${Date.now()}_${token}.${ext}`;\n  const {error:upErr}=await supabaseClient.storage.from(REPORT_BUCKET_V16).upload(path,file,{upsert:false,contentType:file.type||'application/octet-stream'});\n  if(upErr)throw upErr;\n  const todayISO=new Date().toISOString().slice(0,10);\n  const status=row['Reliability Test Status']||'Not tested';\n  let start=row['Reliability Test Start Date']||null;\n  let end=row['Reliability Test Expected End Date']||null;\n  if(status==='신뢰성 진행 중'&&!start)start=todayISO;\n  if(status==='Finished'&&!start)start=todayISO;\n  if(status==='Finished'&&!end)end=todayISO;\n  const patch={report_path:path,report_filename:file.name,report_mime:file.type||null,reliability_start_date:start,reliability_expected_end_date:end,updated_at:new Date().toISOString()};\n  const {data,error:dbErr}=await supabaseClient.from('reliability_tests').update(patch).eq('id',targetNo).select('*').single();\n  if(dbErr){await supabaseClient.storage.from(REPORT_BUCKET_V16).remove([path]).catch(()=>{});throw dbErr;}\n  if(old?.report_path&&old.report_path!==path)await supabaseClient.storage.from(REPORT_BUCKET_V16).remove([old.report_path]).catch(()=>{});\n  return mapDbRow(data);\n}\n'''
    s=s[:a]+fn+s[b:]

# 3) Remove duplicated modal item-id assignments/declarations created by earlier patches.
s=re.sub(r"\s*document\.getElementById\('reportModal'\)\.dataset\.itemId\s*=\s*String\(no\)\s*;",'',s)
needle="  currentReportNo=String(no);currentReportFile=null;"
if needle in s and "currentReportNo=String(no);currentReportFile=null;document.getElementById('reportModal').dataset.itemId=String(no);" not in s:
    s=s.replace(needle,needle+"document.getElementById('reportModal').dataset.itemId=String(no);",1)
s=re.sub(r"const\s+deleteFileBtn\s*=\s*document\.getElementById\('deleteReportLink'\)\s*;",'',s)
s=re.sub(r"if\s*\(\s*deleteFileBtn\s*\)\s*deleteFileBtn\.style\.display\s*=\s*['\"]none['\"]\s*;",'',s)
open_anchor="  const openBtn=document.getElementById('openReportFile');openBtn.style.display='none';"
if open_anchor in s and "const deleteFileBtn=document.getElementById('deleteReportLink');if(deleteFileBtn)deleteFileBtn.style.display='none';" not in s:
    s=s.replace(open_anchor,open_anchor+"const deleteFileBtn=document.getElementById('deleteReportLink');if(deleteFileBtn)deleteFileBtn.style.display='none';",1)
s=s.replace("document.getElementById('deleteReportLink').onclick=()=>window.deleteReportNow();\n",'')
marker='window.deleteReportNow = async function(){'
if marker in s:
    s=s.replace(marker,"const __deleteReportLink=document.getElementById('deleteReportLink');if(__deleteReportLink)__deleteReportLink.onclick=()=>window.deleteReportNow();\n"+marker,1)

# 4) Status/date save logic: always fill dates when a row is saved as running/finished.
old_marker="  const statusValue=document.getElementById('mStatus').value||null;\n  let reliabilityStartDate=document.getElementById('mReliabilityStartDate').value||old['Reliability Test Start Date']||null;\n  let reliabilityExpectedEndDate=document.getElementById('mReliabilityExpectedEndDate').value||old['Reliability Test Expected End Date']||null;\n  const todayISO=new Date().toISOString().slice(0,10);\n  if(statusValue==='신뢰성 진행 중' && !reliabilityStartDate) reliabilityStartDate=todayISO;\n  if(statusValue==='Finished' && !reliabilityExpectedEndDate) reliabilityExpectedEndDate=todayISO;"
new_marker="  const statusValue=document.getElementById('mStatus').value||null;\n  let reliabilityStartDate=document.getElementById('mReliabilityStartDate').value||old['Reliability Test Start Date']||null;\n  let reliabilityExpectedEndDate=document.getElementById('mReliabilityExpectedEndDate').value||old['Reliability Test Expected End Date']||null;\n  const todayISO=new Date().toISOString().slice(0,10);\n  if(statusValue==='신뢰성 진행 중' && !reliabilityStartDate) reliabilityStartDate=todayISO;\n  if(statusValue==='Finished' && !reliabilityStartDate) reliabilityStartDate=todayISO;\n  if(statusValue==='Finished' && !reliabilityExpectedEndDate) reliabilityExpectedEndDate=todayISO;"
if old_marker in s:s=s.replace(old_marker,new_marker,1)

# 5) Final browser-side guard. This is intentionally idempotent and does not depend on
# the exact older modal HTML. It provides draft persistence, independent report UI,
# and injects start/end date columns into the reliability-status table when headers exist.
guard='''\n<script id="reliabilityFinalGuard">\n(function(){\n  const DRAFT_KEY='sjit_reliability_report_draft_v1';\n  const $=id=>document.getElementById(id);\n  function modal(){return $('reportModal');}\n  function isOpen(){const m=modal();return !!(m&&m.classList.contains('show'));}\n  function fields(){return ['mRequestDate','mModel','mMaterial','mTestItem','mTestResult','mCpkReview','mResultBefore','mResultAfter','mStatus','mReliabilityStartDate','mReliabilityExpectedEndDate','mReportNo','mReportPublished','mPic','mCrNo','mTestQty','mLotNo','mProductionDate','mReason','mRemark'];}\n  function saveDraft(){if(!isOpen())return;const o={};fields().forEach(id=>{const e=$(id);if(e)o[id]=e.value;});try{sessionStorage.setItem(DRAFT_KEY,JSON.stringify(o));}catch(e){}}\n  function restoreDraft(){let o=null;try{o=JSON.parse(sessionStorage.getItem(DRAFT_KEY)||'null');}catch(e){}if(!o)return;fields().forEach(id=>{const e=$(id);if(e&&o[id]!==undefined&&e.value==='')e.value=o[id];});}\n  function clearDraft(){try{sessionStorage.removeItem(DRAFT_KEY);}catch(e){}}\n  function wireDraft(){fields().forEach(id=>{const e=$(id);if(e&&!e.dataset.draftWired){e.addEventListener('input',saveDraft);e.addEventListener('change',saveDraft);e.dataset.draftWired='1';}});}\n  const oldShow=window.showReportModalV16;\n  if(typeof oldShow==='function'&&!oldShow.__draftWrapped){window.showReportModalV16=function(){const r=oldShow.apply(this,arguments);setTimeout(()=>{wireDraft();restoreDraft();},0);return r;};window.showReportModalV16.__draftWrapped=true;}\n  document.addEventListener('click',function(ev){\n    const nav=ev.target.closest('.nav button');\n    if(nav&&isOpen()){saveDraft();}\n    const save=ev.target.closest('#saveManualBtn,#saveReportBtn,[data-action="save-report"]');\n    if(save){setTimeout(()=>{if(!isOpen())clearDraft();},300);}\n  },true);\n  const observer=new MutationObserver(()=>{if(isOpen())wireDraft();});\n  observer.observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['class']});\n\n  // Prevent backdrop clicks from destroying an in-progress registration. The X/close button still works.\n  document.addEventListener('click',function(ev){const m=modal();if(m&&ev.target===m&&isOpen()){ev.stopPropagation();}},true);\n\n  // Ensure the delete button is visible only for the currently selected report.\n  window.__syncReportDeleteButton=function(){\n    const b=$('deleteReportLink');if(!b)return;\n    const no=Number(modal()?.dataset.itemId||window.currentReportNo||0);\n    const row=(window.DATA||[]).find(r=>Number(r.No)===no);\n    const has=!!(row&&row.__report_path);\n    b.style.display=has?'inline-block':'none';\n  };\n\n  // Add date columns to the status table without duplicating them.\n  window.__ensureReliabilityDateColumns=function(){\n    const tables=[...document.querySelectorAll('table')];\n    tables.forEach(t=>{\n      const head=t.querySelector('thead tr');if(!head)return;\n      const texts=[...head.children].map(x=>(x.textContent||'').trim());\n      if(!texts.some(x=>x.includes('TEST 시작일'))){\n        const th=document.createElement('th');th.textContent='TEST 시작일';head.appendChild(th);\n      }\n      if(!texts.some(x=>x.includes('TEST 종료예정일'))){\n        const th=document.createElement('th');th.textContent='TEST 종료예정일';head.appendChild(th);\n      }\n      const rows=[...t.querySelectorAll('tbody tr')];\n      rows.forEach((tr,i)=>{\n        const cells=[...tr.children];\n        if(cells.length<2)return;\n        if(tr.querySelector('[data-rel-date="start"]'))return;\n        const noText=(cells[0]?.textContent||'').trim();\n        const no=Number(noText.replace(/[^0-9]/g,''));\n        const row=(window.DATA||[]).find(r=>Number(r.No)===no);\n        if(!row)return;\n        let td=document.createElement('td');td.dataset.relDate='start';td.textContent=row['Reliability Test Start Date']||'-';tr.appendChild(td);\n        td=document.createElement('td');td.dataset.relDate='end';td.textContent=row['Reliability Test Expected End Date']||'-';tr.appendChild(td);\n      });\n    });\n  };\n  setInterval(window.__ensureReliabilityDateColumns,1200);\n})();\n</script>\n'''
if 'id="reliabilityFinalGuard"' not in s:
    s=s.replace('</body>',guard+'</body>')

p.write_text(s,encoding='utf-8')
print('changed:',s!=original)
