"""ย้ายภาพที่ capture จาก Downloads → _attachments + **verify HD อัตโนมัติ** (quality gate)

อ่านขนาด PNG จาก header เอง (ไม่ต้องใช้ PIL) → เตือนถ้าภาพ < 1900px กว้าง (= ไม่ใช่ 1080p, เบลอ)
→ ต้องกลับไป capture ใหม่ด้วย hd1080 (ดู references/distill-and-timestamps.md)

Usage:
  python prepare_images.py target1=src1.png target2=/full/path/src2.png ...
    - target = ชื่อปลายทางใน _attachments (ไม่ต้องใส่ .png ก็ได้)
    - src    = ชื่อไฟล์ใน Downloads หรือ path เต็ม
  เช่น:
  python prepare_images.py ltd-kb-flywheel=hd-flywheel.png ltd-kb-index=hd-index.png

ผลลัพธ์: ย้ายไฟล์ + พิมพ์ขนาด + ✅/⚠️ ต่อภาพ + exit code 1 ถ้ามีภาพไม่ HD (เพื่อให้รู้ว่าต้อง re-capture)
"""
import struct
import sys
from pathlib import Path

import config  # vault paths from OBSIDIAN_VAULT env
MIN_W = 1900  # 1080p ~ 1920 กว้าง; ต่ำกว่านี้ = เบลอ (มัก 854x480)

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def png_size(p: Path):
    """อ่าน (width,height) จาก PNG header (bytes 16-24). คืน None ถ้าไม่ใช่ PNG."""
    with p.open("rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python prepare_images.py target=src.png ...")
    attach = config.attachments()
    attach.mkdir(parents=True, exist_ok=True)
    bad = []
    for arg in sys.argv[1:]:
        if "=" not in arg:
            print(f"  ข้าม (รูปแบบผิด): {arg}")
            continue
        target, src = arg.split("=", 1)
        target = target if target.endswith(".png") else target + ".png"
        sp = Path(src)
        if not sp.is_absolute():
            sp = config.downloads() / src
        if not sp.exists():
            print(f"  ⚠️ ไม่พบ source: {sp}")
            bad.append(target)
            continue
        size = png_size(sp)
        dst = attach / target
        sp.replace(dst)
        if size is None:
            print(f"  ⚠️ {target}: ไม่ใช่ PNG ที่อ่าน header ได้")
            bad.append(target)
        elif size[0] < MIN_W:
            print(f"  ⚠️ {target}: {size[0]}x{size[1]} = ไม่ HD (เบลอ!) → re-capture ด้วย hd1080")
            bad.append(target)
        else:
            print(f"  ✅ {target}: {size[0]}x{size[1]}")
    if bad:
        print(f"\n⚠️ {len(bad)} ภาพไม่ผ่าน — re-capture: {', '.join(bad)}")
        sys.exit(1)
    print("\nOK — ทุกภาพ HD พร้อม embed ![[...]]")


if __name__ == "__main__":
    main()
