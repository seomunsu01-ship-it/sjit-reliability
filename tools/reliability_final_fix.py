import re
from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
original=s

# Add a real per-row attachment delete button.
if 'id="deleteReportLink"' not in s:
    anchor='<button class="btn danger" id="deleteTestItemLink"'
    if anchor in s:
        s=s.replace(anchor,'<button class="btn danger" id="deleteReportLink" type="button" style="display:none">첨부파일 삭제</button>\n'+anchor,1)

# Replace upload logic with strict row-id isolation and date stamping.
a=s.find('async function uploadReportV16(rowId,file){')
b=s.find('async function makeSignedReportUrlV16',a)
if a>=0 and b>a:
    fn='''async function uploadReportV16(rowId,file){\n  const targetNo=Number(rowId);\n  if(!targetNo||!file)throw new Error('Report 파일과 시험 항목을 확인하세요.');\n  const old=await getReportInfoV16(targetNo).catch(()=>null);\n  const row=DATA.find(r=>Number(r.No)===targetNo);\n  if(!row)throw new Error('선택한 시험 항목을 찾을 수 없습니다.');\n  const ext=((file.name||'').match(/\\.([A-Za-z0-9]+)$/)||['','bin'])[1].toLowerCase();\n  const token=(crypto.randomUUID?crypto.randomUUID().replace(/-/g,''):String(Date.now())+Math.random().toString(36).slice(2));\n  const path=`reports/${targetNo}/${Date.now()}_${token}.${ext}`;\n  const {error:upErr}=await supabaseClient.storage.from(REPORT_BUCKET_V16).upload(path,file,{upsert:false,contentType:file.type||'application/octet-stream'});\n  if(upErr)throw upErr;\n  const todayISO=new Date().toISOString().slice(0,10);\n  const status=row['Reliability Test Status']||'Not tested';\n  let start=row['Reliability Test Start Date']||null;\n  let end=row['Reliability Test Expected End Date']||null;\n  if(status==='신뢰성 진행 중'&&!start)start=todayISO;\n  if(status==='Finished'&&!start)start=todayISO;\n  if(status==='Finished'&&!end)end=todayISO;\n  const patch={report_path:path,report_filename:file.name,report_mime:file.type||null,reliability_start_date:start,reliability_expected_end_date:end,updated_at:new Date().toISOString()};\n  const {data,error:dbErr}=await supabaseClient.from('reliability_tests').update(patch).eq('id',targetNo).select('*').single();\n  if(dbErr){await supabaseClient.storage.from(REPORT_BUCKET_V16).remove([path]).catch(()=>{});throw dbErr;}\n  if(old?.report_path&&old.report_path!==path)await supabaseClient.storage.from(REPORT_BUCKET_V16).remove([old.report_path]).catch(()=>{});\n  return mapDbRow(data);\n}\n'''
    s=s[:a]+fn+s[b:]

# Remove every duplicate report-modal item id assignment, then add exactly one.
s=re.sub(r"\s*document\.getElementById\('reportModal'\)\.dataset\.itemId\s*=\s*String\(no\);",'',s)
needle="  currentReportNo=String(no);currentReportFile=null;"
if needle in s:
    s=s.replace(needle,needle+"document.getElementById('reportModal').dataset.itemId=String(no);",1)

# Remove every existing delete-file declaration/hide statement, then add exactly one.
decl=re.compile(r"\s*const\s+deleteFileBtn\s*=\s*document\.getElementById\('deleteReportLink'\)\s*;\s*if\s*\(deleteFileBtn\)\s*deleteFileBtn\.style\.display\s*=\s*'none'\s*;",re.S)
s=decl.sub('',s)
open_anchor="  const openBtn=document.getElementById('openReportFile');openBtn.style.display='none';"
if open_anchor in s:
    s=s.replace(open_anchor,open_anchor+"const deleteFileBtn=document.getElementById('deleteReportLink');if(deleteFileBtn)deleteFileBtn.style.display='none';",1)

# Bind attachment delete once.
s=s.replace("document.getElementById('deleteReportLink').onclick=()=>window.deleteReportNow();\n",'')
marker='window.deleteReportNow = async function(){'
if marker in s:
    s=s.replace(marker,"document.getElementById('deleteReportLink').onclick=()=>window.deleteReportNow();\n"+marker,1)

# Status transition dates.
old_marker="  const statusValue=document.getElementById('mStatus').value||null;\n  let reliabilityStartDate=document.getElementById('mReliabilityStartDate').value||old['Reliability Test Start Date']||null;\n  let reliabilityExpectedEndDate=document.getElementById('mReliabilityExpectedEndDate').value||old['Reliability Test Expected End Date']||null;\n  const todayISO=new Date().toISOString().slice(0,10);\n  if(statusValue==='신뢰성 진행 중' && !reliabilityStartDate) reliabilityStartDate=todayISO;\n  if(statusValue==='Finished' && !reliabilityExpectedEndDate) reliabilityExpectedEndDate=todayISO;"
new_marker="  const statusValue=document.getElementById('mStatus').value||null;\n  const oldStatus=old['Reliability Test Status']||'Not tested';\n  let reliabilityStartDate=document.getElementById('mReliabilityStartDate').value||old['Reliability Test Start Date']||null;\n  let reliabilityExpectedEndDate=document.getElementById('mReliabilityExpectedEndDate').value||old['Reliability Test Expected End Date']||null;\n  const todayISO=new Date().toISOString().slice(0,10);\n  if(statusValue==='신뢰성 진행 중' && oldStatus!=='신뢰성 진행 중' && !reliabilityStartDate) reliabilityStartDate=todayISO;\n  if(statusValue==='Finished' && oldStatus==='신뢰성 진행 중' && !reliabilityExpectedEndDate) reliabilityExpectedEndDate=todayISO;"
if old_marker in s:s=s.replace(old_marker,new_marker,1)

p.write_text(s,encoding='utf-8')
print('changed:',s!=original)
