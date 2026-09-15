from pathlib import Path
from datetime import datetime, timezone
import sqlite3
import subprocess

BOT_DIR = Path("/root/BZM-Telegram-Replit/BZM-Telegram-Replit")
BOT = BOT_DIR / "bot.py"
DB = BOT_DIR / "bzm_loyalty.db"

results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))

# 1 - Servis
r = subprocess.run(
    ["systemctl", "is-active", "bzm-bot.service"],
    capture_output=True, text=True
)
check("BZM bot servisi", r.stdout.strip() == "active", r.stdout.strip())

# 2 - Python derleme
r = subprocess.run(
    [str(BOT_DIR / "venv/bin/python"), "-m", "py_compile", str(BOT)],
    capture_output=True, text=True
)
check("bot.py Python kontrolü", r.returncode == 0)

# 3 - Veritabanı
try:
    con = sqlite3.connect(DB)
    tables = {x[0] for x in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    con.close()

    required = {"users", "campaign_claims", "withdrawals"}
    check("SQLite veritabanı", True)
    check("Gerekli tablolar", required.issubset(tables))
except Exception as e:
    check("SQLite veritabanı", False, type(e).__name__)

# 4 - Temel yazılım modülleri
try:
    code = BOT.read_text(encoding="utf-8")

    required_code = [
        "def is_admin(",
        "async def admin_panel(",
        "async def admin_callback(",
        "async def gorev(",
        "async def cek(",
        "def blocked_user_info("
    ]

    check(
        "Admin/görev/çekim güvenlik modülleri",
        all(x in code for x in required_code)
    )
except Exception:
    check("Admin/görev/çekim güvenlik modülleri", False)

print("BZM BOT YAZILIM SAGLIK KONTROLU")
print("Tarih UTC:", datetime.now(timezone.utc).isoformat())
print("-" * 46)

for name, ok, detail in results:
    status = "PASS" if ok else "FAIL"
    extra = f" ({detail})" if detail else ""
    print(f"[{status}] {name}{extra}")

passed = sum(1 for _, ok, _ in results if ok)

print("-" * 46)
print(f"SONUC: {passed}/{len(results)} kontrol basarili")
print("GENEL DURUM:", "HEALTHY" if passed == len(results) else "CHECK REQUIRED")
