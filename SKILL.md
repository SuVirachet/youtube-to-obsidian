---
name: youtube-to-obsidian
description: >-
  ดึง transcript จากคลิป YouTube (ทั้ง public และ member-only "เฉพาะสมาชิก") เข้า Obsidian vault นี้
  แล้ว distill เป็นโน้ต concept ในโดเมนที่เหมาะ พร้อม clickable timestamp links + ภาพประกอบจากวิดีโอ.
  ใช้ skill นี้ทุกครั้งที่ผู้ใช้อยากเอาคลิป/วิดีโอ/lesson/talk จาก YouTube ลง Obsidian หรือ vault —
  รวมถึงวลีอย่าง "ดึงคลิป", "เอา youtube ลง obsidian", "transcript คลิปนี้", "distill คลิป",
  "สรุปคลิปนี้ลง vault", หรือเมื่อผู้ใช้วางลิงก์ youtube.com / youtu.be พร้อมเจตนาจะเก็บ/สรุป.
  จัดการคลิป member-only ผ่าน Claude-in-Chrome extension เมื่อ download ปกติโดนบล็อก (cookie/ABE).
  Make sure to use this skill even when the user doesn't say the word "skill" or "transcript" —
  any intent to capture, save, summarize, or take notes from a YouTube video belongs here.
---

# YouTube → Obsidian

ดึงคลิป YouTube → transcript ดิบ (timestamp + chapter) ใน archive → distill เป็นโน้ต concept **แน่น** ในโดเมน + timestamp links + **ภาพประกอบ HD** จากวิดีโอ

**ปรัชญา vault: "AI distill, user refine"** — เก็บ transcript ดิบเป็น source of truth เสมอ (อย่าแก้) แล้ว distill โน้ตที่ผู้ใช้มา refine ต่อ · **"refine" = เติม Insight/เลือกโดเมน ไม่ใช่มาเติมเนื้อที่ AI ควรเก็บครบตั้งแต่แรก**

## 🎯 Definition of Done — มาตรฐานขั้นต่ำ (ทุกข้อต้องผ่าน)
> นี่คือ baseline ที่ skill นี้ต้องทำได้เองโดยไม่ต้องให้ user แก้ — เช็คก่อนบอกว่าเสร็จ

1. **Transcript ดิบ** อยู่ใน `_archive/conversations-raw/youtube/` format Gemma (`## บทต่างๆ` + `## Transcript` + `### chapter` + `M:SS · `)
2. **โน้ต distill แน่น ~80%+** ของคลิป — named entity ทุกตัว (ทำตาราง roster), ตัวอย่างรูปธรรม, ตัวเลข, why, ข้อเสีย/คำเตือน · ยาว 150-250 บรรทัดปกติ (ดู `references/distill-and-timestamps.md` กฎความแน่น)
3. **timestamp links คลิกได้** ตามหัวข้อ/จุดสำคัญ (`[▸ M:SS](url&t=Ns)`) — timing จริงจาก transcript
4. **คลิป visual-heavy → ภาพประกอบ HD** (1920×1080) ~1 ภาพ/หัวข้อหลัก · **วิเคราะห์เนื้อหา + เฟรมต้องแสดง diagram ครบทั้งอัน (ไม่ใช่ส่วนเสี้ยว)** · embed + caption + Read ภาพยืนยัน
5. **ลิงก์สองทาง** transcript ↔ distill (`clip_source` ↔ `Distilled:`)
6. **รายงานเป็นเฟส** ให้ user เห็นความคืบหน้า

---

## STEP 0 — Triage
คลิป public หรือ **member-only** ("เฉพาะสมาชิก")? · ไม่แน่ใจ → ลอง Path A ก่อน เด้ง `available to channel's members` = member → Path B

## STEP 1 — ดึง + format transcript (จบในคำสั่งเดียวทั้ง 2 path)

**Path A (PUBLIC):**
```bash
python <skill>/scripts/fetch_public.py "<URL>" --distill "[[<ชื่อโน้ต distill ที่จะสร้าง>]]"
```
ทำครบ: metadata + chapters อัตโนมัติ → caption(vtt)/Whisper → Gemma format + frontmatter → archive

**Path B (MEMBER-ONLY)** — cookie ใช้ไม่ได้ (Chrome ABE) → ดักจับ caption ที่ player โหลดผ่าน Claude-in-Chrome · **อ่าน `references/member-capture.md` (6 step + JS templates)** สรุป:
1. `list_connected_browsers`→`select_browser` (ว่าง: ให้ user เปิด side panel Claude extension)
2. `navigate` ไปคลิป → 3. inject hook ดักจับ `timedtext` → 4. กด `c` เปิด CC + ดึง metadata/chapters → 5. download raw json3 → 6. `format_transcript.py <json3> --chapters '...' --title '...' ...`
> gotchas: อย่า return URL caption (โดนบล็อก) · fetch baseUrl = body ว่าง · Chrome บล็อกโหลดไฟล์ที่ 2/หน้า (ชื่อไม่ซ้ำ) · **ถ้า `captured:[]` = `c` ไม่ติด** → playVideo ก่อน + คลิก player + กด `c` ซ้ำ + เช็ค aria-pressed ก่อน download

→ ได้ `_archive/conversations-raw/youtube/<title> — transcript.md` (= STEP 2 รวมในนี้แล้ว)

## STEP 3 — Distill (แน่น) + timestamp links
1. **ถาม user ก่อนว่าลงโดเมนไหน** (`50_dev/`, `20_trading/`, ...) — judgment ของ user อย่าเดา
2. **อ่าน transcript ครบทุกหน้า** (Read หลาย offset ถ้า >25k tokens) → เขียนตาม template + **กฎความแน่น** (`references/distill-and-timestamps.md`)
3. **timestamp links** ตามหัวข้อ — grep transcript หาวลีที่ตรงกับหัวข้อเพื่อหา timing จริง (อย่าเดา)

## STEP 4 — ภาพประกอบ (คลิป visual-heavy: diagram/dashboard/ภาพระบบ)
> **บังคับทำถ้าคลิปมีภาพสำคัญ** (user reject โน้ตที่ไม่มีภาพ + โน้ตที่ภาพไม่ครบ) · ทำเมื่อ browser เปิดคลิปอยู่ (Path B หรือ user เปิดไว้)

ทำตาม `references/distill-and-timestamps.md` ส่วน "🖼️ ภาพประกอบ" — แกน:
1. **บังคับ 1080p ก่อน** (`setPlaybackQualityRange('hd1080')` + รอ `videoWidth==1920`) ไม่งั้นได้ 480p เบลอ
2. **วิเคราะห์**: แต่ละหัวข้อต้องการภาพอะไร → scout หลายเฟรม → เลือก **เฟรม zoom-to-fit เห็น diagram ครบทั้งอัน** (ไม่ใช่ที่ผู้พูด zoom เข้าส่วนเดียว)
3. capture canvas→PNG → `python <skill>/scripts/prepare_images.py ltd-X=hd-X.png ...` (ย้าย + **verify HD อัตโนมัติ**)
4. embed `![[...]]` + caption + timestamp ตรงหัวข้อ → **Read ภาพกลับมาดูยืนยันครบ+คม+ตรงเนื้อหา**

---

## Scripts (bundled)
- `scripts/fetch_public.py` — Path A: public → Gemma transcript ใน archive (คำสั่งเดียว, chapters อัตโนมัติ, Whisper fallback)
- `scripts/format_transcript.py` — **formatter ร่วม** (json3/vtt/srt/cues → Gemma + frontmatter → archive) ทั้ง 2 path เรียกตัวนี้
- `scripts/prepare_images.py` — ย้ายภาพ Downloads→`_attachments` + **verify HD** (เตือนถ้า <1900px = เบลอ ต้อง re-capture)

## Reference files
- `references/member-capture.md` — Path B 6 step + JS templates
- `references/distill-and-timestamps.md` — กฎความแน่น distill + timestamp links + **กฎเหล็กของภาพ** (วิเคราะห์เนื้อหา/ครบทั้งอัน/HD/verify)
- `references/transcript-format.md` — สเปก Gemma format
- `references/setup.md` — ติดตั้ง + แก้ Norton SSL + known issues

## Prerequisites
`python -m yt_dlp` · `faster-whisper` · `imageio-ffmpeg` · `certifi` (ลงแล้ว) · **AV SSL fix** ถ้าเจอ `CERTIFICATE_VERIFY_FAILED` (ดู setup.md) · Path B ต้องเปิด side panel Claude extension
