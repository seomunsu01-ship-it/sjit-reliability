const express = require('express');
const multer = require('multer');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;
const ROOT = __dirname;
const DATA = path.join(ROOT, 'data');
const JSON_FILE = path.join(DATA, 'voc-data.json');
const ORIGINAL_FILE = path.join(DATA, 'original.xlsx');
fs.mkdirSync(DATA, { recursive: true });
app.use(cors());
app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(ROOT, 'public')));
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 50 * 1024 * 1024 } });
function normalize(v) {
  if (v === null || v === undefined) return '';
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  return String(v).trim();
}
function parseExcel(buf) {
  const wb = XLSX.read(buf, { cellDates: true });
  let sheetName = wb.SheetNames.find(n => String(n).trim().toLowerCase() === 'voc list');
  if (!sheetName) {
    sheetName = wb.SheetNames.find(n => {
      const testRows = XLSX.utils.sheet_to_json(wb.Sheets[n], { header: 1, defval: '', raw: true }).slice(0, 15);
      return testRows.some(r => r.some(v => normalize(v).toLowerCase() === 'voc no'));
    });
  }
  if (!sheetName) sheetName = wb.SheetNames[0];
  const ws = wb.Sheets[sheetName];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '', raw: true });
  if (!rows.length) return { columns: [], data: [], updatedAt: new Date().toISOString(), sheet: sheetName };
  const headerIndex = rows.findIndex(r => r.some(v => normalize(v).toLowerCase() === 'voc no'));
  const headerRow = headerIndex >= 0 ? headerIndex : 0;
  const columns = rows[headerRow].map((x, i) => normalize(x) || `Column ${i + 1}`);
  const vocNoIndex = columns.findIndex(c => normalize(c).toLowerCase() === 'voc no');
  const data = rows.slice(headerRow + 1)
    .filter(r => vocNoIndex < 0 || normalize(r[vocNoIndex]) !== '')
    .map((r, idx) => {
      const o = { _row: idx + headerRow + 2 };
      columns.forEach((c, i) => { o[c] = normalize(r[i]); });
      return o;
    });
  return { columns, data, updatedAt: new Date().toISOString(), sheet: sheetName };
}
function load() {
  try { return JSON.parse(fs.readFileSync(JSON_FILE, 'utf8')); }
  catch (_) { return { columns: [], data: [], updatedAt: null, sheet: null }; }
}
app.get('/api/status', (req, res) => { const d = load(); res.json({ ok: true, count: d.data.length, updatedAt: d.updatedAt, sheet: d.sheet, columns: d.columns }); });
app.get('/api/voc', (req, res) => res.json(load()));
app.post('/api/upload', upload.single('file'), (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ ok: false, message: 'Excel 파일이 없습니다.' });
    const parsed = parseExcel(req.file.buffer);
    fs.writeFileSync(JSON_FILE, JSON.stringify(parsed, null, 2), 'utf8');
    fs.writeFileSync(ORIGINAL_FILE, req.file.buffer);
    res.json({ ok: true, count: parsed.data.length, updatedAt: parsed.updatedAt, sheet: parsed.sheet, columns: parsed.columns });
  } catch (e) { res.status(500).json({ ok: false, message: e.message }); }
});
app.get('/api/download/original', (req, res) => { if (!fs.existsSync(ORIGINAL_FILE)) return res.status(404).send('원본 Excel이 아직 없습니다.'); res.download(ORIGINAL_FILE, 'SJIT_VINA_VOC_original.xlsx'); });
app.get('/api/download/current', (req, res) => {
  try {
    const d = load(); const wb = XLSX.utils.book_new();
    const rows = [d.columns, ...d.data.map(o => d.columns.map(c => o[c] ?? ''))];
    const ws = XLSX.utils.aoa_to_sheet(rows); XLSX.utils.book_append_sheet(wb, ws, 'VOC list');
    const buf = XLSX.write(wb, { type: 'buffer', bookType: 'xlsx' });
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', 'attachment; filename="SJIT_VINA_VOC_current.xlsx"'); res.send(buf);
  } catch (e) { res.status(500).send(e.message); }
});
app.use((req, res) => res.sendFile(path.join(ROOT, 'public', 'index.html')));
app.listen(PORT, '0.0.0.0', () => console.log(`SJIT VINA VOC server running on ${PORT}`));
