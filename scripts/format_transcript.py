"""Universal YouTube-caption → Obsidian transcript formatter (single source of truth).

รับ caption ได้หลายแบบ → จัดเป็น Gemma format (## บทต่างๆ / ## Transcript / ### chapter /
`M:SS · ` ย่อหน้าทุก ~20 วิ) → ห่อ frontmatter → เขียนลง _archive/conversations-raw/youtube/

ใช้ได้ทั้ง Path A (public, vtt/srt) และ Path B (member, json3 ที่ดักจับจาก browser)
และ Whisper (cues.json = [[startSec, text], ...]).

CLI:
  python format_transcript.py <caption_file> \
      --url URL --id VIDEO_ID --title TITLE --channel CHANNEL \
      --duration 35m38s --source youtube-membership \
      --fetch-method "caption-capture (th-asr via Claude-in-Chrome)" \
      --chapters '[[0,"intro"],[52,"GOAL"]]' \
      [--distill "[[ชื่อโน้ต distill]]"] [--print-path]

  caption_file นามสกุล: .json3 (timedtext json3) | .vtt | .srt | .json (cues [[sec,text]])

Importable: parse_any(), cues_to_body(), build_note(), write_note()
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# Windows console เป็น cp1252 → กันพิมพ์ไทยพัง
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config  # vault paths from OBSIDIAN_VAULT env


# ---------- parsers: ทุกตัวคืน cues = list[(startSec:int, text:str)] ----------

def parse_json3(text):
    """YouTube timedtext json3 (events[].segs[].utf8 + tStartMs)."""
    data = json.loads(text)
    cues = []
    for ev in data.get("events", []):
        segs = ev.get("segs")
        if not segs:
            continue
        t = "".join(s.get("utf8", "") for s in segs)
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            cues.append((int(ev.get("tStartMs", 0)) // 1000, t))
    return cues


def _ts_to_sec(ts):
    ts = ts.replace(",", ".")
    parts = ts.split(":")
    parts = [float(p) for p in parts]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts[-3], parts[-2], parts[-1]
    return int(h * 3600 + m * 60 + s)


def parse_vtt(text):
    """WebVTT (รวม auto-caption ที่มี inline timing tags)."""
    cues, start = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if "-->" in line:
            start = _ts_to_sec(line.split("-->")[0].strip().split()[0])
            continue
        if (not line or line == "WEBVTT" or line.isdigit()
                or line.startswith(("Kind:", "Language:", "NOTE"))):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"&nbsp;", " ", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line and start is not None:
            cues.append((start, line))
    return cues


def parse_srt(text):
    return parse_vtt(text)  # โครงคล้ายกันพอใช้ตัวเดียวกันได้


def parse_cues_json(text):
    """[[startSec, text], ...] — สำหรับ Whisper segments หรือป้อนเอง."""
    return [(int(s), str(t).strip()) for s, t in json.loads(text) if str(t).strip()]


def parse_any(path: Path):
    raw = path.read_text(encoding="utf-8", errors="ignore")
    suf = path.suffix.lower()
    if suf == ".json3":
        return parse_json3(raw)
    if suf == ".vtt":
        return parse_vtt(raw)
    if suf == ".srt":
        return parse_srt(raw)
    if suf == ".json":
        # อาจเป็น json3 หรือ cues — เดาจากเนื้อ
        return parse_json3(raw) if '"events"' in raw[:200] else parse_cues_json(raw)
    # fallback: เดา json3
    return parse_json3(raw)


# ---------- formatter ----------

def _mmss(s):
    return f"{int(s) // 60:02d}:{int(s) % 60:02d}"


def _mss(s):
    return f"{int(s) // 60}:{int(s) % 60:02d}"


def cues_to_body(cues, chapters=None, group=20):
    """cues + chapters([[sec,name]]) → markdown body (Gemma format)."""
    chapters = sorted(chapters or [], key=lambda c: c[0])
    # dedupe บรรทัดซ้ำติดกัน
    clean, last = [], None
    for sec, t in cues:
        if t != last:
            clean.append((sec, t))
            last = t
    out = []
    if chapters:
        out.append("## บทต่างๆ (Chapters)\n")
        out += [f"{_mmss(t)} - {n}" for t, n in chapters]
        out.append("")
    out.append("## Transcript\n")
    ci, para, pstart = -1, [], None

    def flush():
        if para:
            out.append(f"{_mss(pstart)} · {' '.join(para)}")
            out.append("")
            para.clear()

    for sec, text in clean:
        nci = ci
        for k, (cs, _) in enumerate(chapters):
            if sec >= cs:
                nci = k
        if nci != ci:
            flush()
            out.append(f"### {chapters[nci][1]}\n")
            ci, pstart = nci, None
        if pstart is None:
            pstart = sec
        para.append(text)
        if sec - pstart >= group:
            flush()
            pstart = None
    flush()
    body = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def _safe(name):
    name = re.sub(r'[\\/:*?"<>|]', "", name)
    return re.sub(r"\s+", " ", name).strip()[:120] or "youtube"


def build_note(body, meta):
    distill = meta.get("distill") or "[[<ชื่อโน้ต distill>]]"
    title = meta.get("title", "untitled")
    fm = (
        "---\n"
        "type: youtube-transcript-raw\n"
        f"source: {meta.get('source', 'youtube')}\n"
        f"url: {meta.get('url', '')}\n"
        f"video_id: {meta.get('id', '')}\n"
        f"channel: {meta.get('channel', '')}\n"
        f'title: "{title}"\n'
        f"duration: {meta.get('duration', '')}\n"
        f"fetch_method: {meta.get('fetch_method', 'captions')}\n"
        f"date: {meta.get('date') or date.today().isoformat()}\n"
        "status: raw\n"
        "tags: [youtube, transcript, verbatim]\n"
        "---\n\n"
        f"# {title}\n\n"
        "> Verbatim transcript จับจากเซสชันที่ login อยู่. Raw capture — distill อย่าแก้ตรงนี้.\n"
        f"> Distilled: {distill}\n\n"
        f"{body}\n"
    )
    return fm


def write_note(body, meta):
    archive = config.archive()
    archive.mkdir(parents=True, exist_ok=True)
    out = archive / f"{_safe(meta.get('title', 'youtube'))} — transcript.md"
    out.write_text(build_note(body, meta), encoding="utf-8")
    return out


# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caption_file")
    ap.add_argument("--url", default="")
    ap.add_argument("--id", default="")
    ap.add_argument("--title", default="untitled")
    ap.add_argument("--channel", default="")
    ap.add_argument("--duration", default="")
    ap.add_argument("--source", default="youtube")
    ap.add_argument("--fetch-method", dest="fetch_method", default="captions")
    ap.add_argument("--chapters", default="[]", help='JSON [[sec,"name"],...]')
    ap.add_argument("--distill", default="")
    ap.add_argument("--group", type=int, default=20)
    ap.add_argument("--print-path", action="store_true")
    ns = ap.parse_args()

    cues = parse_any(Path(ns.caption_file))
    if not cues:
        sys.exit("ERROR: ไม่พบ cue ในไฟล์ caption (ไฟล์ว่างหรือ format ไม่รองรับ)")
    chapters = json.loads(ns.chapters) if ns.chapters else []
    body = cues_to_body(cues, chapters, group=ns.group)
    meta = {k: getattr(ns, k) for k in
            ("url", "id", "title", "channel", "duration", "source", "fetch_method", "distill")}
    out = write_note(body, meta)

    n_chap = body.count("\n### ")
    n_para = len(re.findall(r"(?m)^\d+:\d\d · ", body))
    if ns.print_path:
        print(out)
    else:
        print(f"OK -> {out.name}")
        print(f"   cues={len(cues)}  chapters={n_chap}  paragraphs={n_para}  chars={len(body)}")


if __name__ == "__main__":
    main()
