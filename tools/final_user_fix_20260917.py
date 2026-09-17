from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Replace only our own previous patch so reruns are idempotent.
s=re.sub(r'\n<style id="finalUserFix20260917">.*?</style>\n<script id="finalUserFix20260917">.*?</script>\n','\n',s,flags=re.S)

patch=r'''
<style id="finalUserFix20260917">
.final-user-pagination{display:flex;justify-content:center;align-items:center;gap:6px;flex-wrap:wrap;margin:10px 0 2px;padding:8px 0}.final-user-pagination button{min-width:32px;height:32px;border:1px solid var(--line);background:#fff;color:var(--navy);border-radius:7px;font-weight:700;cursor:pointer}.final-user-pagination button.active{background:var(--blue);color:#fff;border-color:var(--blue)}.final-user-pagination button:disabled{opacity:.45;cursor:not-allowed}.final-user-pagination .info{font-size:11px;color:var(--muted);margin:0 8px}
</style>
<script id="finalUserFix20260917">
(function(){
  const $=id=>document.getElementById(id);
  const getLang=()=>{try{return typeof lang!=='undefined'?lang:(window.lang||'ko')}catch(e){return window.lang||'ko'}};
  const vi=()=>getLang()==='vi';
  const en=()=>getLang()==='en';
  const textMap={
    '신뢰성 전 CPK 검토결과':'Kết quả đánh giá CPK trước kiểm tra độ tin cậy','신뢰성 TEST 결과':'Kết quả TEST độ tin cậy','신뢰성 TEST 상태':'Trạng thái TEST độ tin cậy','신뢰성 TEST 시작 일자':'Ngày bắt đầu TEST độ tin cậy','신뢰성 TEST 시작일':'Ngày bắt đầu TEST độ tin cậy','신뢰성 TEST 종료 예정 일자':'Ngày dự kiến kết thúc TEST độ tin cậy','신뢰성 TEST 종료예정일':'Ngày dự kiến kết thúc TEST độ tin cậy','Report 발송 여부':'Trạng thái gửi Report','Report 파일':'Tệp Report','생산일':'Ngày sản xuất','생성일':'Ngày tạo','reason':'Lý do','remark':'Ghi chú','미발송':'Chưa gửi','미발행':'Chưa phát hành','발행':'Đã phát hành','미실시':'Chưa thử nghiệm','시험 미실시':'Chưa thử nghiệm','시험 결과 미입력':'Chưa nhập kết quả','시험 결과':'Kết quả kiểm tra','시험 항목':'Hạng mục kiểm tra','신뢰성 TEST 상태':'Trạng thái TEST độ tin cậy','신뢰성 TEST 결과':'Kết quả TEST độ tin cậy','신뢰성 진행 중':'Đang thực hiện','미입력':'Chưa nhập','미검토':'Chưa đánh giá','양호':'Tốt','보완필요':'Cần cải thiện','Report 등록':'Đăng ký Report','수정':'Sửa','수정 저장':'Lưu thay đổi','저장':'Lưu','저장 후 닫기':'Lưu và đóng','저장 후 계속 등록':'Lưu và tiếp tục','취소':'Hủy','삭제':'Xóa','시험 항목 삭제':'Xóa hạng mục kiểm tra','Report 삭제':'Xóa Report','Report 열기':'Mở Report','Report 다운로드':'Tải Report','연결 저장':'Lưu liên kết','파일 선택':'Chọn tệp','선택':'Chọn','Test Qty':'Số lượng thử nghiệm','Lot No.':'Lot No.','PIC':'PIC','CR No.':'CR No.','Report No.':'Số Report','저장 실패':'Lưu thất bại','DB 저장 중...':'Đang lưu DB...','등록':'Đăng ký','완료':'Hoàn thành','대기':'Chờ xử lý','TEST 중':'Đang thực hiện'
  };
  const textMapEn={
    '신뢰성 전 CPK 검토결과':'CPK Review Result Before Reliability Test','신뢰성 TEST 결과':'Reliability Test Result','신뢰성 TEST 상태':'Reliability Test Status','신뢰성 TEST 시작 일자':'Reliability Test Start Date','신뢰성 TEST 종료 예정 일자':'Reliability Test Expected End Date','Report 발송 여부':'Report Issue Status','Report 파일':'Report File','생산일':'Production Date','생성일':'Created Date','reason':'Reason','remark':'Remark','미발송':'Not Sent','미발행':'Not Issued','발행':'Issued','미실시':'Not Tested','시험 미실시':'Not Tested','시험 결과 미입력':'Result Not Entered','시험 결과':'Test Result','시험 항목':'Test Item','신뢰성 진행 중':'In Progress','미입력':'Not Entered','미검토':'Not Reviewed','양호':'Good','보완필요':'Needs Improvement','Report 등록':'Register Report','수정':'Edit','수정 저장':'Save Changes','저장':'Save','저장 후 닫기':'Save & Close','저장 후 계속 등록':'Save & Continue','취소':'Cancel','삭제':'Delete','시험 항목 삭제':'Delete Test Item','Report 삭제':'Delete Report','Report 열기':'Open Report','Report 다운로드':'Download Report','연결 저장':'Save Link','파일 선택':'Choose File','선택':'Select','Test Qty':'Test Qty','Lot No.':'Lot No.','PIC':'PIC','CR No.':'CR No.','Report No.':'Report No.','저장 실패':'Save failed','DB 저장 중...':'Saving to DB...','등록':'Register','완료':'Completed','대기':'Pending','TEST 중':'In Progress'
  };
  function translateDom(){
    const map=vi()?textMap:(en()?textMapEn:{}); if(!Object.keys(map).length)return;
    document.querySelectorAll('label,button,option,th,h1,h2,h3,h4,p,span,div').forEach(el=>{
      if(el.children.length===0){const t=(el.textContent||'').trim();if(map[t])el.textContent=map[t];}
    });
    document.querySelectorAll('input,textarea').forEach(el=>{const p=el.getAttribute('placeholder');if(p&&map[p])el.setAttribute('placeholder',map[p]);});
    document.querySelectorAll('select').forEach(sel=>{[...sel.options].forEach(o=>{const t=o.textContent.trim();if(map[t])o.textContent=map[t]})});
  }

  const nativeAlert=window.alert.bind(window);
  window.alert=function(msg){
    let s=String(msg??'');
    if(vi()){
      s=s.replace(/^저장 실패\s*:/,'Lưu thất bại:').replace('선택한 시험 항목을 찾을 수 없습니다.','Không tìm thấy hạng mục kiểm tra đã chọn.').replace('Report 파일과 시험 항목을 확인하세요.','Vui lòng kiểm tra tệp Report và hạng mục kiểm tra.').replace('파일과 시험 항목을 확인하세요.','Vui lòng kiểm tra tệp và hạng mục kiểm tra.');
    }else if(en()){
      s=s.replace(/^저장 실패\s*:/,'Save failed:').replace('선택한 시험 항목을 찾을 수 없습니다.','Selected test item was not found.').replace('Report 파일과 시험 항목을 확인하세요.','Please check the Report file and test item.');
    }
    nativeAlert(s);
  };

  function paginateMaterial(){
    const body=$('materialAnalysisBody'); if(!body)return;
    const table=body.closest('table'); if(!table)return;
    const rows=[...body.querySelectorAll('tr')]; const size=10; const pages=Math.max(1,Math.ceil(rows.length/size));
    let page=Number(table.dataset.finalPage||1); if(page>pages)page=pages;if(page<1)page=1;table.dataset.finalPage=page;
    rows.forEach((r,i)=>r.style.display=(i>=(page-1)*size&&i<page*size)?'':'none');
    let nav=table.parentElement.querySelector(':scope > .final-user-pagination');
    if(!nav){nav=document.createElement('div');nav.className='final-user-pagination';table.parentElement.appendChild(nav)}
    let h=`<button type="button" ${page<=1?'disabled':''} data-fup="${page-1}">‹</button>`;
    for(let i=1;i<=pages;i++)h+=`<button type="button" class="${i===page?'active':''}" data-fup="${i}">${i}</button>`;
    const from=rows.length?((page-1)*size+1):0,to=Math.min(page*size,rows.length);const info=vi()?`Trang ${page}/${pages} · ${from}-${to}/${rows.length}`:en()?`Page ${page}/${pages} · ${from}-${to}/${rows.length}`:`${page}/${pages} · ${from}-${to}/${rows.length}`;
    h+=`<span class="info">${info}</span><button type="button" ${page>=pages?'disabled':''} data-fup="${page+1}">›</button>`;nav.innerHTML=h;
    nav.querySelectorAll('[data-fup]').forEach(b=>b.onclick=()=>{table.dataset.finalPage=b.dataset.fup;paginateMaterial();});
  }

  function clearNewRegistration(no){
    try{
      const modal=$('reportModal');if(!modal)return;
      const input=$('reportFileInput');
      let row=(window.DATA||[]).find(r=>Number(r.No)===Number(no));
      const hasExisting=!!(row&&row.__report_path);
      if(!hasExisting){
        sessionStorage.removeItem('sjit_reliability_report_draft_v2');
        if(input){input.value='';input.removeAttribute('data-selected-file');}
        if(window.currentReportFile!==undefined)window.currentReportFile=null;
        const note=modal.querySelector('.file-note');if(note)note.textContent=vi()?'Chưa chọn tệp Report.':en()?'No Report file selected.':'Report 파일을 선택하세요.';
      }
    }catch(e){}
  }

  const oldShow=window.showReportModalV16;
  if(typeof oldShow==='function'&&!oldShow.__finalUserFix){
    window.showReportModalV16=async function(no){const r=await oldShow.apply(this,arguments);setTimeout(()=>{clearNewRegistration(no);translateDom();},80);return r;};
    window.showReportModalV16.__finalUserFix=true;
  }

  const oldUpload=window.uploadReportV16;
  if(typeof oldUpload==='function'&&!oldUpload.__finalUserFix){
    window.uploadReportV16=async function(rowId,file){
      let target=Number(rowId); const rows=window.DATA||[];
      if(!rows.some(r=>Number(r.No)===target)){
        const modal=$('reportModal');const modalId=Number(modal?.dataset?.itemId||0);if(rows.some(r=>Number(r.No)===modalId))target=modalId;
      }
      if(!rows.some(r=>Number(r.No)===target)){
        const rr=rows.find(r=>String(r['Report No']||'').trim()===String(rowId||'').trim());if(rr)target=Number(rr.No);
      }
      if(!rows.some(r=>Number(r.No)===target)){
        const {data}=await supabaseClient.from('reliability_tests').select('*').eq('id',target).maybeSingle();
        if(data){rows.push(mapDbRow(data));}
      }
      return oldUpload(target,file);
    };
    window.uploadReportV16.__finalUserFix=true;
  }

  const obs=new MutationObserver(()=>{translateDom();paginateMaterial();});
  obs.observe(document.body,{subtree:true,childList:true});
  document.addEventListener('click',e=>{if(e.target.closest('.nav button,.langs button'))setTimeout(()=>{translateDom();paginateMaterial();},150)},true);
  setTimeout(()=>{translateDom();paginateMaterial();},200);
  setTimeout(()=>{translateDom();paginateMaterial();},1200);
})();
</script>
'''
s=s.replace('</body>',patch+'</body>')
p.write_text(s,encoding='utf-8')
print('final user fix applied',len(s))
