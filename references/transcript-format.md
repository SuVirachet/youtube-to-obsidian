# Transcript format มาตรฐานของ vault (อ้างอิง)

> **logic จริงอยู่ใน `scripts/format_transcript.py`** (เทสต์แล้ว) — ไฟล์นี้แค่อธิบายสเปกให้เข้าใจ ไม่ต้อง implement เอง

ผู้ใช้ต้องการให้ transcript YouTube ทุกอันหน้าตาเหมือนโน้ต web-clipper เดิม (อ้างอิง: คลิป "Gemma 4 12B" ของช่อง 2noobs)

```markdown
## บทต่างๆ (Chapters)

00:00 - <ชื่อบท>          ← MM:SS - name (มี leading zero, คั่นด้วย " - ")
03:58 - <ชื่อบท>

## Transcript

### <ชื่อบท>               ← chapter เป็น ### header ชื่อเฉยๆ (ไม่มี timestamp ในหัวข้อ)

0:00 · <ย่อหน้า>          ← M:SS · text (ไม่มี leading zero, จุดกลาง · , ไม่ตัวหนา)
0:25 · <ย่อหน้า>          ← จัดกลุ่ม caption cue ทุก ~20 วินาทีต่อย่อหน้า
```

**กฎ (script จัดการให้):**
- chapter list บน: `MM:SS - ชื่อ` · chapter section: `### ชื่อบท` · ย่อหน้า: `M:SS · ข้อความ` (middot)
- จัดกลุ่ม cue จนครบ ~20 วิ แล้วขึ้นย่อหน้าใหม่ + ขึ้นใหม่ทุกครั้งที่ข้าม chapter
- timestamp = start ของ cue แรกในย่อหน้า (ของจริง) · dedupe บรรทัดซ้ำติดกัน
- **ห้าม** `**[MM:00]**` แบบ bold ต่อนาที (ผู้ใช้ไม่เอา)

## วิธีใช้ formatter

```bash
python <skill>/scripts/format_transcript.py <caption_file> \
  --url URL --id ID --title TITLE --channel CH --duration "Xm YYs" \
  --source {youtube|youtube-membership} --fetch-method "..." \
  --chapters '[[0,"intro"],[52,"GOAL"]]' --distill "[[ชื่อโน้ต distill]]"
```
- `caption_file`: `.json3` (Path B), `.vtt`/`.srt` (Path A), `.json` (cues `[[sec,text]]` จาก Whisper)
- chapters: JSON `[[วินาที,"ชื่อ"]]` (ไม่มีก็ส่ง `[]`)
- เขียนลง `_archive/conversations-raw/youtube/<title> — transcript.md` อัตโนมัติ (frontmatter + body)
- importable ด้วย: `parse_any()`, `cues_to_body()`, `build_note()`, `write_note()` (fetch_public.py ใช้แบบนี้)
