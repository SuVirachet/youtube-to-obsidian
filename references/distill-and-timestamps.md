# Distill → โน้ต concept + timestamp links

## ⚠️⚠️ กฎเหล็ก: distill ต้อง "แน่น" ไม่ใช่ "บาง"

**ความผิดพลาดที่เจอบ่อยสุด = distill ได้แค่ concept ระดับบน ทิ้งรายละเอียด 70%** (user เคย reject เพราะ "ได้แค่ 20-30%")

เป้าหมาย: คนที่**ดูคลิปไม่ได้** อ่านโน้ตแล้วได้สาระ **~80%+** ของคลิป ไม่ใช่ outline บางๆ

ต้อง**เก็บให้ครบ** (สิ่งที่มักหล่น):
- **named entities ทุกตัว** — ชื่อ agent/สกิล/ไฟล์/เครื่องมือ + หน้าที่ของแต่ละตัว (อย่าสรุปรวบ "มีลูกทีมหลายคน" → ทำเป็น **ตาราง roster**)
- **ตัวอย่างรูปธรรมทุกอัน** — ผู้พูดยกตัวอย่างอะไร (เคสจริง, ตัวเลข, ชื่อหุ้น/บริษัท/คน) เก็บไว้ มันคือเนื้อ
- **เทคนิค/ขั้นตอนเฉพาะ** — ไม่ใช่แค่ "เขาใช้ index" แต่ index คืออะไร ทำไม ทำยังไง
- **why เบื้องหลังทุกอย่าง** — เหตุผลที่ผู้พูดทำแบบนั้น (เช่น "ทำ atom เพราะไฟล์ใหญ่ = noise + ช้า")
- **คำเตือน/ข้อยกเว้น/ข้อเสีย** ที่ผู้พูดพูด (garbage-in-garbage-out, switching cost, ฯลฯ)

จัดการความแน่นด้วย **ตาราง + bullet หนาแน่น + แบ่ง section ละเอียด** (โน้ตยาว 150-250 บรรทัดเป็นเรื่องปกติ ไม่ต้องกลัวยาว) — ความยาวไม่ใช่ปัญหา **การตกหล่นคือปัญหา**

วิธีกันหล่น: **ไล่ตาม chapter/section ของ transcript ทีละอัน** เก็บ point สำคัญของแต่ละ section ก่อนเขียน (อย่ากระโดดสรุปจากความจำหลังอ่านผ่านๆ)

## ก่อนเริ่ม
- **ถามผู้ใช้ว่าจะลงโดเมนไหน** (`50_dev/`, `20_trading/`, `10_dharma/`, `70_astrology/...`) — การเลือกโดเมน + ความลึกคือ judgment ของผู้ใช้ อย่าเดา
- **อ่าน transcript ให้ครบทุกหน้า** (ไฟล์ยาวอาจ >25k tokens → Read หลายรอบ/ทุก offset) — อย่า distill จากหน้าแรกหน้าเดียว
- ดูโน้ต distill ที่มีอยู่ในโดเมนนั้นเป็นตัวอย่าง (เช่น `50_dev/Knowledge Base — ทำไมต้องมี + วิธีเริ่ม (ลงทุน Diary).md` = ตัวอย่างความแน่นที่ดี) เพื่อ match สไตล์ + หา `[[...]]` ที่เชื่อมได้

## โครงโน้ต concept (อิง template `_templates/T_concept.md` + ตัวอย่างจริงใน vault)

```markdown
---
type: concept
domain: <dev|trading|...>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
status: ai-distilled
source: youtube-clip
clip_source: "[[<ชื่อ transcript ดิบ>]]"
youtube_url: <url>
author: <ช่อง>
published: <YYYY-MM-DD>
tags: [#ai-generated, #status/distilled, #needs-refine, #youtube]
---

# <หัวข้อโน้ต>

> 🤖 **AI distilled** จาก transcript เต็ม · confidence: <สูง/กลาง> + เหตุผลสั้นๆ

## 🎯 Core idea (ในประโยคเดียว)
> ...

## <เนื้อหาแบ่งตามหัวข้อหลัก>     ← ใส่ timestamp link ที่หัวข้อ (ดูล่าง)
...

## 💡 Insight (เขียนเอง — หลังลองทำ)
- *(เว้นให้ผู้ใช้เติม + seed คำถาม/มุมที่เชื่อมกับงานของผู้ใช้)*

## 🔗 เชื่อมกับอะไร
- [[...]] เยอะๆ จัดกลุ่มตามแกน + cross-domain (ลิงก์ liberally แม้โน้ตปลายทางยังไม่มี)

## 📂 อ้างอิง
- YouTube url, transcript ดิบ [[...]], web-clipper [[...]], ผู้สร้าง
```

หลักการ: เนื้อหาแน่นแต่ไม่ลอกทั้ง transcript · ดึง concept/pattern/ตัวอย่าง · เว้น 💡 Insight ให้ผู้ใช้ refine (paradigm "AI distill, user refine") · ลิงก์ `[[...]]` เยอะ

## Timestamp links (คลิกแล้วกระโดดวิดีโอ)

ใส่ที่หัวข้อ + จุดสำคัญ เป็น markdown link ไปยัง YouTube พร้อม `&t=<วินาที>s`:
```
## <หัวข้อ> · [▸ M:SS](<youtube_url>&t=<วินาที>s)
```
- ตารางคำสั่ง/เทคนิค: เพิ่มคอลัมน์ `⏱️` ใส่ `[M:SS](url&t=Ns)` ต่อแถว
- ตามจุดย่อย: ต่อท้ายบรรทัด `... [▸ M:SS](url&t=Ns)`

**หา timestamp จริง (อย่าเดา)** — grep transcript หาวลีที่ตรงกับหัวข้อ แล้วอ่าน `M:SS · ` ที่ต้นย่อหน้านั้น:
```python
import re, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8")
p = pathlib.Path(r"...<transcript>.md")
paras = [(m.group(1), l) for l in p.read_text(encoding="utf-8").splitlines()
         if (m:=re.match(r'^(\d+:\d\d) · ', l))]
anchors = [("หัวข้อ A","วลีค้นในย่อหน้า"), ("หัวข้อ B","อีกวลี")]
for label, needle in anchors:
    ts = next((t for t,txt in paras if needle in txt), None)
    print(f"{ts or '--':>6}  {label}")
```
แปลง `M:SS` → วินาที (`m*60+s`) ใส่ใน `&t=Ns`

## 🖼️ ภาพประกอบ (สำหรับคลิปที่มี diagram/dashboard/ภาพระบบ)

คลิปสายเทคนิคหลายอันมี **diagram/screenshot สำคัญ** ที่ transcript จับไม่ได้ — ถ้าคลิป visual-heavy **ต้อง capture ภาพมา embed ด้วย** (user เคย feedback ว่า "ขาดภาพประกอบ") · ทำได้เมื่อ browser เปิดคลิปอยู่ (Path B หรือ user เปิดไว้):

0. **⚠️ บังคับ 1080p ก่อน (สำคัญสุด — ไม่งั้นได้ภาพเบลอ ตัวอักษรอ่านไม่ออก)**: ค่า default มัก 480p → canvas จะได้แค่ 854×480 · ตั้ง hd แล้วเล่นให้ buffer จน `video.videoWidth==1920`:
   ```js
   const mp=document.getElementById('movie_player');
   const best=mp.getAvailableQualityLevels().filter(l=>l!=='auto')[0];  // เช่น 'hd1080'
   mp.setPlaybackQualityRange(best,best); mp.playVideo();
   // รอ ~4 วิ แล้วเช็ค document.querySelector('video').videoWidth === 1920 ก่อนไปต่อ
   ```
1. **หาเฟรมสำคัญ**: seek ไป timestamp ที่ diagram โชว์ชัด แล้ว screenshot ดู (scout ก่อน อย่าเพิ่ง capture) — หลัง seek ให้ play ~3 วิ buffer HD ที่จุดนั้นก่อน (re-assert `setPlaybackQualityRange` หลัง seek กัน quality ตก) แล้วค่อย pause
   ```js
   document.getElementById('movie_player').seekTo(<sec>, true);
   ```
2. **capture เฟรมตรงๆ ผ่าน canvas → PNG** (สะอาด ไม่มีขอบเบราว์เซอร์ ไม่ติด CORS) — เช็ค `videoWidth>=1900` ก่อน capture:
   ```js
   const v=document.querySelector('video'); const c=document.createElement('canvas');
   c.width=v.videoWidth; c.height=v.videoHeight; c.getContext('2d').drawImage(v,0,0,c.width,c.height);
   const a=document.createElement('a'); a.href=c.toDataURL('image/png'); a.download='kb-x.png';
   document.body.appendChild(a); a.click();
   ```
   **⚠️⚠️ กับดักร้ายแรง: "เฟรมค้าง" ใน background tab (เสียเวลานานมากถ้าไม่รู้)** — ถ้า YouTube tab ไม่ใช่ tab ที่ active/มองเห็นอยู่ เบราว์เซอร์จะ **throttle การ present เฟรม**: `video.currentTime` เดินไปเรื่อยๆ แต่ `drawImage(video)` คืน **เฟรมเก่าค้าง** (decode ล่าสุดก่อน throttle) → ได้ภาพผิดหัวข้อ! อันตรายเพราะ **`computer screenshot` บังคับ paint เลยเห็นเฟรมสด** ทำให้เข้าใจผิดว่า capture ถูก แต่ไฟล์ที่ download เป็นเฟรมเก่า · diagnostic: `video.requestVideoFrameCallback` **ไม่ยิงเลย** = ยืนยันโดน throttle
   - **วิธีแก้ที่ใช้ได้จริง (proven)**: ใน `browser_batch` เดียว เรียง action ให้ **`computer screenshot` มาก่อน `drawImage` ทันที** — screenshot บังคับ paint เฟรมสด แล้ว drawImage ตัวถัดไปจะได้เฟรมนั้น (อย่า `pause` ก่อน draw — ปล่อยเล่นค้างไว้): `[seek+play] → [wait 5s] → [computer screenshot] → [drawImage+download]`
   - ทุกครั้งหลังย้ายไฟล์ **Read ภาพกลับมาดูเสมอ** ว่าตรงหัวข้อจริง (เฟรมค้างจะดูเนียนจนกว่าจะเปิดดู)
3. ย้ายไฟล์ `Downloads/*.png` → `_attachments/` (ตั้งชื่อสื่อความหมาย เช่น `ltd-kb-master-index.png`)
4. **embed ในโน้ต** ตรงหัวข้อที่เกี่ยว + caption + timestamp link:
   ```markdown
   ![[ltd-kb-master-index.png]]
   > *คำอธิบายภาพ [▸ M:SS](url&t=Ns)*
   ```
> **⚠️ จำนวนภาพ — อย่าขี้เหนียว (user เคย reject "3 ภาพน้อยไป" สำหรับคลิป 34 บท)**: เล็ง **1 ภาพต่อทุกหัวข้อ/feature ที่มีการสาธิตบนจอจริง** ไม่ใช่แค่ 2-3 จุดเด่น · คลิป tutorial feature-rich (Obsidian/สาธิตระบบ) ปกติ **8-12 ภาพ** เป็นเรื่องธรรมดา — ไล่ตามสารบัญ: แต่ละ feature ที่ผู้พูดโชว์หน้าจอ (link, theme, shortcuts, media, graph, canvas, ทำงานกับ AI, ...) ควรมีภาพคู่กับหัวข้อนั้น · เลือกเฟรมที่มีคุณค่า (diagram, dashboard, ไฟล์จริง, ผลลัพธ์ที่ AI ทำ) ข้ามเฉพาะหัวข้อที่เป็นการพูดล้วนไม่มีภาพ

### ⚠️⚠️ กฎเหล็กของภาพ: ต้อง "วิเคราะห์เนื้อหา" + capture เฟรมที่แสดงแนวคิด **ครบทั้งหมด** (ไม่ใช่ส่วนเสี้ยว)
> **ความผิดพลาดที่เจอจริง (user reject): capture แบบกลไก** — seek ไป timestamp แล้วกดเฟรมเลย โดยไม่ดูว่าเฟรมนั้นแสดงแนวคิด**ครบ**ไหม → ได้ diagram แค่ส่วนเดียว (เช่น flywheel ที่ zoom เข้ามุมเดียว แทนที่จะเป็นวงเต็ม)

ทำให้ถูก:
1. **เข้าใจก่อนว่าแต่ละหัวข้อต้องการภาพอะไร** แล้วหาเฟรมที่ตรง + ครบ (diagram ทั้งอัน, dashboard เต็มจอ, ไฟล์ที่เห็นโครงครบ)
2. **diagram ในวิดีโอมักถูก zoom/pan หลายระดับ** — scout หลายเฟรม (ก่อน/หลัง/zoom ต่างกัน) แล้วเลือก **เฟรมที่ zoom-to-fit เห็นทั้ง diagram** ไม่ใช่เฟรมที่ผู้พูด zoom เข้าไปดูส่วนเดียว · มักอยู่ตอนเขา**เพิ่งเปิด diagram** หรือ**ตอนสรุป** (zoom ออก)
3. **เช็คความสัมพันธ์ภาพ↔เนื้อหา**: ภาพต้อง "เสริม/ยืนยัน" สิ่งที่เขียนในหัวข้อนั้นจริงๆ — ถ้าภาพไม่ตรงหัวข้อ/ไม่ครบ อย่าใส่
4. **หลัง capture ให้ Read ภาพกลับมาดู** ว่าคม + ครบ + ตรงเนื้อหา ก่อนยืนยัน (อย่าเชื่อแค่ว่า download สำเร็จ)

## เสร็จแล้ว
- ลิงก์ transcript ดิบกับโน้ต distill ทั้งสองทาง (`clip_source` ↔ `Distilled:`)
- ถ้าคลิป visual-heavy: **embed diagram/screenshot สำคัญ** (อย่าลืม — เป็น feedback ที่ user ให้ความสำคัญ)
- บอกผู้ใช้ว่าได้ไฟล์อะไรบ้าง + เตือนว่า 💡 Insight เว้นไว้ให้ refine
