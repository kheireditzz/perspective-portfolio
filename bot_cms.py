import os
import sys
import json
import time
import re
import subprocess
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BOT_TOKEN = "8762053043:AAEIUgJzTFu_G_lMNunjhZ4LqQMrzbnwnyI"
ADMIN_ID = 5185334850
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BASE_DIR = "/data/data/com.termux/files/home/perspective-portfolio"
DATA_FILE = os.path.join(BASE_DIR, "portfolio-data.js")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# High Performance Connection Pooling
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=20)
session.mount("https://", adapter)
session.mount("http://", adapter)

user_states = {}

def api_call(method, payload=None, files=None):
    try:
        url = f"{API_URL}/{method}"
        if files:
            r = session.post(url, data=payload, files=files, timeout=60)
        elif payload:
            r = session.post(url, json=payload, timeout=10)
        else:
            r = session.get(url, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

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

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'window\.PORTFOLIO_CONFIG\s*=\s*(\{[\s\S]*\});', content)
    if match:
        raw_json = match.group(1)
        raw_json = re.sub(r'//.*', '', raw_json)
        raw_json = re.sub(r'/\*[\s\S]*?\*/', '', raw_json)
        raw_json = re.sub(r',(\s*[\}\]])', r'\1', raw_json)
        try:
            return json.loads(raw_json)
        except Exception:
            pass
    return None

def save_data(data):
    formatted_js = "/**\n * PUSAT DATA PORTOFOLIO MIFTAHUL KHAIRIN (AUTO-MANAGED BY TELEGRAM BOT)\n */\nwindow.PORTFOLIO_CONFIG = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n"
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(formatted_js)

def git_and_deploy():
    try:
        cmd = f"bash {BASE_DIR}/deploy.sh"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
        return res.returncode == 0, res.stdout + res.stderr
    except Exception as e:
        return False, str(e)

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
                {"text": "📞 Kontak / Medsos", "callback_data": "m_contact"}
            ],
            [
                {"text": "🚀 DEPLOY KE WEB LIVE", "callback_data": "act_deploy"}
            ],
            [
                {"text": "🌐 Status", "callback_data": "act_status"},
                {"text": "📥 Backup", "callback_data": "act_backup"}
            ]
        ]
    }

def handle_message(msg):
    try:
        chat_id = msg.get("chat", {}).get("id")
        user_id = msg.get("from", {}).get("id")
        text = msg.get("text", "").strip() if "text" in msg else msg.get("caption", "").strip()
        
        if user_id != ADMIN_ID:
            send_msg(chat_id, "⛔ <b>Akses Ditolak.</b> Bot pribadi.")
            return

        # 1. HANDLE VIDEO
        video_file_id = None
        if "video" in msg:
            video_file_id = msg["video"]["file_id"]
        elif "video_note" in msg:
            video_file_id = msg["video_note"]["file_id"]
        elif "animation" in msg:
            video_file_id = msg["animation"]["file_id"]
        elif "document" in msg:
            doc = msg["document"]
            mime = doc.get("mime_type", "").lower()
            fname = doc.get("file_name", "").lower()
            if mime.startswith("video/") or fname.endswith(('.mp4', '.mov', '.webm', '.mkv', '.avi', '.3gp', '.flv')):
                video_file_id = doc["file_id"]

        if video_file_id:
            status_msg = send_msg(chat_id, "⏳ <i>Mengunduh video...</i>")
            m_id = status_msg.get("result", {}).get("message_id")
            
            info = api_call("getFile", {"file_id": video_file_id})
            file_path = info.get("result", {}).get("file_path")
            if file_path:
                download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                r = session.get(download_url, stream=True, timeout=120)
                
                vid_filename = f"video_{int(time.time())}.mp4"
                local_vid_path = os.path.join(VIDEOS_DIR, vid_filename)
                rel_vid_path = f"videos/{vid_filename}"
                
                with open(local_vid_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)

                d = load_data()
                if d:
                    vid_title = text if text else f"Video Showcase #{len(d.get('videos', [])) + 1}"
                    new_vid = {
                        "id": int(time.time()),
                        "title": vid_title,
                        "desc": "Video demonstrasi & showcase interaktif.",
                        "file": rel_vid_path,
                        "embed": rel_vid_path,
                        "videoUrl": ""
                    }
                    d.setdefault('videos', []).insert(0, new_vid)
                    save_data(d)

                user_states[chat_id] = None
                kb = {
                    "inline_keyboard": [
                        [{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}],
                        [{"text": "🏠 Menu", "callback_data": "b_main"}]
                    ]
                }
                edit_msg(chat_id, m_id, f"✅ <b>Video Tersimpan!</b> 🎥\n• <b>Judul:</b> {vid_title}\n• <b>File:</b> <code>{rel_vid_path}</code>", kb)
            else:
                edit_msg(chat_id, m_id, "⚠️ <b>Video >20MB.</b> Gunakan link YouTube via menu Video.")
            return

        # 2. HANDLE FOTO
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
            status_msg = send_msg(chat_id, "⏳ <i>Mengoptimasi foto...</i>")
            m_id = status_msg.get("result", {}).get("message_id")
            
            info = api_call("getFile", {"file_id": photo_file_id})
            file_path = info.get("result", {}).get("file_path")
            if file_path:
                download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
                r = session.get(download_url, timeout=60)
                
                p_path = os.path.join(BASE_DIR, "profile.jpg")
                fav_ico = os.path.join(BASE_DIR, "favicon.ico")
                fav_jpg = os.path.join(BASE_DIR, "favicon.jpg")
                apple_ico = os.path.join(BASE_DIR, "apple-touch-icon.png")
                
                with open(p_path, 'wb') as f: f.write(r.content)
                with open(fav_ico, 'wb') as f: f.write(r.content)
                with open(fav_jpg, 'wb') as f: f.write(r.content)
                with open(apple_ico, 'wb') as f: f.write(r.content)

                d = load_data()
                if d:
                    d['profile']['photo'] = 'profile.jpg'
                    d['profile']['logo'] = 'profile.jpg'
                    save_data(d)

                user_states[chat_id] = None
                kb = {
                    "inline_keyboard": [
                        [{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}],
                        [{"text": "🏠 Menu", "callback_data": "b_main"}]
                    ]
                }
                edit_msg(chat_id, m_id, "✅ <b>Foto Profil & Favicon Diperbarui!</b> 📸\nKlik Deploy untuk menerapkan ke web.", kb)
            else:
                edit_msg(chat_id, m_id, "❌ Gagal mengunduh foto.")
            return

        # 3. COMMANDS
        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ["/start", "/menu"]:
                user_states[chat_id] = None
                welcome = (
                    "🎛️ <b>PORTFOLIO DASHBOARD CMS</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "👤 <b>Miftahul Khairin</b>\n"
                    "🌐 portofolio.kheireditz.my.id\n\n"
                    "Pilih kategori di bawah untuk mengelola website:"
                )
                send_msg(chat_id, welcome, main_menu())
                return

            elif cmd == "/help":
                help_text = (
                    "📖 <b>DAFTAR PERINTAH CEPAT</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "• /menu — Buka Dashboard Utama\n"
                    "• /deploy — Deploy ke Web Live\n"
                    "• /status — Status Web & Git\n"
                    "• /backup — Download File Data\n"
                    "• /setnama [Nama] — Ganti Nama\n"
                    "• /setprofesi [Profesi] — Ganti Profesi\n"
                    "• /setbio [Bio] — Ganti Bio\n"
                    "• /setwa [No WA] — Ganti Nomor WA\n"
                    "• /batal — Batalkan Input"
                )
                send_msg(chat_id, help_text)
                return

            elif cmd == "/deploy":
                status_m = send_msg(chat_id, "⏳ <i>Mendeploy ke Vercel & GitHub...</i>")
                m_id = status_m.get("result", {}).get("message_id")
                succ, log = git_and_deploy()
                kb = {
                    "inline_keyboard": [
                        [{"text": "🌐 Buka Web Live", "url": "https://portofolio.kheireditz.my.id/"}],
                        [{"text": "🏠 Menu", "callback_data": "b_main"}]
                    ]
                }
                if succ:
                    edit_msg(chat_id, m_id, "✅ <b>DEPLOY SUKSES!</b> 🚀\nWebsite live dan terupdate.", kb)
                else:
                    edit_msg(chat_id, m_id, f"❌ Deploy Gagal:\n<code>{log[-200:]}</code>")
                return

            elif cmd == "/status":
                res = subprocess.run(f"git -C {BASE_DIR} log -1 --pretty=format:'%h - %s (%cr)'", shell=True, capture_output=True, text=True)
                status_text = (
                    "🌐 <b>STATUS SISTEM</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    f"• <b>Domain:</b> portofolio.kheireditz.my.id\n"
                    f"• <b>Git:</b> <code>{res.stdout}</code>\n"
                    f"• <b>CMS Bot:</b> 🟢 Aktif 24/7"
                )
                send_msg(chat_id, status_text)
                return

            elif cmd == "/backup":
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'rb') as f:
                        api_call("sendDocument", {"chat_id": chat_id, "caption": "📦 Backup Data Web"}, files={"document": f})
                return

            elif cmd in ["/batal", "/cancel"]:
                user_states[chat_id] = None
                send_msg(chat_id, "👌 Input dibatalkan.", main_menu())
                return

            elif cmd in ["/setnama", "/setprofesi", "/setbio", "/setwa"]:
                if not arg:
                    send_msg(chat_id, f"⚠️ Format: <code>{cmd} [nilai baru]</code>")
                    return
                d = load_data()
                if not d: return
                if cmd == "/setnama": d['profile']['name'] = arg; d['profile']['headerTitle'] = arg
                elif cmd == "/setprofesi": d['profile']['profession'] = arg
                elif cmd == "/setbio": d['profile']['bio'] = arg
                elif cmd == "/setwa": d['profile']['whatsapp'] = re.sub(r'[^0-9]', '', arg)
                save_data(d)
                kb = {
                    "inline_keyboard": [
                        [{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}],
                        [{"text": "🏠 Menu", "callback_data": "b_main"}]
                    ]
                }
                send_msg(chat_id, f"✅ <b>Data Disimpan!</b>\n<code>{arg}</code>", kb)
                return

        # 4. HANDLE GUIDED FORM INPUTS
        state = user_states.get(chat_id)
        if not state:
            send_msg(chat_id, "💡 Ketik /menu untuk membuka dashboard.")
            return

        action = state.get("action")
        d = load_data()
        if not d: return

        if action == "set_photo_url":
            url = text.strip()
            d['profile']['photo'] = url
            d['profile']['logo'] = url
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Foto Profil", url, "m_photo")

        elif action == "edit_profile_field":
            field = state.get("field")
            if field == "name": d['profile']['name'] = text; d['profile']['headerTitle'] = text
            elif field == "profession": d['profile']['profession'] = text
            elif field == "location": d['profile']['location'] = text
            elif field == "status": d['profile']['status'] = text
            elif field == "bio": d['profile']['bio'] = text
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Profil", text, "m_profile")

        elif action == "edit_contact_field":
            field = state.get("field")
            if field == "wa": d['profile']['whatsapp'] = re.sub(r'[^0-9]', '', text)
            elif field == "email": d['profile']['email'] = text
            elif field == "ig": d['profile']['socialLinks']['instagram'] = text
            elif field == "tiktok": d['profile']['socialLinks']['tiktok'] = text
            elif field == "github": d['profile']['socialLinks']['github'] = text
            elif field == "tg": d['profile']['telegram'] = text
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Kontak", text, "m_contact")

        elif action == "edit_prod_field":
            field = state.get("field"); idx = state.get("idx")
            if idx < len(d.get('products', [])):
                d['products'][idx][field] = text
                save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, f"Produk #{idx+1}", text, "m_products")

        elif action == "edit_proj_field":
            field = state.get("field"); idx = state.get("idx")
            if idx < len(d.get('projects', [])):
                d['projects'][idx][field] = text
                save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, f"Proyek #{idx+1}", text, "m_projects")

        elif action == "edit_gal_field":
            field = state.get("field"); idx = state.get("idx")
            if idx < len(d.get('gallery', [])):
                d['gallery'][idx][field] = text
                save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, f"Galeri #{idx+1}", text, "m_gallery")

        elif action == "edit_vid_field":
            field = state.get("field"); idx = state.get("idx")
            if idx < len(d.get('videos', [])):
                d['videos'][idx][field] = text
                save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, f"Video #{idx+1}", text, "m_videos")

        elif action == "edit_card3d_title":
            card_key = state.get("card_key")
            user_states[chat_id] = {"action": "edit_card3d_desc", "card_key": card_key, "title": text}
            send_msg(chat_id, f"🃏 Judul: <b>{text}</b>\n\nKetik <b>Deskripsi Kartu</b>:")

        elif action == "edit_card3d_desc":
            card_key = state.get("card_key"); title = state.get("title")
            if 'cards3D' in d and card_key in d['cards3D']:
                d['cards3D'][card_key]['title'] = title
                d['cards3D'][card_key]['desc'] = text
                save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, f"Kartu 3D", f"{title}", "m_cards3d")

        # Add Product flow
        elif action == "add_prod_1":
            user_states[chat_id] = {"action": "add_prod_2", "title": text}
            send_msg(chat_id, f"📦 Judul: <b>{text}</b>\n\nKetik <b>Harga</b> (contoh: <code>Rp 199.000</code>):")
        elif action == "add_prod_2":
            user_states[chat_id] = {"action": "add_prod_3", "title": state.get("title"), "price": text}
            send_msg(chat_id, f"💵 Harga: <b>{text}</b>\n\nKetik <b>Deskripsi Singkat</b>:")
        elif action == "add_prod_3":
            new_prod = {
                "id": int(time.time()),
                "badge": "PRODUK BARU",
                "title": state.get("title"),
                "desc": text,
                "price": state.get("price"),
                "originalPrice": "",
                "demoUrl": "https://portofolio.kheireditz.my.id",
                "features": ["Source code siap pakai", "Support & Garansi"]
            }
            d.setdefault('products', []).insert(0, new_prod)
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Produk Baru", state.get("title"), "m_products")

        # Add Project flow
        elif action == "add_proj_1":
            user_states[chat_id] = {"action": "add_proj_2", "title": text}
            send_msg(chat_id, f"💼 Judul: <b>{text}</b>\n\nKetik <b>Tech Stack</b> (contoh: <code>Next.js • Node.js</code>):")
        elif action == "add_proj_2":
            user_states[chat_id] = {"action": "add_proj_3", "title": state.get("title"), "tech": text}
            send_msg(chat_id, f"⚙️ Tech: <b>{text}</b>\n\nKetik <b>Deskripsi Singkat</b>:")
        elif action == "add_proj_3":
            new_proj = {
                "id": int(time.time()),
                "category": "KARYA UNGGULAN",
                "title": state.get("title"),
                "desc": text,
                "tech": state.get("tech"),
                "link": "https://github.com/kheireditzz",
                "githubUrl": "https://github.com/kheireditzz",
                "icon": "layers"
            }
            d.setdefault('projects', []).insert(0, new_proj)
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Proyek Baru", state.get("title"), "m_projects")

        # Add Gallery flow
        elif action == "add_gal_1":
            user_states[chat_id] = {"action": "add_gal_2", "title": text}
            send_msg(chat_id, f"🖼️ Judul: <b>{text}</b>\n\nKetik <b>Tag / Kategori</b> (contoh: <code>DOKUMENTASI</code>):")
        elif action == "add_gal_2":
            user_states[chat_id] = {"action": "add_gal_3", "title": state.get("title"), "tag": text}
            send_msg(chat_id, f"🏷️ Tag: <b>{text}</b>\n\nKetik <b>URL Gambar</b> (atau ketik <code>profile.jpg</code>):")
        elif action == "add_gal_3":
            new_gal = {
                "id": int(time.time()),
                "tag": state.get("tag"),
                "title": state.get("title"),
                "img": text,
                "desc": "Dokumentasi hasil karya dan arsitektur sistem."
            }
            d.setdefault('gallery', []).insert(0, new_gal)
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Foto Galeri Baru", state.get("title"), "m_gallery")

        # Add Video flow
        elif action == "add_vid_1":
            user_states[chat_id] = {"action": "add_vid_2", "title": text}
            send_msg(chat_id, f"🎬 Judul: <b>{text}</b>\n\nKirimkan <b>Link YouTube / URL Video</b>:")
        elif action == "add_vid_2":
            url = text.strip()
            title = state.get("title")
            
            is_direct_mp4 = bool(re.search(r'\.(mp4|webm|mov|ogg)$', url, re.I))
            if is_direct_mp4:
                embed_src = url
            else:
                yt_id = "dQw4w9WgXcQ"
                m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
                if m: yt_id = m.group(1)
                embed_src = f"https://www.youtube-nocookie.com/embed/{yt_id}?controls=1&rel=0"

            new_vid = {
                "id": int(time.time()),
                "title": title,
                "desc": "Video showcase resmi.",
                "embed": embed_src,
                "file": url if is_direct_mp4 else "",
                "videoUrl": url
            }
            d.setdefault('videos', []).insert(0, new_vid)
            save_data(d)
            user_states[chat_id] = None
            send_finish(chat_id, "Video Baru", title, "m_videos")
    except Exception as e:
        print(f"Error in handle_message: {e}")

def handle_callback(call):
    try:
        chat_id = call.get("message", {}).get("chat", {}).get("id")
        m_id = call.get("message", {}).get("message_id")
        user_id = call.get("from", {}).get("id")
        action = call.get("data", "")
        call_id = call.get("id")
        answer_callback(call_id)

        if user_id != ADMIN_ID:
            return

        d = load_data()

        if action == "b_main":
            user_states[chat_id] = None
            text = (
                "🎛️ <b>PORTFOLIO DASHBOARD CMS</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👤 <b>Miftahul Khairin</b>\n"
                "🌐 portofolio.kheireditz.my.id\n\n"
                "Pilih kategori untuk dikelola:"
            )
            edit_msg(chat_id, m_id, text, main_menu())

        elif action == "act_deploy":
            edit_msg(chat_id, m_id, "⏳ <i>Mendeploy ke Vercel & GitHub...</i>")
            succ, log = git_and_deploy()
            kb = {
                "inline_keyboard": [
                    [{"text": "🌐 Buka Web Live", "url": "https://portofolio.kheireditz.my.id/"}],
                    [{"text": "🏠 Menu", "callback_data": "b_main"}]
                ]
            }
            if succ:
                edit_msg(chat_id, m_id, "✅ <b>DEPLOY SUKSES!</b> 🚀\nWebsite live dan terupdate.", kb)
            else:
                edit_msg(chat_id, m_id, f"❌ Deploy Gagal:\n<code>{log[-200:]}</code>")

        elif action == "act_status":
            res = subprocess.run(f"git -C {BASE_DIR} log -1 --pretty=format:'%h - %s (%cr)'", shell=True, capture_output=True, text=True)
            kb = {"inline_keyboard": [[{"text": "🏠 Menu", "callback_data": "b_main"}]]}
            edit_msg(chat_id, m_id, f"🌐 <b>STATUS SISTEM</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Domain:</b> portofolio.kheireditz.my.id\n• <b>Git:</b> <code>{res.stdout}</code>\n• <b>CMS:</b> 🟢 Aktif", kb)

        elif action == "act_backup":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'rb') as f:
                    api_call("sendDocument", {"chat_id": chat_id, "caption": "📦 Backup Data Web"}, files={"document": f})

        elif action == "m_profile":
            p = d.get('profile', {}) if d else {}
            kb = {
                "inline_keyboard": [
                    [{"text": "✏️ Nama", "callback_data": "ed_p_name"}, {"text": "💼 Profesi", "callback_data": "ed_p_profession"}],
                    [{"text": "📍 Lokasi", "callback_data": "ed_p_location"}, {"text": "🟢 Status", "callback_data": "ed_p_status"}],
                    [{"text": "📝 Edit Bio", "callback_data": "ed_p_bio"}],
                    [{"text": "🔙 Menu", "callback_data": "b_main"}]
                ]
            }
            text = f"👤 <b>PROFIL & BIO</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Nama:</b> {p.get('name')}\n• <b>Profesi:</b> {p.get('profession')}\n• <b>Lokasi:</b> {p.get('location')}\n• <b>Status:</b> {p.get('status')}\n• <b>Bio:</b> {p.get('bio')}"
            edit_msg(chat_id, m_id, text, kb)

        elif action == "m_contact":
            p = d.get('profile', {}) if d else {}
            soc = p.get('socialLinks', {})
            kb = {
                "inline_keyboard": [
                    [{"text": "💬 WhatsApp", "callback_data": "ed_c_wa"}, {"text": "✉️ Email", "callback_data": "ed_c_email"}],
                    [{"text": "📸 Instagram", "callback_data": "ed_c_ig"}, {"text": "🎬 TikTok", "callback_data": "ed_c_tiktok"}],
                    [{"text": "🐙 GitHub", "callback_data": "ed_c_github"}, {"text": "✈️ Telegram", "callback_data": "ed_c_tg"}],
                    [{"text": "🔙 Menu", "callback_data": "b_main"}]
                ]
            }
            text = f"📞 <b>KONTAK & SOSMED</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>WhatsApp:</b> +{p.get('whatsapp')}\n• <b>Email:</b> {p.get('email')}\n• <b>IG:</b> {soc.get('instagram')}\n• <b>TikTok:</b> {soc.get('tiktok')}\n• <b>GitHub:</b> {soc.get('github')}"
            edit_msg(chat_id, m_id, text, kb)

        elif action == "m_photo":
            p = d.get('profile', {}) if d else {}
            kb = {
                "inline_keyboard": [
                    [{"text": "🔗 Input Link URL Gambar", "callback_data": "set_photo_link"}],
                    [{"text": "🔙 Menu", "callback_data": "b_main"}]
                ]
            }
            text = f"📸 <b>FOTO PROFIL & FAVICON</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Sumber:</b> <code>{p.get('photo')}</code>\n\n💡 <i>Kirim foto langsung ke chat atau klik tombol link:</i>"
            edit_msg(chat_id, m_id, text, kb)

        elif action == "set_photo_link":
            user_states[chat_id] = {"action": "set_photo_url"}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_photo"}]]}
            edit_msg(chat_id, m_id, "🔗 Ketik <b>Link URL Gambar</b>:", kb)

        elif action == "m_products":
            prods = d.get('products', []) if d else []
            kb_rows = [[{"text": f"📦 {it.get('title')} ({it.get('price')})", "callback_data": f"vp_{i}"}] for i, it in enumerate(prods)]
            kb_rows.append([{"text": "➕ Tambah Produk", "callback_data": "add_prod"}])
            kb_rows.append([{"text": "🔙 Menu", "callback_data": "b_main"}])
            edit_msg(chat_id, m_id, f"🛍️ <b>TOKO DIGITAL ({len(prods)} Produk)</b>\nPilih produk untuk kelola:", {"inline_keyboard": kb_rows})

        elif action.startswith("vp_"):
            idx = int(action.split("_")[1]); prods = d.get('products', [])
            if idx < len(prods):
                p = prods[idx]
                kb = {
                    "inline_keyboard": [
                        [{"text": "✏️ Judul", "callback_data": f"ed_pr_title_{idx}"}, {"text": "💵 Harga", "callback_data": f"ed_pr_price_{idx}"}],
                        [{"text": "🏷️ Badge", "callback_data": f"ed_pr_badge_{idx}"}, {"text": "📝 Deskripsi", "callback_data": f"ed_pr_desc_{idx}"}],
                        [{"text": "🗑️ Hapus Produk", "callback_data": f"dp_{idx}"}],
                        [{"text": "🔙 Daftar Produk", "callback_data": "m_products"}]
                    ]
                }
                text = f"📦 <b>PRODUK #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {p.get('title')}\n• <b>Harga:</b> {p.get('price')}\n• <b>Badge:</b> {p.get('badge')}\n• <b>Deskripsi:</b> {p.get('desc')}"
                edit_msg(chat_id, m_id, text, kb)

        elif action.startswith("dp_"):
            idx = int(action.split("_")[1])
            if d and 'products' in d and idx < len(d['products']):
                rem = d['products'].pop(idx); save_data(d)
                kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🛍️ Produk", "callback_data": "m_products"}]]}
                edit_msg(chat_id, m_id, f"✅ Produk <b>{rem.get('title')}</b> dihapus!", kb)

        elif action == "add_prod":
            user_states[chat_id] = {"action": "add_prod_1"}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_products"}]]}
            edit_msg(chat_id, m_id, "➕ <b>TAMBAH PRODUK</b>\nKetik <b>Judul Produk</b>:", kb)

        elif action == "m_projects":
            projs = d.get('projects', []) if d else []
            kb_rows = [[{"text": f"💼 {it.get('title')}", "callback_data": f"vproj_{i}"}] for i, it in enumerate(projs)]
            kb_rows.append([{"text": "➕ Tambah Proyek", "callback_data": "add_proj"}])
            kb_rows.append([{"text": "🔙 Menu", "callback_data": "b_main"}])
            edit_msg(chat_id, m_id, f"💼 <b>PORTOFOLIO ({len(projs)} Proyek)</b>\nPilih proyek untuk kelola:", {"inline_keyboard": kb_rows})

        elif action.startswith("vproj_"):
            idx = int(action.split("_")[1]); projs = d.get('projects', [])
            if idx < len(projs):
                p = projs[idx]
                kb = {
                    "inline_keyboard": [
                        [{"text": "✏️ Judul", "callback_data": f"ed_pj_title_{idx}"}, {"text": "⚙️ Tech", "callback_data": f"ed_pj_tech_{idx}"}],
                        [{"text": "📝 Deskripsi", "callback_data": f"ed_pj_desc_{idx}"}, {"text": "🗑️ Hapus Proyek", "callback_data": f"dproj_{idx}"}],
                        [{"text": "🔙 Daftar Proyek", "callback_data": "m_projects"}]
                    ]
                }
                text = f"💼 <b>PROYEK #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {p.get('title')}\n• <b>Tech:</b> {p.get('tech')}\n• <b>Deskripsi:</b> {p.get('desc')}"
                edit_msg(chat_id, m_id, text, kb)

        elif action.startswith("dproj_"):
            idx = int(action.split("_")[1])
            if d and 'projects' in d and idx < len(d['projects']):
                rem = d['projects'].pop(idx); save_data(d)
                kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "💼 Proyek", "callback_data": "m_projects"}]]}
                edit_msg(chat_id, m_id, f"✅ Proyek <b>{rem.get('title')}</b> dihapus!", kb)

        elif action == "add_proj":
            user_states[chat_id] = {"action": "add_proj_1"}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_projects"}]]}
            edit_msg(chat_id, m_id, "➕ <b>TAMBAH PROYEK</b>\nKetik <b>Judul Proyek</b>:", kb)

        elif action == "m_gallery":
            gals = d.get('gallery', []) if d else []
            kb_rows = [[{"text": f"🖼️ {it.get('title')} [{it.get('tag')}]", "callback_data": f"vg_{i}"}] for i, it in enumerate(gals)]
            kb_rows.append([{"text": "➕ Tambah Foto", "callback_data": "add_gal"}])
            kb_rows.append([{"text": "🔙 Menu", "callback_data": "b_main"}])
            edit_msg(chat_id, m_id, f"🖼️ <b>GALERI FOTO ({len(gals)} Foto)</b>\nPilih foto untuk kelola:", {"inline_keyboard": kb_rows})

        elif action.startswith("vg_"):
            idx = int(action.split("_")[1]); gals = d.get('gallery', [])
            if idx < len(gals):
                g = gals[idx]
                kb = {
                    "inline_keyboard": [
                        [{"text": "✏️ Judul", "callback_data": f"ed_gl_title_{idx}"}, {"text": "🏷️ Tag", "callback_data": f"ed_gl_tag_{idx}"}],
                        [{"text": "🔗 URL", "callback_data": f"ed_gl_img_{idx}"}, {"text": "🗑️ Hapus Foto", "callback_data": f"dg_{idx}"}],
                        [{"text": "🔙 Galeri", "callback_data": "m_gallery"}]
                    ]
                }
                text = f"🖼️ <b>FOTO #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {g.get('title')}\n• <b>Tag:</b> {g.get('tag')}\n• <b>URL:</b> <code>{g.get('img')}</code>"
                edit_msg(chat_id, m_id, text, kb)

        elif action.startswith("dg_"):
            idx = int(action.split("_")[1])
            if d and 'gallery' in d and idx < len(d['gallery']):
                rem = d['gallery'].pop(idx); save_data(d)
                kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🖼️ Galeri", "callback_data": "m_gallery"}]]}
                edit_msg(chat_id, m_id, f"✅ Foto <b>{rem.get('title')}</b> dihapus!", kb)

        elif action == "add_gal":
            user_states[chat_id] = {"action": "add_gal_1"}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_gallery"}]]}
            edit_msg(chat_id, m_id, "➕ <b>TAMBAH FOTO</b>\nKetik <b>Judul Foto</b>:", kb)

        elif action == "m_videos":
            vids = d.get('videos', []) if d else []
            kb_rows = [[{"text": f"🎬 {it.get('title')}", "callback_data": f"vv_{i}"}] for i, it in enumerate(vids)]
            kb_rows.append([{"text": "➕ Tambah Video (Link)", "callback_data": "add_vid"}])
            kb_rows.append([{"text": "🔙 Menu", "callback_data": "b_main"}])
            edit_msg(chat_id, m_id, f"🎥 <b>VIDEO SHOWCASE ({len(vids)} Video)</b>\nKirim file MP4 ke chat atau klik Tambah:", {"inline_keyboard": kb_rows})

        elif action.startswith("vv_"):
            idx = int(action.split("_")[1]); vids = d.get('videos', [])
            if idx < len(vids):
                v = vids[idx]
                kb = {
                    "inline_keyboard": [
                        [{"text": "✏️ Judul", "callback_data": f"ed_vd_title_{idx}"}, {"text": "🔗 URL", "callback_data": f"ed_vd_embed_{idx}"}],
                        [{"text": "🗑️ Hapus Video", "callback_data": f"dv_{idx}"}],
                        [{"text": "🔙 Video", "callback_data": "m_videos"}]
                    ]
                }
                src = v.get('file') or v.get('embed') or v.get('videoUrl')
                text = f"🎬 <b>VIDEO #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {v.get('title')}\n• <b>Sumber:</b> <code>{src}</code>"
                edit_msg(chat_id, m_id, text, kb)

        elif action.startswith("dv_"):
            idx = int(action.split("_")[1])
            if d and 'videos' in d and idx < len(d['videos']):
                rem = d['videos'].pop(idx); save_data(d)
                kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🎥 Video", "callback_data": "m_videos"}]]}
                edit_msg(chat_id, m_id, f"✅ Video <b>{rem.get('title')}</b> dihapus!", kb)

        elif action == "add_vid":
            user_states[chat_id] = {"action": "add_vid_1"}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_videos"}]]}
            edit_msg(chat_id, m_id, "🎬 <b>TAMBAH VIDEO</b>\nKetik <b>Judul Video</b>:", kb)

        elif action == "m_cards3d":
            c = d.get('cards3D', {}) if d else {}
            kb = {
                "inline_keyboard": [
                    [{"text": f"1️⃣ {c.get('skill', {}).get('title', 'Skill')}", "callback_data": "ed_c3_skill"}],
                    [{"text": f"2️⃣ {c.get('asset', {}).get('title', 'Asset')}", "callback_data": "ed_c3_asset"}],
                    [{"text": f"3️⃣ {c.get('video', {}).get('title', 'Video')}", "callback_data": "ed_c3_video"}],
                    [{"text": "🔙 Menu", "callback_data": "b_main"}]
                ]
            }
            edit_msg(chat_id, m_id, "🃏 <b>KARTU 3D</b>\nPilih kartu yang ingin diedit:", kb)

        elif action.startswith("ed_c3_"):
            key = action.replace("ed_c3_", "")
            user_states[chat_id] = {"action": "edit_card3d_title", "card_key": key}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_cards3d"}]]}
            edit_msg(chat_id, m_id, f"🃏 Ketik <b>Judul Baru</b> untuk [<code>{key}</code>]:", kb)

        elif action.startswith("ed_p_"):
            field = action.replace("ed_p_", "")
            user_states[chat_id] = {"action": "edit_profile_field", "field": field}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_profile"}]]}
            edit_msg(chat_id, m_id, f"✏️ Ketik <b>nilai baru</b> untuk [<code>{field}</code>]:", kb)

        elif action.startswith("ed_c_"):
            field = action.replace("ed_c_", "")
            user_states[chat_id] = {"action": "edit_contact_field", "field": field}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": "m_contact"}]]}
            edit_msg(chat_id, m_id, f"📞 Ketik <b>nilai baru</b> untuk [<code>{field}</code>]:", kb)

        elif action.startswith("ed_pr_"):
            parts = action.split("_"); field = parts[2]; idx = int(parts[3])
            user_states[chat_id] = {"action": "edit_prod_field", "field": field, "idx": idx}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": f"vp_{idx}"}]]}
            edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b>:", kb)

        elif action.startswith("ed_pj_"):
            parts = action.split("_"); field = parts[2]; idx = int(parts[3])
            user_states[chat_id] = {"action": "edit_proj_field", "field": field, "idx": idx}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": f"vproj_{idx}"}]]}
            edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b>:", kb)

        elif action.startswith("ed_gl_"):
            parts = action.split("_"); field = parts[2]; idx = int(parts[3])
            user_states[chat_id] = {"action": "edit_gal_field", "field": field, "idx": idx}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": f"vg_{idx}"}]]}
            edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b>:", kb)

        elif action.startswith("ed_vd_"):
            parts = action.split("_"); field = parts[2]; idx = int(parts[3])
            user_states[chat_id] = {"action": "edit_vid_field", "field": field, "idx": idx}
            kb = {"inline_keyboard": [[{"text": "❌ Batal", "callback_data": f"vv_{idx}"}]]}
            edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b>:", kb)
    except Exception as e:
        print(f"Error in handle_callback: {e}")

def send_finish(chat_id, category, val, back_menu):
    kb = {
        "inline_keyboard": [
            [{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}],
            [{"text": "🔙 Kembali", "callback_data": back_menu}, {"text": "🏠 Menu", "callback_data": "b_main"}]
        ]
    }
    send_msg(chat_id, f"✅ <b>{category} Disimpan!</b>\n<code>{val}</code>", kb)

def run_loop():
    print("Ultra Fast Instant Polling running with Keep-Alive...")
    offset = 0
    while True:
        try:
            res = api_call("getUpdates", {"offset": offset, "timeout": 2, "limit": 20})
            if res.get("ok"):
                updates = res.get("result", [])
                for u in updates:
                    offset = u["update_id"] + 1
                    if "message" in u:
                        handle_message(u["message"])
                    elif "callback_query" in u:
                        handle_callback(u["callback_query"])
            time.sleep(0.01)
        except Exception as e:
            print(f"Loop reconnect: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    run_loop()
