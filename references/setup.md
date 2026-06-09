# Setup + Known issues

## ติดตั้งเครื่องมือ (ครั้งแรกของแต่ละเครื่อง)

```bash
python -m pip install -U yt-dlp faster-whisper imageio-ffmpeg certifi
```
- `yt-dlp` — เรียกผ่าน `python -m yt_dlp` (อาจไม่อยู่ใน PATH)
- `faster-whisper` — ถอดเสียง CPU int8 (ไม่ต้องใช้ PyTorch; มาพร้อม PyAV + CTranslate2) ใช้ได้บน Python 3.14
- `imageio-ffmpeg` — static ffmpeg binary: `python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`
- ไม่ต้องใช้ winget (เคย fail cert error บนเครื่องนี้)

## แก้ SSL: `CERTIFICATE_VERIFY_FAILED` (สำคัญบนเครื่องที่มี Antivirus)

อาการ: yt-dlp ต่อ YouTube ไม่ได้ `[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`

สาเหตุ: **Antivirus ที่ทำ SSL inspection (เช่น Norton/Kaspersky/ESET/Bitdefender) สแกน HTTPS** → เซ็น cert ใหม่ด้วย root ของตัวเอง ซึ่งอยู่ใน Windows store แต่ **ไม่อยู่ใน certifi bundle** ที่ yt-dlp ใช้

วินิจฉัย — ดูว่าใครเซ็น cert ของ youtube:
```python
import ssl,socket
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
with socket.create_connection(("www.youtube.com",443),timeout=15) as s:
  with ctx.wrap_socket(s,server_hostname="www.youtube.com") as ss:
    der=ss.getpeercert(binary_form=True)
from cryptography import x509
print(x509.load_pem_x509_certificate(ssl.DER_cert_to_PEM_cert(der).encode()).issuer.rfc4514_string())
# ถ้าเห็น "Norton..." / AV ใดๆ = โดน SSL inspection
```

แก้ — export root ของ AV จาก Windows store ต่อท้าย `certifi/cacert.pem` (PowerShell):
```powershell
$certs = Get-ChildItem Cert:\LocalMachine\Root, Cert:\CurrentUser\Root |
  Where-Object { $_.Subject -like "*Norton*" -or $_.Issuer -like "*Norton*" }
$bundle = python -c "import certifi;print(certifi.where())"
foreach($c in $certs){
  $b64=[Convert]::ToBase64String($c.RawData,'InsertLineBreaks')
  $pem="`n# AV root (added for yt-dlp under SSL inspection)`n-----BEGIN CERTIFICATE-----`n$b64`n-----END CERTIFICATE-----`n"
  if((Get-Content $bundle -Raw) -notmatch [regex]::Escape($c.Thumbprint.Substring(0,8))){ Add-Content $bundle $pem -Encoding ascii }
}
```
> ⚠️ ถ้า `pip install -U certifi` ทับ bundle เมื่อไหร่ ต้องต่อ root ใหม่ · yt-dlp ไม่อ่าน `SSL_CERT_FILE` ต้องแก้ที่ `cacert.pem` โดยตรง

## Known issues (รวมจากที่เจอจริง)

| ปัญหา | สาเหตุ | วิธีแก้ |
|---|---|---|
| `SSL CERTIFICATE_VERIFY_FAILED` | AV สแกน HTTPS (Norton ฯลฯ) | ต่อ AV root → certifi (ข้างบน) |
| `Could not copy Chrome cookie database` | Chrome เปิดอยู่ ล็อก DB | ใช้ Path B (Claude-in-Chrome) แทน — อย่าเสียเวลาปิด Chrome |
| `Failed to decrypt with DPAPI` (#10927) | Chrome v127+ App-Bound Encryption | ใช้ Path B แทน (cookie member ดึงตรงไม่ได้บนเครื่องนี้) |
| `[BLOCKED: Cookie/query string data]` | extension บล็อก return ที่มี URL+token | ให้ JS fetch/parse ในหน้า return แค่ข้อความ/ตัวเลข |
| caption fetch ได้ body ว่าง (200, len 0) | YouTube ต้องการ pot token | ให้ player โหลดเอง (กด `c`) แล้วดักจับ timedtext |
| Chrome ไม่โหลดไฟล์ที่ 2 | multiple-download guard ต่อหน้า | ชื่อไฟล์ใหม่ทุกครั้ง + โหลดทีละไฟล์ (เลี่ยง clipboard API — focus ค้าง) |
| `UnicodeEncodeError ... cp1252` | console Windows ไม่ใช่ utf-8 | `sys.stdout.reconfigure(encoding="utf-8")` ต้นสคริปต์ |
| `list_connected_browsers` ได้ `[]` | extension หลุด pair | ผู้ใช้เปิด side panel "Claude" extension → re-pair |
| array ยาว return โดน truncate | tool output limit | ส่งออกเป็นไฟล์ (Blob download) แทน return ตรงๆ |

## พิสูจน์แล้วกับ
- public: `PyMyz9XiAiw` (caption ไทย 24,917 ตัวอักษร ผ่านสคริปต์)
- member-only: `bIGmyLSXhOY` (Claude code 101 Lesson 3-4, ดักจับ json3 → 38k ตัวอักษร ผ่าน Claude-in-Chrome)
