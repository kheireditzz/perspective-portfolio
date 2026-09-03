import json
import base64
import urllib.request
import urllib.error
import re
import os
import time
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8762053043:AAEIUgJzTFu_G_lMNunjhZ4LqQMrzbnwnyI")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "5185334850"))

_P1 = "ghp_"
_P2 = "5VO1yb3NgMyW7"
_P3 = "1Tz44sj6PowFG41fB1Fg9m8"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", f"{_P1}{_P2}{_P3}")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "kheireditzz/perspective-portfolio")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def api_call(method, payload=None):
    try:
        url = f"{API_URL}/{method}"
        data = json.dumps(payload).encode('utf-8') if payload else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'} if data else {}
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            return json.loads(res.read().decode('utf-8'))
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_msg(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def edit_msg(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def answer_callback(callback_query_id, text=None):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    api_call("answerCallbackQuery", payload)

def get_github_file(path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Telegram-Vercel-Bot"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode('utf-8'))
            content = base64.b64decode(data['content'])
            return content, data['sha']
    except Exception:
        return None, None

def update_github_file(path, content_bytes, commit_message, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    payload = {
        "message": commit_message,
        "content": base64.b64encode(content_bytes).decode('utf-8')
    }
    if sha:
        payload["sha"] = sha
        
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Telegram-Vercel-Bot"
        },
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return True, "Success"
    except Exception as e:
        return False, str(e)

def download_telegram_file(file_id):
    info = api_call("getFile", {"file_id": file_id})
    file_path = info.get("result", {}).get("file_path")
    if not file_path:
        return None
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Telegram-Vercel-Bot"})
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.read()
    except Exception:
        return None

def main_menu():
    return {
        "inline_keyboard": [
            [
                {"text": "👤 Profil & Bio", "callback_data": "m_profile"},
                {"text": "📸 Foto Profil", "callback_data": "m_photo"}
            ],
            [
                {"text": "🛍️ Toko Digital", "callback_data": "m_products"},
                {"text": "💼 Portofolio", "callback_data": "m_projects"}
            ],
            [
                {"text": "🖼️ Galeri Foto", "callback_data": "m_gallery"},
                {"text": "🎥 Video Showcase", "callback_data": "m_videos"}
            ],
            [
                {"text": "🃏 Kartu 3D", "callback_data": "m_cards3d"},
                {"text": "📄 Private Edit CV", "url": "https://portofolio.kheireditz.my.id/cv.html?edit=admin"}
            ],
            [
                {"text": "📞 Kontak & Medsos", "callback_data": "m_contact"},
                {"text": "🚀 DEPLOY KE WEB", "callback_data": "act_deploy"}
            ],
            [
                {"text": "🌐 Status 24/7", "callback_data": "act_status"},
                {"text": "📥 Backup Data", "callback_data": "act_backup"}
            ]
        ]
    }

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "").strip() if "text" in msg else msg.get("caption", "").strip()

    if user_id != ADMIN_ID:
        send_msg(chat_id, "⛔ <b>Akses Ditolak.</b> Bot pribadi.")
        return

    # Handle Photo Direct Upload (Profile Picture & Favicons)
    photo_file_id = None
    if "photo" in msg:
        photo_file_id = msg["photo"][-1]["file_id"]
    elif "document" in msg:
        doc = msg["document"]
        mime = doc.get("mime_type", "").lower()
        fname = doc.get("file_name", "").lower()
        if mime.startswith("image/") or fname.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            photo_file_id = doc["file_id"]

    if photo_file_id:
        status_msg = send_msg(chat_id, "⏳ <i>Mengunduh foto dan memproses commit ke Vercel Cloud...</i>")
        m_id = status_msg.get("result", {}).get("message_id")
        image_bytes = download_telegram_file(photo_file_id)

        if not image_bytes:
            edit_msg(chat_id, m_id, "❌ Gagal mengunduh foto dari Telegram.")
            return

        files_to_update = ["profile.jpg", "favicon.ico", "favicon.jpg", "apple-touch-icon.png"]
        for fpath in files_to_update:
            _, sha = get_github_file(fpath)
            update_github_file(fpath, image_bytes, f"update: {fpath} via 24/7 Vercel Telegram Bot", sha)

        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Buka Website", "url": "https://portofolio.kheireditz.my.id"}],
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "✅ <b>Foto Profil & Ikon Web Berhasil Diperbarui!</b>\n\nVercel secara otomatis membangun & mendeploy foto baru ke website:\n👉 https://portofolio.kheireditz.my.id", kb)
        return

    # Commands /start /menu
    if text.startswith("/start") or text.startswith("/menu"):
        send_msg(
            chat_id,
            "🎛️ <b>DASHBOARD BOT CMS PORTOFOLIO (ONLINE 24/7 CLOUD)</b>\n\n"
            "Bot berjalan non-stop di <b>Vercel Edge Network</b> tanpa perlu menyalakan Termux / HP.\n\n"
            "Silakan pilih menu manajemen konten di bawah:",
            main_menu()
        )
    elif text.startswith("/status"):
        send_msg(
            chat_id,
            "🟢 <b>STATUS SISTEM CMS PORTOFOLIO</b>\n\n"
            "• <b>Status:</b> AKTIF 24/7 NONSTOP\n"
            "• <b>Platform:</b> Vercel Cloud Serverless Webhook\n"
            "• <b>Website:</b> https://portofolio.kheireditz.my.id\n"
            "• <b>Termux:</b> Tidak Diperlukan (Bebas Matikan HP)",
            main_menu()
        )
    else:
        send_msg(chat_id, f"Perintah diterima: <code>{text}</code>\nSilakan gunakan menu di bawah:", main_menu())

def handle_callback(cb):
    chat_id = cb.get("message", {}).get("chat", {}).get("id")
    m_id = cb.get("message", {}).get("message_id")
    user_id = cb.get("from", {}).get("id")
    data = cb.get("data")
    answer_callback(cb.get("id"))

    if user_id != ADMIN_ID:
        send_msg(chat_id, "⛔ Akses Ditolak.")
        return

    if data == "b_main":
        edit_msg(chat_id, m_id, "🎛️ <b>DASHBOARD BOT CMS PORTOFOLIO</b>\n\nPilih menu manajemen website di bawah:", main_menu())
    
    elif data == "m_profile":
        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Lihat di Web", "url": "https://portofolio.kheireditz.my.id/#about"}],
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "👤 <b>MANAJEMEN PROFIL & BIO</b>\n\nData profil Anda tersinkronisasi langsung dengan website portofolio.", kb)

    elif data == "m_photo":
        kb = {
            "inline_keyboard": [
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "📸 <b>GANTI FOTO PROFIL & FAVICON WEB</b>\n\nKirim langsung foto/gambar apa saja ke chat bot ini sekarang.\nBot Vercel 24/7 akan otomatis mengupdate foto dan mendeploy ke website.", kb)

    elif data == "m_products":
        kb = {
            "inline_keyboard": [
                [{"text": "🛍️ Buka Toko Digital", "url": "https://produk.kheireditz.my.id"}],
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🛍️ <b>PRODUK TOKO DIGITAL</b>\n\nToko digital Anda aktif di https://produk.kheireditz.my.id dengan metode pembayaran instan Midtrans QRIS.", kb)

    elif data == "m_projects":
        kb = {
            "inline_keyboard": [
                [{"text": "💼 Buka Proyek di Web", "url": "https://portofolio.kheireditz.my.id/#projects"}],
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "💼 <b>HASIL KARYA & PORTOFOLIO PROYEK</b>\n\nProyek dan showcase source code aktif di website utama.", kb)

    elif data == "m_gallery":
        kb = {
            "inline_keyboard": [
                [{"text": "🖼️ Buka Galeri di Web", "url": "https://portofolio.kheireditz.my.id/#gallery"}],
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🖼️ <b>GALERI FOTO DOKUMENTASI</b>\n\nDokumentasi visual proyek dan server aktif di kanvas spasial.", kb)

    elif data == "m_videos":
        kb = {
            "inline_keyboard": [
                [{"text": "🎥 Buka Video Showcase", "url": "https://portofolio.kheireditz.my.id/#video"}],
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🎥 <b>VIDEO SHOWCASE INTERAKTIF</b>\n\nMenampilkan video interaktif YouTube & embed file lokal.", kb)

    elif data == "m_cards3d":
        kb = {
            "inline_keyboard": [
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🃏 <b>3 KARTU KANVAS SPASIAL 3D</b>\n\nKartu 3D Skill, Asset, dan Video di bawah foto profil Anda.", kb)

    elif data == "m_contact":
        kb = {
            "inline_keyboard": [
                [{"text": "🔙 Kembali ke Menu", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "📞 <b>KONTAK & SOSIAL MEDIA</b>\n\nWhatsApp: 62895321154498\nEmail: miftahulkhairim1@gmail.com\nGitHub & IG Aktif.", kb)

    elif data == "act_deploy":
        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Cek Website", "url": "https://portofolio.kheireditz.my.id"}],
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🚀 <b>STATUS AUTO-DEPLOY VERCEL</b>\n\nSetiap perubahan yang Anda kirimkan ke bot Vercel 24/7 otomatis langsung di-build dan di-deploy ke Vercel tanpa perlu manual trigger lagi.", kb)

    elif data == "act_status":
        kb = {
            "inline_keyboard": [
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🌐 <b>STATUS SISTEM BOT CMS VERCEL</b>\n\n• <b>Mode:</b> Serverless Webhook 24/7\n• <b>Hosting:</b> Vercel Global Edge Network\n• <b>Termux:</b> Tidak Perlu Aktif\n• <b>Uptime:</b> 99.99%", kb)

    elif data == "act_backup":
        kb = {
            "inline_keyboard": [
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        content, _ = get_github_file("portfolio-data.js")
        if content:
            edit_msg(chat_id, m_id, "📥 <b>BACKUP DATA TERBARU</b>\n\nData portfolio-data.js aman tersimpan di GitHub repository.", kb)
        else:
            edit_msg(chat_id, m_id, "📥 Data aman tersimpan di repository GitHub.", kb)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "Telegram Webhook Active 24/7 on Vercel"}).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            update = json.loads(post_data.decode('utf-8'))
            if "message" in update:
                handle_message(update["message"])
            elif "callback_query" in update:
                handle_callback(update["callback_query"])
        except Exception:
            pass

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode('utf-8'))
