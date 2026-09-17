from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
s=re.sub(r'\n<style id="fix20260917">.*?</style>\n<script id="fix20260917">.*?</script>\n','\n',s,flags=re.S)
patch=r'''
<style id="fix20260917">
.report-pagination{display:flex;justify-content:center;align-items:center;gap:6px;margin-top:12px;flex-wrap:wrap}.report-pagination button{min-width:34px;height:34px;border:1px solid var(--line);background:#fff;color:var(--navy);border-radius:7px;font-weight:700;cursor:pointer}.report-pagination button.active{background:var(--blue);color:#fff;border-color:var(--blue)}.report-pagination button:disabled{opacity:.45;cursor:not-allowed}.report-page-info{font-size:11px;color:var(--muted);margin:0 8px}
</style>
<script id="fix20260917">
(function(){
 const $=id=>document.getElementById(id);
 const missing=()=>lang==='vi'?'Chưa nhập':lang==='en'?'Not Entered':'미입력';
 const condLabel=v=>{const c=cleanCond(v);return c==='미입력'?missing():c};
 const matLabel=v=>{const c=cleanMaterial(v);return c==='미입력'?missing():c};
 const resultLabel=v=>{const r=(v||'').toString().trim();return r||missing()};
 const statusLabel=v=>{const s=(v||'').toString().trim();if(s==='Finished')return lang==='vi'?'Hoàn thành':lang==='en'?'Completed':'완료';if(s==='신뢰성 진행 중')return lang==='vi'?'Đang thực hiện':lang==='en'?'In Progress':'TEST 중';return lang==='vi'?'Chờ xử lý':lang==='en'?'Pending':'대기'};
 const cpkLabel=v=>{const c=v||'미검토';return lang==='vi'?(c==='양호'?'Tốt':c==='보완필요'?'Cần cải thiện':'Chưa đánh giá'):lang==='en'?(c==='양호'?'Good':c==='보완필요'?'Needs Improvement':'Not Reviewed'):c};
 const reportState=has=>has?(lang==='vi'?'Đã phát hành':lang==='en'?'Issued':'발행'):(lang==='vi'?'Chưa phát hành':lang==='en'?'Not Issued':'미발행');
 const esc=window.escapeHtml||String;

 const reportTable=document.querySelector('#viewReport table');
 if(reportTable){
   const head=reportTable.querySelector('thead tr');
   if(head&&!head.querySelector('[data-fix-start]')){
     const a=document.createElement('th');a.dataset.fixStart='1';a.dataset.k='reliabilityStartDate';a.textContent='TEST 시작일';
     const b=document.createElement('th');b.dataset.fixEnd='1';b.dataset.k='reliabilityExpectedEndDate';b.textContent='TEST 종료예정일';
     const manage=head.lastElementChild;head.insertBefore(a,manage);head.insertBefore(b,manage);
   }
   if(!$('reportPagination')){const wrap=reportTable.closest('.tablewrap');if(wrap){const d=document.createElement('div');d.id='reportPagination';d.className='report-pagination';wrap.after(d)}}
 }

 window.reportPage=window.reportPage||1;
 window.renderReport=function(){
   initReportModels();
   const all=filteredReport().sort((a,b)=>String(b['Requested Date by Planning team']||'').localeCompare(String(a['Requested Date by Planning team']||'')));
   const issued=DATA.filter(x=>(x['Report No']||'').toString().trim()).length,total=DATA.length;
   $('rTotal').textContent=total;$('rIssued').textContent=issued;$('rMissing').textContent=total-issued;$('rRate').textContent=Math.round(issued/Math.max(total,1)*100)+'%';
   const size=10,pages=Math.max(1,Math.ceil(all.length/size));if(window.reportPage>pages)window.reportPage=pages;if(window.reportPage<1)window.reportPage=1;const page=window.reportPage,arr=all.slice((page-1)*size,page*size);
   $('reportBody').innerHTML=arr.length?arr.map((x,i)=>{
     const report=(x['Report No']||'').toString().trim(),rv=(x['Reliability Test Result']||'').toString().trim(),cpk=x['CPK Review Result']||'미검토',ts=x['Reliability Test Status']||'Not tested';
     const reportCell=report?`<button class="report-link" data-report="${esc(report)}" data-no="${esc(x.No)}">${esc(report)}</button>`:`<button class="smallbtn report-register" data-no="${esc(x.No)}">${esc(lang==='vi'?'Đăng ký Report':lang==='en'?'Register Report':'Report 등록')}</button>`;
     const cpkCls=cpk==='양호'?'cpk-good':cpk==='보완필요'?'cpk-improve':'cpk-review',tsCls=ts==='Finished'?'test-done':ts==='신뢰성 진행 중'?'test-run':'test-wait';
     return `<tr><td>${(page-1)*size+i+1}</td><td><span class="cpk-status ${cpkCls}">${esc(cpkLabel(cpk))}</span></td><td><span class="test-status ${tsCls}">${esc(statusLabel(ts))}</span></td><td>${esc(x['Requested Date by Planning team']||'-')}</td><td>${esc(x.Model||missing())}</td><td>${esc(matLabel(x.Material))}</td><td>${esc(condLabel(x['Test Condition']))}</td><td>${esc(resultLabel(rv))}</td><td>${reportCell}</td><td><span class="report-status ${report?'ok':'missing'}">${esc(reportState(!!report))}</span></td><td>${esc(x.PIC||'-')}</td><td>${esc(x['CR No']||'-')}</td><td>${esc(x['Reliability Test Start Date']||'-')}</td><td>${esc(x['Reliability Test Expected End Date']||'-')}</td><td><button class="smallbtn edit-report-item" type="button" data-no="${esc(x.No)}">${esc(lang==='vi'?'Sửa':lang==='en'?'Edit':'수정')}</button></td></tr>`;
   }).join(''):`<tr><td colspan="15" class="empty">${t('noData')}</td></tr>`;
   const pg=$('reportPagination');if(pg){let h=`<button ${page<=1?'disabled':''} data-rpage="${page-1}">‹</button>`;for(let n=1;n<=pages;n++)h+=`<button class="${n===page?'active':''}" data-rpage="${n}">${n}</button>`;h+=`<span class="report-page-info">${page} / ${pages}</span><button ${page>=pages?'disabled':''} data-rpage="${page+1}">›</button>`;pg.innerHTML=h;pg.querySelectorAll('[data-rpage]').forEach(b=>b.onclick=()=>{window.reportPage=Number(b.dataset.rpage);renderReport()})}
   refreshReportLinks();document.querySelectorAll('.edit-report-item').forEach(b=>b.onclick=()=>openManualForEdit(b.dataset.no));
 };

 window.renderDetailTable=function(){
   const arr=detailFiltered().sort((a,b)=>String(b['Requested Date by Planning team']||'').localeCompare(String(a['Requested Date by Planning team']||'')));
   $('detailCount').textContent=arr.length+' '+(lang==='ko'?'건':lang==='en'?'cases':'ca');
   $('detailBody').innerHTML=arr.length?arr.map((x,i)=>{const rv=x['Reliability Test Result']||'',st=x['Reliability Test Status']||'';const cls=rv==='Pass'?'pass':(rv==='Fail'||rv==='NG')?'fail':'pending';return `<tr data-no="${esc(x.No)}"><td>${i+1}</td><td>${esc(x['Requested Date by Planning team']||'-')}</td><td>${esc(x.Model||'-')}</td><td>${esc(matLabel(x.Material))}</td><td>${esc(condLabel(x['Test Condition']))}</td><td><span class="badge ${cls}">${esc(resultLabel(rv))}</span></td><td>${esc(statusLabel(st))}</td><td>${esc(x['Report No']||'-')}</td><td>${esc(x.PIC||'-')}</td><td>${esc(x['Reliability Test Start Date']||'-')}</td><td>${esc(x['Reliability Test Expected End Date']||'-')}</td></tr>`}).join(''):`<tr><td colspan="11" class="empty">${t('noData')}</td></tr>`;
   document.querySelectorAll('#detailBody tr[data-no]').forEach(tr=>tr.onclick=()=>openDetail(tr.dataset.no));
   const head=document.querySelector('#viewOverview table thead tr');if(head&&!head.querySelector('[data-fix-start]')){const a=document.createElement('th');a.dataset.fixStart='1';a.textContent='TEST 시작일';const b=document.createElement('th');b.dataset.fixEnd='1';b.textContent='TEST 종료예정일';head.append(a,b)}
 };

 const oldMat=window.renderMaterialAnalysis;window.renderMaterialAnalysis=function(){oldMat();document.querySelectorAll('#materialAnalysisBody td').forEach(td=>{if(td.textContent.trim()==='미입력')td.textContent=missing()})};

 const oldShow=window.showReportModalV16;window.showReportModalV16=async function(no){await oldShow(no);const d=$('deleteReportLink'),dt=$('deleteTestItemLink'),op=$('openReportFile'),dl=$('downloadReportLink'),sv=$('saveReportLink');if(d)d.textContent=lang==='vi'?'Xóa Report':lang==='en'?'Delete Report':'Report 삭제';if(dt)dt.textContent=lang==='vi'?'Xóa hạng mục kiểm tra':lang==='en'?'Delete Test Item':'시험 항목 삭제';if(op&&op.style.display!=='none')op.textContent=lang==='vi'?'Mở Report':lang==='en'?'Open Report':'Report 열기';if(dl&&dl.style.display!=='none')dl.textContent=lang==='vi'?'Tải Report':lang==='en'?'Download Report':'Report 다운로드';if(sv)sv.textContent=lang==='vi'?'Lưu liên kết':lang==='en'?'Save Link':'연결 저장'};

 const result=$('mResult'),after=$('mResultAfter');
 function resetResultOptions(){const first=lang==='vi'?'Chọn':lang==='en'?'Select':'선택';if(result)result.innerHTML=`<option value="">${first}</option><option value="Pass">Pass</option><option value="Fail">Fail</option>`;if(after)after.innerHTML=`<option value="">${first}</option><option value="Pass">Pass</option><option value="Fail">Fail</option>`}
 resetResultOptions();
 const oldSave=window.saveManualV16;window.saveManualV16=async function(closeAfter){const r=result?.value||'',a=after?.value||'';if(r&&!['Pass','Fail'].includes(r)){alert(lang==='vi'?'Kết quả chỉ được chọn Pass hoặc Fail.':lang==='en'?'Result must be Pass or Fail.':'결과는 Pass 또는 Fail만 선택할 수 있습니다.');return}if(a&&!['Pass','Fail'].includes(a)){alert(lang==='vi'?'Kết quả sau kiểm tra chỉ được chọn Pass hoặc Fail.':lang==='en'?'After-test result must be Pass or Fail.':'신뢰성 시험 후 결과는 Pass 또는 Fail만 선택할 수 있습니다.');return}return oldSave(closeAfter)};

 const baseSet=window.setLang;if(baseSet&&!baseSet.__fix20260917){const wrapped=function(l){baseSet(l);resetResultOptions();const vi=l==='vi',en=l==='en';const map={manualCancel:vi?'Hủy':en?'Cancel':'취소',manualSaveContinue:vi?'Lưu và tiếp tục':en?'Save & Continue':'저장 후 계속 등록',manualSave:vi?'Lưu và đóng':en?'Save & Close':'저장 후 닫기',deleteReportLink:vi?'Xóa Report':en?'Delete Report':'Report 삭제',deleteTestItemLink:vi?'Xóa hạng mục kiểm tra':en?'Delete Test Item':'시험 항목 삭제',saveReportLink:vi?'Lưu liên kết':en?'Save Link':'연결 저장'};Object.entries(map).forEach(([id,v])=>{const e=$(id);if(e)e.textContent=v});window.reportPage=1;renderReport()};wrapped.__fix20260917=true;window.setLang=wrapped}

 setTimeout(()=>{try{renderReport()}catch(e){}try{renderDetailTable()}catch(e){}},0);
})();
'''
s=s.replace('</body>',patch+'\n</body>')
p.write_text(s,encoding='utf-8')
print('applied 2026-09-17 fix',len(s))
