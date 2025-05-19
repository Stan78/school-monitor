from flask import Flask
import hashlib
import requests
import os
import json

app = Flask(__name__)

TELEGRAM_TOKEN = "8104929376:AAHTdEhMLDtJlujISK7k5qdDaJreKqBskm4"
TELEGRAM_CHAT_ID = "1707995106"

SCHOOL_URLS = {
    "18 СУ": "https://18sou.net/свободни-места/",
    "32 СУИЧЕ": "https://school32.com/прием/свободни-места/",
    "СМГ": "https://smg.bg/razni/2024/03/11/8622/svobodni-mesta-za-priem-na-uchenitsi-v-10-klas-za-втори-срок-на-учебната-2023-2024-гoдина/",
    "НПМГ": "https://npmg.org/прием-в-старши-класове/",
    "1 АЕГ": "https://www.fels-sofia.org/bg/svobodni-mesta-236",
    "2 АЕГ": "https://2els.com/информация-за-свободни-места",
    "90 СУ": "https://sou90.org/priem/",
    "22 СЕУ": "https://22seu.org/свободни-места-за-ученици/"
}

HASHES_FILE = "site_hashes.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

def check_sites():
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, "r") as f:
            old_hashes = json.load(f)
    else:
        old_hashes = {}

    updates = []
    new_hashes = {}

    for school, url in SCHOOL_URLS.items():
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            hash = hashlib.md5(res.text.encode()).hexdigest()
            new_hashes[school] = hash
            if old_hashes.get(school) != hash:
                updates.append(f"🔔 <b>{school}</b>: {url}")
        except Exception as e:
            updates.append(f"⚠️ {school} error: {e}")

    with open(HASHES_FILE, "w") as f:
        json.dump(new_hashes, f, ensure_ascii=False, indent=2)

    if updates:
        send_telegram("📝 <b>Нови съобщения:</b>\n\n" + "\n\n".join(updates))

@app.route('/')
def index():
    return "🟢 Running!"

@app.route('/run')
def run_check():
    try:
        check_sites()
        return "✅ Check completed."
    except Exception as e:
        # Log error somewhere (e.g., to a file or just print)
        print(f"Error during check: {e}")
        return "❌ Error during check."

from datetime import datetime

@app.route('/dashboard')
def dashboard():
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, "r") as f:
            current_hashes = json.load(f)
    else:
        current_hashes = {}

    html = "<h1>📊 School Monitoring Dashboard</h1><ul>"

    for school, url in SCHOOL_URLS.items():
        hash_val = current_hashes.get(school, "—")
        html += f"<li><strong>{school}</strong>: <a href='{url}' target='_blank'>линк</a> — Хеш: <code>{hash_val}</code></li>"

    html += f"</ul><p>⏱️ Последна проверка: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
    return html
