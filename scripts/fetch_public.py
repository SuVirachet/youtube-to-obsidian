"""Path A — ดึง transcript คลิป PUBLIC → Gemma format → _archive/conversations-raw/youtube/

ลอง caption (vtt) ก่อน → ไม่มีค่อย Whisper (faster-whisper, segments มี timing).
ใช้ format_transcript.py เป็น formatter ร่วม (single source) → ได้ output แบบเดียวกับ Path B
(member) คือ ## บทต่างๆ + ## Transcript + ### chapter + `M:SS · ` ย่อหน้า ~20 วิ.

chapters มาจาก yt-dlp อัตโนมัติ (ถ้าคลิปมี). ถ้าคลิป member จะเด้ง error → ใช้ Path B แทน.

Usage:
  python fetch_public.py "<URL>" [--browser none|chrome] [--cookies file]
        [--lang th,en] [--model large-v3] [--distill "[[ชื่อโน้ต distill]]"]
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).resolve().parent))
import format_transcript as F  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def ytdlp(args, capture=True):
    cmd = [sys.executable, "-m", "yt_dlp", "--ffmpeg-location", FFMPEG, *args]
    return subprocess.run(cmd, capture_output=capture, text=True, encoding="utf-8")


def auth(ns):
    if ns.cookies:
        return ["--cookies", ns.cookies]
    if ns.browser.lower() == "none":
        return []
    return ["--cookies-from-browser", ns.browser]


def dur_str(sec):
    sec = int(sec or 0)
    return f"{sec // 60}m{sec % 60:02d}s" if sec else "?"


def get_meta(url, ns):
    r = ytdlp([*auth(ns), "--skip-download", "--no-warnings", "-J", url])
    if r.returncode != 0:
        sys.exit(
            "ERROR: yt-dlp เข้าถึงคลิปไม่ได้.\n"
            "  - member-only? → ใช้ Path B (Claude-in-Chrome) แทน\n"
            "  - SSL CERTIFICATE_VERIFY_FAILED? → ดู references/setup.md (Norton root)\n\n"
            f"{r.stderr[-1200:]}"
        )
    j = json.loads(r.stdout)
    chapters = [[int(c.get("start_time", 0)), c.get("title", "")]
                for c in (j.get("chapters") or []) if c.get("title")]
    return {
        "id": j.get("id", ""), "title": j.get("title", "untitled"),
        "channel": j.get("uploader", ""), "duration": dur_str(j.get("duration")),
        "url": j.get("webpage_url", url), "chapters": chapters,
    }


def get_vtt(url, ns, tmp):
    langs = ",".join(f"{l}.*" for l in ns.lang.split(","))
    ytdlp([*auth(ns), "--skip-download", "--write-subs", "--write-auto-subs",
           "--sub-langs", langs, "--sub-format", "vtt",
           "-o", str(tmp / "%(id)s.%(ext)s"), url])
    vtts = sorted(tmp.glob("*.vtt"), key=lambda p: (".auto." in p.name.lower(), p.name))
    return vtts[0] if vtts else None


def whisper_cues(url, ns, tmp):
    print("  ไม่มี caption → โหลดเสียงถอดด้วย Whisper...", flush=True)
    r = ytdlp([*auth(ns), "-f", "bestaudio/best", "-o", str(tmp / "a.%(ext)s"), url], capture=False)
    if r.returncode != 0:
        sys.exit("ERROR: โหลดเสียงไม่สำเร็จ")
    audio = next((p for p in tmp.iterdir() if p.suffix.lower()
                  in (".m4a", ".webm", ".opus", ".mp3", ".mp4")), None)
    if not audio:
        sys.exit("ERROR: ไม่พบไฟล์เสียง")
    print(f"  Whisper ({ns.model}, CPU int8)...", flush=True)
    from faster_whisper import WhisperModel
    model = WhisperModel(ns.model, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(audio), language=ns.lang.split(",")[0], vad_filter=True)
    return [(int(s.start), s.text.strip()) for s in segs if s.text.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--browser", default="none")
    ap.add_argument("--cookies", default=None)
    ap.add_argument("--lang", default="th,en")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--distill", default="")
    ns = ap.parse_args()

    meta = get_meta(ns.url, ns)
    print(f"Video: {meta['title']}  [{meta['id']}]  ·  {len(meta['chapters'])} chapters")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        vtt = get_vtt(ns.url, ns, tmp)
        if vtt:
            cues = F.parse_vtt(vtt.read_text(encoding="utf-8", errors="ignore"))
            fetch_method = f"captions ({vtt.name})"
        else:
            cues = whisper_cues(ns.url, ns, tmp)
            fetch_method = f"whisper:{ns.model}"

    if not cues:
        sys.exit("ERROR: ไม่ได้ cue เลย (ทั้ง caption และ Whisper)")
    body = F.cues_to_body(cues, meta["chapters"])
    out = F.write_note(body, {
        "url": meta["url"], "id": meta["id"], "title": meta["title"],
        "channel": meta["channel"], "duration": meta["duration"],
        "source": "youtube", "fetch_method": fetch_method, "distill": ns.distill,
    })
    print(f"OK -> {out.name}\n   method={fetch_method}  cues={len(cues)}  chapters={len(meta['chapters'])}")


if __name__ == "__main__":
    main()
