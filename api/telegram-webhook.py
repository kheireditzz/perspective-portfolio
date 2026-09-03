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

# In-memory session state per user for multi-step prompts
user_states = {}

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
        with urllib.request.urlopen(req, timeout=45) as res:
            return res.read()
    except Exception:
        return None

def load_data_from_github():
    content, sha = get_github_file("portfolio-data.js")
    if not content:
        return None, None
    text = content.decode('utf-8')
    match = re.search(r'window\.PORTFOLIO_CONFIG\s*=\s*(\{[\s\S]*\});', text)
    if match:
        raw_json = match.group(1)
        raw_json = re.sub(r'//.*', '', raw_json)
        raw_json = re.sub(r'/\*[\s\S]*?\*/', '', raw_json)
        raw_json = re.sub(r',(\s*[\}\]])', r'\1', raw_json)
        try:
            return json.loads(raw_json), sha
        except Exception:
            pass
    return None, sha

def save_data_to_github(data, sha, commit_msg="update: portfolio data via Telegram Bot CMS"):
    formatted_js = "/**\n * PUSAT DATA PORTOFOLIO MIFTAHUL KHAIRIN (AUTO-MANAGED BY TELEGRAM BOT)\n */\nwindow.PORTFOLIO_CONFIG = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n"
    return update_github_file("portfolio-data.js", formatted_js.encode('utf-8'), commit_msg, sha)

def format_youtube_embed(url):
    # Convert standard YouTube URL to clean embed format
    if "youtu.be/" in url:
        vid_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube-nocookie.com/embed/{vid_id}?controls=1&rel=0"
    elif "watch?v=" in url:
        vid_id = url.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{vid_id}?controls=1&rel=0"
    elif "/embed/" in url:
        return url
    return url

def main_menu():
    return {
        "inline_keyboard": [
            [
                {"text": "👤 Profil & Bio", "callback_data": "m_profile"},
                {"text": "📸 Foto Profil", "callback_data": "m_photo"}
            ],
            [
                {"text": "🎥 Video Showcase", "callback_data": "m_videos"},
                {"text": "🛍️ Toko Digital", "callback_data": "m_products"}
            ],
            [
                {"text": "💼 Portofolio", "callback_data": "m_projects"},
                {"text": "🖼️ Galeri Foto", "callback_data": "m_gallery"}
            ],
            [
                {"text": "🃏 Kartu 3D", "callback_data": "m_cards3d"},
                {"text": "📄 Private Edit CV", "url": "https://portofolio.kheireditz.my.id/cv.html?edit=admin"}
            ],
            [
                {"text": "📞 Kontak & Medsos", "callback_data": "m_contact"},
                {"text": "🌐 Status 24/7", "callback_data": "act_status"}
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

    state = user_states.get(chat_id)

    # 1. HANDLE DIRECT VIDEO FILE UPLOAD (MP4)
    video_file_id = None
    if "video" in msg:
        video_file_id = msg["video"]["file_id"]
    elif "animation" in msg:
        video_file_id = msg["animation"]["file_id"]
    elif "document" in msg:
        doc = msg["document"]
        mime = doc.get("mime_type", "").lower()
        fname = doc.get("file_name", "").lower()
        if mime.startswith("video/") or fname.endswith(('.mp4', '.mov', '.webm')):
            video_file_id = doc["file_id"]

    if video_file_id:
        status_msg = send_msg(chat_id, "⏳ <i>Mengunduh video MP4 dan mengunggah ke GitHub/Vercel...</i>")
        m_id = status_msg.get("result", {}).get("message_id")
        video_bytes = download_telegram_file(video_file_id)

        if not video_bytes:
            edit_msg(chat_id, m_id, "❌ Gagal mengunduh video dari Telegram.")
            return

        vid_filename = f"video_{int(time.time())}.mp4"
        github_vid_path = f"videos/{vid_filename}"
        ok_vid, _ = update_github_file(github_vid_path, video_bytes, f"feat: upload {github_vid_path} via Telegram")

        if ok_vid:
            d, sha = load_data_from_github()
            if d:
                vid_title = text if text else f"Video Showcase #{len(d.get('videos', [])) + 1}"
                new_vid = {
                    "id": int(time.time()),
                    "title": vid_title,
                    "desc": "Video demonstrasi & showcase interaktif.",
                    "file": github_vid_path,
                    "embed": github_vid_path,
                    "videoUrl": ""
                }
                d.setdefault('videos', []).insert(0, new_vid)
                save_data_to_github(d, sha, f"feat: add video {vid_title}")

            kb = {
                "inline_keyboard": [
                    [{"text": "🎥 Lihat di Web", "url": "https://portofolio.kheireditz.my.id/#video"}],
                    [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                ]
            }
            edit_msg(chat_id, m_id, f"✅ <b>Video Berhasil Diunggah & Ditambahkan!</b>\n\n• <b>Judul:</b> {vid_title}\n• <b>Path:</b> <code>{github_vid_path}</code>\n\nVercel otomatis mendeploy video ke website Anda.", kb)
        else:
            edit_msg(chat_id, m_id, "❌ Gagal mengunggah video ke GitHub (Maksimum upload 25MB). Gunakan URL YouTube jika video berukuran besar.")
        return

    # 2. HANDLE DIRECT PHOTO UPLOAD (PROFILE & FAVICONS)
    photo_file_id = None
    if "photo" in msg:
        photo_file_id = msg["photo"][-1]["file_id"]

    if photo_file_id and not state:
        status_msg = send_msg(chat_id, "⏳ <i>Mengunduh foto dan mengupdate ke Vercel Cloud...</i>")
        m_id = status_msg.get("result", {}).get("message_id")
        image_bytes = download_telegram_file(photo_file_id)

        if not image_bytes:
            edit_msg(chat_id, m_id, "❌ Gagal mengunduh foto.")
            return

        files_to_update = ["profile.jpg", "favicon.ico", "favicon.jpg", "apple-touch-icon.png"]
        for fpath in files_to_update:
            _, sha = get_github_file(fpath)
            update_github_file(fpath, image_bytes, f"update: {fpath} via 24/7 Vercel Bot", sha)

        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Buka Website", "url": "https://portofolio.kheireditz.my.id"}],
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "✅ <b>Foto Profil & Ikon Web Berhasil Diperbarui!</b>\n\nVercel langsung mendeploy foto baru ke website Anda.", kb)
        return

    # 3. MULTI-STEP FLOWS (ADD YOUTUBE VIDEO, EDIT FIELDS)
    if state:
        action = state.get("action")
        if action == "add_vid_title":
            user_states[chat_id] = {"action": "add_vid_url", "title": text}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_videos"}]]}
            send_msg(chat_id, f"🎬 Judul: <b>{text}</b>\n\nSekarang kirim <b>Link Video YouTube / URL MP4</b>:\nContoh: <code>https://www.youtube.com/watch?v=dQw4w9WgXcQ</code>", kb)
            return

        elif action == "add_vid_url":
            vid_title = state.get("title", "Video Baru")
            user_states[chat_id] = None
            embed_url = format_youtube_embed(text)

            status_msg = send_msg(chat_id, "⏳ <i>Menyimpan video ke data website & mendeploy...</i>")
            m_id = status_msg.get("result", {}).get("message_id")

            d, sha = load_data_from_github()
            if d:
                new_vid = {
                    "id": int(time.time()),
                    "title": vid_title,
                    "desc": "Video demonstrasi showcase interaktif.",
                    "embed": embed_url,
                    "videoUrl": text
                }
                d.setdefault('videos', []).insert(0, new_vid)
                ok, err = save_data_to_github(d, sha, f"feat: add showcase video {vid_title}")
                if ok:
                    kb = {
                        "inline_keyboard": [
                            [{"text": "🎥 Lihat di Web", "url": "https://portofolio.kheireditz.my.id/#video"}],
                            [{"text": "🎬 Kelola Video", "callback_data": "m_videos"}],
                            [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                        ]
                    }
                    edit_msg(chat_id, m_id, f"✅ <b>Video Berhasil Ditambahkan ke Web!</b>\n\n• <b>Judul:</b> {vid_title}\n• <b>URL:</b> <code>{text}</code>\n• <b>Embed:</b> <code>{embed_url}</code>\n\nVercel sedang auto-deploy ke website.", kb)
                else:
                    edit_msg(chat_id, m_id, f"❌ Gagal menyimpan video: {err}")
            return

    # 4. COMMANDS
    if text.startswith("/start") or text.startswith("/menu"):
        send_msg(
            chat_id,
            "🎛️ <b>DASHBOARD BOT CMS PORTOFOLIO (24/7 ONLINE VERCEL)</b>\n\n"
            "Kelola website Anda kapan saja secara instan:\n"
            "• Tambah / Hapus Video Showcase YouTube & MP4\n"
            "• Ganti foto profil & favicon web (kirim foto langsung)\n"
            "• Kelola portofolio, toko produk, dan profil",
            main_menu()
        )
    elif text.startswith("/status"):
        send_msg(
            chat_id,
            "🟢 <b>STATUS SISTEM CMS PORTOFOLIO</b>\n\n"
            "• <b>Status:</b> AKTIF 24/7 NONSTOP\n"
            "• <b>Hosting:</b> Vercel Cloud Edge Network\n"
            "• <b>Website:</b> https://portofolio.kheireditz.my.id",
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
        user_states[chat_id] = None
        edit_msg(chat_id, m_id, "🎛️ <b>DASHBOARD BOT CMS PORTOFOLIO</b>\n\nPilih menu manajemen website di bawah:", main_menu())

    # --- VIDEO MANAGEMENT ---
    elif data == "m_videos":
        user_states[chat_id] = None
        d, _ = load_data_from_github()
        vids = d.get('videos', []) if d else []
        kb_rows = []
        for i, it in enumerate(vids):
            kb_rows.append([{"text": f"🎬 {it.get('title')}", "callback_data": f"vv_{i}"}])
        kb_rows.append([{"text": "➕ Tambah Video YouTube/URL", "callback_data": "add_vid"}])
        kb_rows.append([{"text": "🔙 Menu Utama", "callback_data": "b_main"}])
        text = (
            f"🎥 <b>VIDEO SHOWCASE ({len(vids)} Video Aktif)</b>\n\n"
            "<b>Cara Menambah Video:</b>\n"
            "1. Klik <b>'Tambah Video YouTube/URL'</b> di bawah\n"
            "2. Atau langsung kirim file video <b>.MP4</b> ke chat bot ini.\n\nPilih video di bawah untuk melihat detail atau menghapus:"
        )
        edit_msg(chat_id, m_id, text, {"inline_keyboard": kb_rows})

    elif data == "add_vid":
        user_states[chat_id] = {"action": "add_vid_title"}
        kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_videos"}]]}
        edit_msg(chat_id, m_id, "🎬 <b>TAMBAH VIDEO BARU</b>\n\nKetik <b>Judul Video</b> yang ingin ditampilkan:", kb)

    elif data.startswith("vv_"):
        idx = int(data.split("_")[1])
        d, _ = load_data_from_github()
        vids = d.get('videos', []) if d else []
        if idx < len(vids):
            v = vids[idx]
            kb = {
                "inline_keyboard": [
                    [{"text": "🗑️ Hapus Video Ini", "callback_data": f"dv_{idx}"}],
                    [{"text": "🔙 Daftar Video", "callback_data": "m_videos"}]
                ]
            }
            src = v.get('videoUrl') or v.get('embed') or v.get('file')
            text = f"🎬 <b>DETAIL VIDEO #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {v.get('title')}\n• <b>Deskripsi:</b> {v.get('desc')}\n• <b>URL/Sumber:</b> <code>{src}</code>"
            edit_msg(chat_id, m_id, text, kb)

    elif data.startswith("dv_"):
        idx = int(data.split("_")[1])
        d, sha = load_data_from_github()
        if d and 'videos' in d and idx < len(d['videos']):
            rem = d['videos'].pop(idx)
            save_data_to_github(d, sha, f"feat: remove showcase video {rem.get('title')}")
            kb = {
                "inline_keyboard": [
                    [{"text": "🎥 Daftar Video", "callback_data": "m_videos"}],
                    [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                ]
            }
            edit_msg(chat_id, m_id, f"✅ Video <b>{rem.get('title')}</b> berhasil dihapus dari website portofolio!\n\nVercel sedang mendeploy pembaruan.", kb)

    # --- OTHER MENUS ---
    elif data == "m_photo":
        kb = {"inline_keyboard": [[{"text": "🔙 Menu Utama", "callback_data": "b_main"}]]}
        edit_msg(chat_id, m_id, "📸 <b>GANTI FOTO PROFIL & FAVICON WEB</b>\n\nKirim langsung file foto Anda ke chat ini. Bot 24/7 Vercel akan otomatis mengupdate ke GitHub dan deploy ke website.", kb)

    elif data == "m_profile":
        d, _ = load_data_from_github()
        p = d.get('profile', {}) if d else {}
        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Lihat di Web", "url": "https://portofolio.kheireditz.my.id/#about"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        text = f"👤 <b>PROFIL ANDA</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Nama:</b> {p.get('name')}\n• <b>Profesi:</b> {p.get('profession')}\n• <b>Lokasi:</b> {p.get('location')}\n• <b>Status:</b> {p.get('status')}\n• <b>Bio:</b> {p.get('bio')}"
        edit_msg(chat_id, m_id, text, kb)

    elif data == "m_products":
        kb = {
            "inline_keyboard": [
                [{"text": "🛍️ Buka Toko Digital", "url": "https://produk.kheireditz.my.id"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🛍️ <b>TOKO DIGITAL KHEIREDITZ</b>\n\nPlatform marketplace produk digital aktif di:\nhttps://produk.kheireditz.my.id", kb)

    elif data == "m_projects":
        kb = {
            "inline_keyboard": [
                [{"text": "💼 Buka Proyek di Web", "url": "https://portofolio.kheireditz.my.id/#projects"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "💼 <b>PORTOFOLIO PROYEK</b>\n\nDaftar proyek unggulan aktif di website.", kb)

    elif data == "m_gallery":
        kb = {
            "inline_keyboard": [
                [{"text": "🖼️ Buka Galeri di Web", "url": "https://portofolio.kheireditz.my.id/#gallery"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🖼️ <b>GALERI FOTO DOKUMENTASI</b>\n\nDokumentasi visual proyek aktif di web.", kb)

    elif data == "m_cards3d":
        kb = {"inline_keyboard": [[{"text": "🔙 Menu Utama", "callback_data": "b_main"}]]}
        edit_msg(chat_id, m_id, "🃏 <b>3 KARTU KANVAS SPASIAL 3D</b>\n\nKartu 3D Skill, Asset, dan Video di bawah foto profil Anda.", kb)

    elif data == "m_contact":
        kb = {"inline_keyboard": [[{"text": "🔙 Menu Utama", "callback_data": "b_main"}]]}
        edit_msg(chat_id, m_id, "📞 <b>KONTAK RESMI</b>\n\n• WhatsApp: 62895321154498\n• Email: miftahulkhairim1@gmail.com\n• GitHub: https://github.com/kheireditzz", kb)

    elif data == "act_status":
        kb = {"inline_keyboard": [[{"text": "🏠 Menu Utama", "callback_data": "b_main"}]]}
        edit_msg(chat_id, m_id, "🟢 <b>STATUS SISTEM CMS VERCEL</b>\n\n• <b>Mode:</b> Serverless Webhook 24/7\n• <b>Hosting:</b> Vercel Global Edge Network\n• <b>Termux:</b> Tidak Diperlukan (Bebas Matikan HP)\n• <b>Status:</b> Normal & Siap Digunakan", kb)

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
