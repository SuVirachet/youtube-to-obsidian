# Path B — ดึง transcript คลิป member-only ผ่าน Claude-in-Chrome

ใช้เมื่อคลิปเป็น member-only และ yt-dlp/cookie ใช้ไม่ได้ (Chrome App-Bound Encryption → `Failed to decrypt with DPAPI`)

**หลักการ:** browser ที่ login สมาชิกอยู่ มองเห็นคลิปได้แล้ว — เราแค่ "ดักจับ" caption track ที่ player โหลดเอง (player มี proof-of-origin token ที่ถูกต้อง ซึ่งสร้างเองจากนอก browser ไม่ได้)

> ทำไมไม่ใช้วิธีอื่น: (1) `--cookies-from-browser` → Chrome ABE decrypt ไม่ได้ (2) fetch caption `baseUrl` ตรงๆ → body ว่าง (3) return URL caption ผ่าน javascript_tool → extension บล็อก `[BLOCKED]`

**ปรัชญา flow นี้: browser ทำให้น้อยที่สุด** — แค่ดักจับ + **download raw json3** แล้วให้ `scripts/format_transcript.py` (เทสต์แล้ว) จัดการ parse/format/frontmatter ทั้งหมด → ไม่ต้องพิมพ์ JS parser ยาวๆ ทุกครั้ง (เสี่ยง bug)

เครื่องมือ (โหลดผ่าน ToolSearch ถ้ายังไม่มี): `mcp__Claude_in_Chrome__{list_connected_browsers, select_browser, tabs_context_mcp, navigate, javascript_tool, computer, browser_batch}`

---

## ขั้นตอน (6 step)

### 1. เชื่อม browser
`list_connected_browsers()` → ถ้าได้ `[]` ขอให้ผู้ใช้เปิด **side panel "Claude" extension** (ไอคอน ✳️ บน toolbar) เพื่อ re-pair → ลองใหม่ · ได้ deviceId → `select_browser(deviceId)`

### 2. เปิดหน้าคลิป
`tabs_context_mcp(createIfEmpty:true)` → `navigate(url, tabId)` → wait ~5s · ยืนยัน title ตรง (session สมาชิกผ่านเลย)

### 3. inject hook (JS ก้อนเดียว — ดักจับ timedtext)
```js
(() => {
  window.__cap = window.__cap || [];
  if (!window.__hk) {
    const of = window.fetch;
    window.fetch = async function(...a){ const r = await of.apply(this,a);
      try{ const u = typeof a[0]==='string'?a[0]:(a[0]&&a[0].url);
        if(u&&u.includes('timedtext')) r.clone().text().then(t=>window.__cap.push(t)); }catch(e){}
      return r; };
    const X=window.XMLHttpRequest, oo=X.prototype.open, os=X.prototype.send;
    X.prototype.open=function(m,u){ this.__u=u; return oo.apply(this,arguments); };
    X.prototype.send=function(){ this.addEventListener('load',function(){ try{ if(this.__u&&(''+this.__u).includes('timedtext')) window.__cap.push(this.responseText); }catch(e){} }); return os.apply(this,arguments); };
    window.__hk=1;
  }
  return JSON.stringify({hooked:1});
})()
```

### 4. เปิด CC + ดึง metadata/chapters (browser_batch + JS)
เปิด CC:
```
browser_batch([
  {name:'computer', input:{action:'left_click', coordinate:[600,330], tabId}},
  {name:'computer', input:{action:'key', text:'c', tabId}},
  {name:'computer', input:{action:'wait', duration:3, tabId}}
])
```
แล้วดึง metadata + chapters จาก description ในทีเดียว:
```js
(() => {
  const mp=document.getElementById('movie_player');
  const pr=(mp&&mp.getPlayerResponse&&mp.getPlayerResponse())||{};
  const vd=pr.videoDetails||{};
  const chaps=[];
  for(const l of ((vd.shortDescription||'').split('\n'))){
    const m=l.match(/^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s*[-–—:.)]*\s*(.+?)\s*$/);
    if(m&&m[2]&&m[2].length<80){ const p=m[1].split(':').map(Number); const sec=p.length===3?p[0]*3600+p[1]*60+p[2]:p[0]*60+p[1]; chaps.push([sec,m[2]]); }
  }
  return JSON.stringify({captured:(window.__cap||[]).map(x=>x.length), title:vd.title, id:vd.videoId, lengthSec:vd.lengthSeconds, author:vd.author, chapters:chaps});
})()
```
- `captured` ควรมีตัวเลขหลักแสน = json3 จับได้ · เก็บ chapters (`[[sec,name]]`) ไว้ส่ง script
- ⚠️ **ถ้า `captured: []`** = caption ยังไม่ติด (เจอบ่อยตอนเพิ่ง navigate — `c` ไม่เข้าเพราะ player ยังไม่ focus/วิดีโอไม่เล่น) → แก้: **สั่งวิดีโอเล่นก่อน** (`movie_player.playVideo()`) แล้ว **คลิก player + กด `c` ซ้ำ** → เช็คว่า `document.querySelector('.ytp-subtitles-button').getAttribute('aria-pressed')==='true'` และ `captured` มีค่า **ก่อนไป step 5** (อย่า download ตอน captured ว่าง)

### 5. download raw json3 (JS เล็ก — ไม่ parse)
```js
(() => {
  const body=(window.__cap||[]).sort((a,b)=>b.length-a.length)[0]||'';
  const b=new Blob([body],{type:'application/json'}), u=URL.createObjectURL(b);
  const a=document.createElement('a'); a.href=u; a.download='yt-cap.json3';
  document.body.appendChild(a); a.click(); setTimeout(()=>{a.remove();URL.revokeObjectURL(u);},1500);
  return JSON.stringify({len:body.length});
})()
```
> ⚠️ Chrome บล็อกโหลดไฟล์ที่ 2/หน้า → ถ้าต้องโหลดซ้ำใช้ชื่อใหม่ · เลี่ยง clipper/clipboard API (focus ค้าง)

### 6. format + เขียนลง vault (Python — formatter ร่วม)
```bash
python <skill>/scripts/format_transcript.py "$DOWNLOADS_DIR/yt-cap.json3" \
  --url "<url>" --id "<id>" --title "<title>" --channel "<channel>" \
  --duration "<Xm YYs>" --source youtube-membership \
  --fetch-method "caption-capture (th-asr via Claude-in-Chrome)" \
  --chapters '[[0,"intro"],[52,"GOAL"], ...]' \
  --distill "[[<ชื่อโน้ต distill ที่จะสร้าง>]]"
```
→ เขียน `_archive/conversations-raw/youtube/<title> — transcript.md` (Gemma format + frontmatter) เสร็จในคำสั่งเดียว · เนื้อหาไม่ผ่าน context

> ถ้าคลิปไม่มี chapter ในคำบรรยาย → ส่ง `--chapters '[]'` (ได้แค่ `M:SS · ` ย่อหน้า ไม่มี ### header)

---

## ⚠️ Gotchas ตอนสั่งวิดีโอเล่น (ใช้ทั้งตอนเปิด CC และตอน capture ภาพ)
- **วิดีโอ stall `buffered: 0` (autoplay ถูกบล็อก)** — Chrome บล็อก autoplay ที่มีเสียง → `playVideo()` ไม่ขยับ buffer · **แก้: mute ก่อนเล่น** `const v=document.querySelector('video'); v.muted=true; v.play();` → buffer เดินทันที (มี user gesture จาก `c`/click อยู่แล้วก็ช่วย)
- **"เฟรมค้าง" ตอน capture ภาพใน background tab** — `drawImage(video)` คืนเฟรมเก่าทั้งที่ `currentTime` เดิน (tab โดน throttle, `requestVideoFrameCallback` ไม่ยิง) · **แก้: ใน `browser_batch` เดียว ใส่ `computer screenshot` ก่อน `drawImage` ทันที** (screenshot บังคับ paint เฟรมสด) · รายละเอียดเต็มใน `references/distill-and-timestamps.md` ส่วน 🖼️ ภาพประกอบ
