# youtube-to-obsidian

A **Claude Code skill** that turns any YouTube video — *including member-only ones* — into a polished Obsidian note: a verbatim timestamped transcript in your archive **plus** a dense, well-linked concept note with clickable timestamp links and **HD screenshots pulled straight from the video**.

> ดึง transcript จากคลิป YouTube (public + member-only) เข้า Obsidian → distill เป็นโน้ต concept แน่นๆ พร้อม timestamp links + ภาพประกอบ HD จากในคลิป · เป็น Claude Code skill

It was built and battle-tested through real use, then hardened so a fresh Claude session hits the same quality bar **by default** — see the `## 🎯 Definition of Done` in [`SKILL.md`](SKILL.md).

---

## What it does

| Phase | Output |
|---|---|
| **Triage** | public vs member-only |
| **Fetch + format** | verbatim transcript → `_archive/conversations-raw/youtube/` in a clean *chaptered, paragraph-timestamped* format |
| **Distill** | dense concept note (~80%+ of the talk: named entities as tables, concrete examples, numbers, the *why*) in a domain folder, with `[▸ M:SS]` links that jump the video |
| **Visuals** | for visual-heavy clips: HD (1080p+) frames captured from the video, analyzed so each one shows the **whole** diagram/dashboard, then embedded next to the matching section |

Two fetch paths:

- **Public clips** → one command (`fetch_public.py`): yt-dlp grabs metadata + auto chapters + captions, falls back to local Whisper (with timing) — all formatted and written in one shot.
- **Member-only clips** → captured through the **Claude-in-Chrome** extension by intercepting the caption track the player itself loads (cookies / `--cookies-from-browser` don't work under Chrome's App-Bound Encryption). See [`references/member-capture.md`](references/member-capture.md).

## Repo layout

```
SKILL.md                         # orchestration + Definition of Done (always-loaded)
scripts/
  config.py                      # resolves paths from $OBSIDIAN_VAULT
  format_transcript.py           # universal formatter: json3 / vtt / srt / whisper-cues → note
  fetch_public.py                # public path, one command
  prepare_images.py              # move captured PNGs → vault + verify they're HD
references/
  member-capture.md              # member-only capture (Claude-in-Chrome) + JS templates
  distill-and-timestamps.md      # density rules + timestamp links + image capture rules
  transcript-format.md           # the transcript format spec
  setup.md                       # install + AV/SSL fix + known issues
```

## Install

1. **Python deps**
   ```bash
   python -m pip install -U yt-dlp faster-whisper imageio-ffmpeg certifi
   ```
2. **Point it at your vault** (required)
   ```powershell
   # Windows PowerShell
   $env:OBSIDIAN_VAULT = 'C:\path\to\your\vault'
   ```
   ```bash
   # macOS / Linux
   export OBSIDIAN_VAULT=/path/to/your/vault
   ```
   Optional: `DOWNLOADS_DIR` (defaults to `~/Downloads`).
3. **Install as a Claude Code skill** — copy this folder into `<vault>/.claude/skills/youtube-to-obsidian/` (or any Claude Code skills dir). Claude will auto-discover it.
4. **Member-only clips** also need the **Claude-in-Chrome** extension signed in, with the side panel opened once to pair.

The note structure it produces (`_archive/`, `_attachments/`, domain folders like `50_dev/`) follows a personal-vault convention — adapt the folder names in `scripts/config.py` and the references to your own.

## Usage

Just ask Claude (with the skill installed):

```
ดึงคลิปนี้ลง obsidian: https://www.youtube.com/watch?v=...
```
or in English: *"distill this YouTube talk into my vault: <url>"*

Or run the public path directly:
```bash
python scripts/fetch_public.py "https://www.youtube.com/watch?v=..." --distill "[[My distilled note]]"
```

## Notes & credits

- Designed around the **"AI distill, user refine"** philosophy: the raw transcript is the source of truth (never edited); the distilled note is dense enough that *refining* means adding your own insight, not re-adding content the AI dropped.
- The image-capture rules exist because of real feedback: **analyze the content and capture the complete diagram**, force 1080p+, and verify the saved frame — not a blurry or partial grab.
- Transcript format inspired by the chapter + `M:SS ·` style used by Thai tech channels.

## License

MIT — see [LICENSE](LICENSE).
