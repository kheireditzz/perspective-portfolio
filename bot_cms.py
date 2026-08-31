import os
import sys
import json
import time
import re
import subprocess
import requests

BOT_TOKEN = "8762053043:AAEIUgJzTFu_G_lMNunjhZ4LqQMrzbnwnyI"
ADMIN_ID = 5185334850
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

BASE_DIR = "/data/data/com.termux/files/home/perspective-portfolio"
DATA_FILE = os.path.join(BASE_DIR, "portfolio-data.js")

user_states = {}

def api_post(endpoint, payload=None, files=None):
    try:
        url = f"{API_URL}/{endpoint}"
        if files:
            r = requests.post(url, data=payload, files=files, timeout=30)
        else:
            r = requests.post(url, json=payload, timeout=30)
        return r.json()
    except Exception as e:
        print(f"API error in {endpoint}: {e}")
        return {}

def api_get(endpoint, params=None):
    try:
        url = f"{API_URL}/{endpoint}"
        r = requests.get(url, params=params, timeout=30)
        return r.json()
    except Exception as e:
        print(f"API error in {endpoint}: {e}")
        return {}

def send_typing(chat_id):
    api_post("sendChatAction", {"chat_id": chat_id, "action": "typing"})

def send_msg(chat_id, text, reply_markup=None):
    send_typing(chat_id)
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_post("sendMessage", payload)

def edit_msg(chat_id, message_id, text, reply_markup=None):
    send_typing(chat_id)
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_post("editMessageText", payload)

def answer_callback(callback_query_id, text=None):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    api_post("answerCallbackQuery", payload)

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
        cmd = f"""cd {BASE_DIR} && \
git add . && \
git commit -m "update: content update via Telegram Bot CMS" && \
git push origin main && \
vercel deploy --prod --yes --cwd {BASE_DIR}"""
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
        return res.returncode == 0, res.stdout + res.stderr
    except Exception as e:
        return False, str(e)

def main_menu():
    return {
        "inline_keyboard": [
            [
                {"text": "👤 Profil & Bio", "callback_data": "m_profile"},
                {"text": "📸 Foto & Favicon", "callback_data": "m_photo"}
            ],
            [
                {"text": "🛍️ Toko Digital", "callback_data": "m_products"},
                {"text": "💼 Portofolio Proyek", "callback_data": "m_projects"}
            ],
            [
                {"text": "🖼️ Galeri Foto", "callback_data": "m_gallery"},
                {"text": "🎥 Video YouTube", "callback_data": "m_videos"}
            ],
            [
                {"text": "🃏 3D Canvas Cards", "callback_data": "m_cards3d"},
                {"text": "📞 Kontak & Medsos", "callback_data": "m_contact"}
            ],
            [
                {"text": "🚀 DEPLOY KE VERCEL (LIVE)", "callback_data": "act_deploy"}
            ],
            [
                {"text": "🌐 Cek Status Web", "callback_data": "act_status"},
                {"text": "📥 Backup Data Web", "callback_data": "act_backup"}
            ]
        ]
    }

def handle_message(msg):
    chat_id = msg.get("chat", {}).get("id")
    user_id = msg.get("from", {}).get("id")
    text = msg.get("text", "").strip()
    
    if user_id != ADMIN_ID:
        send_msg(chat_id, "⛔ <b>Akses Ditolak.</b> Bot ini khusus untuk pemilik portfolio.")
        return

    # Handle Photo Upload
    if "photo" in msg:
        photos = msg.get("photo")
        largest_photo = photos[-1]
        file_id = largest_photo.get("file_id")
        
        info = api_get("getFile", {"file_id": file_id})
        file_path = info.get("result", {}).get("file_path")
        if file_path:
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            r = requests.get(download_url)
            
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

            kb = {
                "inline_keyboard": [
                    [{"text": "🚀 DEPLOY SEKARANG", "callback_data": "act_deploy"}],
                    [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                ]
            }
            send_msg(chat_id, "✅ <b>FOTO BERHASIL DIUPDATE!</b> 📸\nFoto Profil, Favicon browser, dan Apple Touch Icon telah diperbarui.\n\nKlik Deploy untuk mempublikasikan!", kb)
        return

    # Commands
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ["/start", "/menu"]:
            user_states[chat_id] = None
            welcome = (
                "⚡ <b>PORTFOLIO SUPER CMS TELEGRAM 24/7</b> ⚡\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Halo <b>Miftahul Khairin</b>!\n"
                "Kelola seluruh website Anda langsung dari sini secara lengkap:\n\n"
                "• 👤 Profil, Nama & Bio\n"
                "• 🛍️ Produk Toko Digital (Tambah/Hapus/Edit)\n"
                "• 💼 Portofolio Karya & Proyek\n"
                "• 🖼️ Galeri Foto Dokumentasi\n"
                "• 🎥 Video YouTube Showcase\n"
                "• 🃏 3D Canvas Depth Cards\n"
                "• 📞 WhatsApp, IG, TikTok & Email\n"
                "• 📸 Upload Foto & Favicon Langsung\n\n"
                "👇 <b>Pilih menu yang ingin dikelola:</b>"
            )
            send_msg(chat_id, welcome, main_menu())
            return

        elif cmd == "/help":
            help_text = (
                "📖 <b>PANDUAN LENGKAP CMS</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "• /menu - Menu Utama Dashboard\n"
                "• /deploy - Langsung Deploy ke Web Live\n"
                "• /status - Cek status commit & web\n"
                "• /backup - Download file backup\n"
                "• /setnama [Nama] - Ganti Nama Lengkap\n"
                "• /setprofesi [Profesi] - Ganti Profesi\n"
                "• /setbio [Bio] - Ganti Bio\n"
                "• /setwa [Nomor WA] - Ganti No WhatsApp\n"
                "• /batal - Batalkan input"
            )
            send_msg(chat_id, help_text)
            return

        elif cmd == "/deploy":
            status_m = send_msg(chat_id, "⏳ <b>Sedang melakukan Deploy ke Vercel & GitHub...</b>")
            m_id = status_m.get("result", {}).get("message_id")
            succ, log = git_and_deploy()
            kb = {
                "inline_keyboard": [
                    [{"text": "🌐 Buka Web Live", "url": "https://portofolio.kheireditz.my.id/"}],
                    [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                ]
            }
            if succ:
                edit_msg(chat_id, m_id, "✅ <b>DEPLOY BERHASIL 100%!</b> 🚀\nPerubahan sudah live di:\n👉 https://portofolio.kheireditz.my.id/", kb)
            else:
                edit_msg(chat_id, m_id, f"❌ Deploy Gagal:\n<code>{log[-300:]}</code>")
            return

        elif cmd == "/status":
            res = subprocess.run(f"git -C {BASE_DIR} log -1 --pretty=format:'%h - %s (%cr)'", shell=True, capture_output=True, text=True)
            status_text = (
                "🌐 <b>STATUS WEB SAAT INI</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "• <b>URL:</b> https://portofolio.kheireditz.my.id/\n"
                "• <b>Repository:</b> kheireditzz/perspective-portfolio\n"
                f"• <b>Commit Terakhir:</b> <code>{res.stdout}</code>\n"
                "• <b>Bot CMS:</b> 🟢 Aktif 24/7 (Daemon)"
            )
            send_msg(chat_id, status_text)
            return

        elif cmd == "/backup":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'rb') as f:
                    api_post("sendDocument", {"chat_id": chat_id, "caption": "📦 Backup portfolio-data.js"}, files={"document": f})
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
                    [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
                ]
            }
            send_msg(chat_id, f"✅ <b>Berhasil Disimpan!</b>\nNilai baru: <code>{arg}</code>", kb)
            return

    # Handle Guided Form Inputs
    state = user_states.get(chat_id)
    if not state:
        send_msg(chat_id, "💡 Gunakan /menu untuk membuka tombol menu CMS, atau /help untuk melihat bantuan.")
        return

    action = state.get("action")
    d = load_data()
    if not d: return

    if action == "edit_profile_field":
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
        send_finish(chat_id, "Kontak / Medsos", text, "m_contact")

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
        send_msg(chat_id, f"🃏 Judul: <b>{text}</b>\n\nSekarang ketik <b>Deskripsi Kartu 3D</b>:")

    elif action == "edit_card3d_desc":
        card_key = state.get("card_key"); title = state.get("title")
        if 'cards3D' in d and card_key in d['cards3D']:
            d['cards3D'][card_key]['title'] = title
            d['cards3D'][card_key]['desc'] = text
            save_data(d)
        user_states[chat_id] = None
        send_finish(chat_id, f"Kartu 3D [{card_key}]", f"{title} - {text}", "m_cards3d")

    # Add Product flow
    elif action == "add_prod_1":
        user_states[chat_id] = {"action": "add_prod_2", "title": text}
        send_msg(chat_id, f"📦 Judul: <b>{text}</b>\n\nSekarang ketik <b>Harga</b> (contoh: <code>Rp 199.000</code>):")
    elif action == "add_prod_2":
        user_states[chat_id] = {"action": "add_prod_3", "title": state.get("title"), "price": text}
        send_msg(chat_id, f"💵 Harga: <b>{text}</b>\n\nSekarang ketik <b>Deskripsi Singkat</b>:")
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
        send_msg(chat_id, f"💼 Judul: <b>{text}</b>\n\nKetik <b>Tech Stack</b> (contoh: <code>Next.js • Node.js • Python</code>):")
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
        send_msg(chat_id, f"🖼️ Judul: <b>{text}</b>\n\nKetik <b>Tag / Kategori</b> (contoh: <code>DOKUMENTASI KARYA</code>):")
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
        send_msg(chat_id, f"🎬 Judul: <b>{text}</b>\n\nKirimkan <b>Link URL YouTube</b>:")
    elif action == "add_vid_2":
        yt_id = "dQw4w9WgXcQ"
        m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', text)
        if m: yt_id = m.group(1)
        new_vid = {
            "id": int(time.time()),
            "title": state.get("title"),
            "desc": "Video demonstrasi resmi.",
            "embed": f"https://www.youtube-nocookie.com/embed/{yt_id}?controls=1&rel=0",
            "videoUrl": text
        }
        d.setdefault('videos', []).insert(0, new_vid)
        save_data(d)
        user_states[chat_id] = None
        send_finish(chat_id, "Video Baru", state.get("title"), "m_videos")

def handle_callback(call):
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
        edit_msg(chat_id, m_id, "⚡ <b>PORTFOLIO SUPER CMS TELEGRAM</b>\nSilakan pilih kategori yang ingin dikelola:", main_menu())

    elif action == "act_deploy":
        edit_msg(chat_id, m_id, "⏳ <b>Sedang melakukan Deploy ke Vercel & GitHub...</b>")
        succ, log = git_and_deploy()
        kb = {
            "inline_keyboard": [
                [{"text": "🌐 Buka Web Live", "url": "https://portofolio.kheireditz.my.id/"}],
                [{"text": "🏠 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        if succ:
            edit_msg(chat_id, m_id, "✅ <b>BERHASIL DITERAPKAN KE WEB!</b> 🚀\nPerubahan sudah live di:\n👉 https://portofolio.kheireditz.my.id/", kb)
        else:
            edit_msg(chat_id, m_id, f"❌ Deploy Gagal:\n<code>{log[-300:]}</code>")

    elif action == "act_status":
        res = subprocess.run(f"git -C {BASE_DIR} log -1 --pretty=format:'%h - %s (%cr)'", shell=True, capture_output=True, text=True)
        kb = {"inline_keyboard": [[{"text": "🏠 Kembali", "callback_data": "b_main"}]]}
        edit_msg(chat_id, m_id, f"🌐 <b>STATUS WEB SAAT INI</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>URL:</b> https://portofolio.kheireditz.my.id/\n• <b>Commit:</b> <code>{res.stdout}</code>\n• <b>Status:</b> 🟢 Live", kb)

    elif action == "act_backup":
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'rb') as f:
                api_post("sendDocument", {"chat_id": chat_id, "caption": "📦 Backup portfolio-data.js"}, files={"document": f})

    elif action == "m_profile":
        p = d.get('profile', {}) if d else {}
        kb = {
            "inline_keyboard": [
                [{"text": "✏️ Nama", "callback_data": "ed_p_name"}, {"text": "💼 Profesi", "callback_data": "ed_p_profession"}],
                [{"text": "📍 Lokasi", "callback_data": "ed_p_location"}, {"text": "🟢 Status", "callback_data": "ed_p_status"}],
                [{"text": "📝 Edit Deskripsi Bio", "callback_data": "ed_p_bio"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        text = f"👤 <b>INFORMASI PROFIL & BIO</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Nama:</b> {p.get('name')}\n• <b>Profesi:</b> {p.get('profession')}\n• <b>Lokasi:</b> {p.get('location')}\n• <b>Status:</b> {p.get('status')}\n• <b>Bio:</b> {p.get('bio')}\n\nPilih yang ingin diedit:"
        edit_msg(chat_id, m_id, text, kb)

    elif action == "m_contact":
        p = d.get('profile', {}) if d else {}
        soc = p.get('socialLinks', {})
        kb = {
            "inline_keyboard": [
                [{"text": "💬 WhatsApp", "callback_data": "ed_c_wa"}, {"text": "✉️ Email", "callback_data": "ed_c_email"}],
                [{"text": "📸 Instagram", "callback_data": "ed_c_ig"}, {"text": "🎬 TikTok", "callback_data": "ed_c_tiktok"}],
                [{"text": "🐙 GitHub", "callback_data": "ed_c_github"}, {"text": "✈️ Telegram", "callback_data": "ed_c_tg"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        text = f"📞 <b>KONTAK & SOSMED</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>WhatsApp:</b> +{p.get('whatsapp')}\n• <b>Email:</b> {p.get('email')}\n• <b>Instagram:</b> {soc.get('instagram')}\n• <b>TikTok:</b> {soc.get('tiktok')}\n• <b>GitHub:</b> {soc.get('github')}\n• <b>Telegram:</b> {p.get('telegram')}\n\nPilih yang ingin diedit:"
        edit_msg(chat_id, m_id, text, kb)

    elif action == "m_photo":
        kb = {"inline_keyboard": [[{"text": "🔙 Menu Utama", "callback_data": "b_main"}]]}
        user_states[chat_id] = {"action": "upload_photo"}
        edit_msg(chat_id, m_id, "📸 <b>GANTI FOTO PROFIL & FAVICON</b>\n━━━━━━━━━━━━━━━━━━━━━\nKirim foto apa saja ke chat bot ini untuk otomatis mengganti Foto Profil & Ikon Web!", kb)

    elif action == "m_products":
        prods = d.get('products', []) if d else []
        kb_rows = [[{"text": f"📦 {it.get('title')} ({it.get('price')})", "callback_data": f"vp_{i}"}] for i, it in enumerate(prods)]
        kb_rows.append([{"text": "➕ Tambah Produk Baru", "callback_data": "add_prod"}])
        kb_rows.append([{"text": "🔙 Menu Utama", "callback_data": "b_main"}])
        edit_msg(chat_id, m_id, f"🛍️ <b>PRODUK TOKO DIGITAL ({len(prods)} Produk)</b>\nKlik produk untuk melihat/edit/hapus:", {"inline_keyboard": kb_rows})

    elif action.startswith("vp_"):
        idx = int(action.split("_")[1]); prods = d.get('products', [])
        if idx < len(prods):
            p = prods[idx]
            kb = {
                "inline_keyboard": [
                    [{"text": "✏️ Judul", "callback_data": f"ed_pr_title_{idx}"}, {"text": "💵 Harga", "callback_data": f"ed_pr_price_{idx}"}],
                    [{"text": "🏷️ Badge", "callback_data": f"ed_pr_badge_{idx}"}, {"text": "📝 Deskripsi", "callback_data": f"ed_pr_desc_{idx}"}],
                    [{"text": "🗑️ Hapus Produk Ini", "callback_data": f"dp_{idx}"}],
                    [{"text": "🔙 Kembali ke Toko", "callback_data": "m_products"}]
                ]
            }
            text = f"📦 <b>DETAIL PRODUK #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {p.get('title')}\n• <b>Badge:</b> {p.get('badge')}\n• <b>Harga:</b> {p.get('price')}\n• <b>Deskripsi:</b> {p.get('desc')}"
            edit_msg(chat_id, m_id, text, kb)

    elif action.startswith("dp_"):
        idx = int(action.split("_")[1])
        if d and 'products' in d and idx < len(d['products']):
            rem = d['products'].pop(idx); save_data(d)
            kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🛍️ Daftar Produk", "callback_data": "m_products"}]]}
            edit_msg(chat_id, m_id, f"✅ Produk <b>{rem.get('title')}</b> berhasil dihapus!", kb)

    elif action == "add_prod":
        user_states[chat_id] = {"action": "add_prod_1"}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_products"}]]}
        edit_msg(chat_id, m_id, "➕ <b>TAMBAH PRODUK (1/3)</b>\nKetik <b>Judul Produk</b>:", kb)

    elif action == "m_projects":
        projs = d.get('projects', []) if d else []
        kb_rows = [[{"text": f"💼 {it.get('title')}", "callback_data": f"vproj_{i}"}] for i, it in enumerate(projs)]
        kb_rows.append([{"text": "➕ Tambah Proyek Baru", "callback_data": "add_proj"}])
        kb_rows.append([{"text": "🔙 Menu Utama", "callback_data": "b_main"}])
        edit_msg(chat_id, m_id, f"💼 <b>PORTOFOLIO PROYEK ({len(projs)} Proyek)</b>\nKlik proyek untuk mengelola:", {"inline_keyboard": kb_rows})

    elif action.startswith("vproj_"):
        idx = int(action.split("_")[1]); projs = d.get('projects', [])
        if idx < len(projs):
            p = projs[idx]
            kb = {
                "inline_keyboard": [
                    [{"text": "✏️ Judul", "callback_data": f"ed_pj_title_{idx}"}, {"text": "⚙️ Tech", "callback_data": f"ed_pj_tech_{idx}"}],
                    [{"text": "📝 Deskripsi", "callback_data": f"ed_pj_desc_{idx}"}, {"text": "🗑️ Hapus Proyek", "callback_data": f"dproj_{idx}"}],
                    [{"text": "🔙 Kembali ke Proyek", "callback_data": "m_projects"}]
                ]
            }
            text = f"💼 <b>DETAIL PROYEK #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Kategori:</b> {p.get('category')}\n• <b>Judul:</b> {p.get('title')}\n• <b>Tech:</b> {p.get('tech')}\n• <b>Deskripsi:</b> {p.get('desc')}"
            edit_msg(chat_id, m_id, text, kb)

    elif action.startswith("dproj_"):
        idx = int(action.split("_")[1])
        if d and 'projects' in d and idx < len(d['projects']):
            rem = d['projects'].pop(idx); save_data(d)
            kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "💼 Daftar Proyek", "callback_data": "m_projects"}]]}
            edit_msg(chat_id, m_id, f"✅ Proyek <b>{rem.get('title')}</b> berhasil dihapus!", kb)

    elif action == "add_proj":
        user_states[chat_id] = {"action": "add_proj_1"}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_projects"}]]}
        edit_msg(chat_id, m_id, "➕ <b>TAMBAH PROYEK (1/3)</b>\nKetik <b>Judul Proyek</b>:", kb)

    elif action == "m_gallery":
        gals = d.get('gallery', []) if d else []
        kb_rows = [[{"text": f"🖼️ {it.get('title')} [{it.get('tag')}]", "callback_data": f"vg_{i}"}] for i, it in enumerate(gals)]
        kb_rows.append([{"text": "➕ Tambah Foto Galeri", "callback_data": "add_gal"}])
        kb_rows.append([{"text": "🔙 Menu Utama", "callback_data": "b_main"}])
        edit_msg(chat_id, m_id, f"🖼️ <b>GALERI FOTO ({len(gals)} Foto)</b>\nKelola foto dokumentasi:", {"inline_keyboard": kb_rows})

    elif action.startswith("vg_"):
        idx = int(action.split("_")[1]); gals = d.get('gallery', [])
        if idx < len(gals):
            g = gals[idx]
            kb = {
                "inline_keyboard": [
                    [{"text": "✏️ Judul", "callback_data": f"ed_gl_title_{idx}"}, {"text": "🏷️ Tag", "callback_data": f"ed_gl_tag_{idx}"}],
                    [{"text": "🗑️ Hapus Foto", "callback_data": f"dg_{idx}"}],
                    [{"text": "🔙 Kembali ke Galeri", "callback_data": "m_gallery"}]
                ]
            }
            text = f"🖼️ <b>FOTO GALERI #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {g.get('title')}\n• <b>Tag:</b> {g.get('tag')}\n• <b>URL:</b> {g.get('img')}"
            edit_msg(chat_id, m_id, text, kb)

    elif action.startswith("dg_"):
        idx = int(action.split("_")[1])
        if d and 'gallery' in d and idx < len(d['gallery']):
            rem = d['gallery'].pop(idx); save_data(d)
            kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🖼️ Galeri", "callback_data": "m_gallery"}]]}
            edit_msg(chat_id, m_id, f"✅ Foto <b>{rem.get('title')}</b> berhasil dihapus!", kb)

    elif action == "add_gal":
        user_states[chat_id] = {"action": "add_gal_1"}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_gallery"}]]}
        edit_msg(chat_id, m_id, "➕ <b>TAMBAH FOTO GALERI (1/3)</b>\nKetik <b>Judul Foto / Karya</b>:", kb)

    elif action == "m_videos":
        vids = d.get('videos', []) if d else []
        kb_rows = [[{"text": f"🎬 {it.get('title')}", "callback_data": f"vv_{i}"}] for i, it in enumerate(vids)]
        kb_rows.append([{"text": "➕ Tambah Video YouTube", "callback_data": "add_vid"}])
        kb_rows.append([{"text": "🔙 Menu Utama", "callback_data": "b_main"}])
        edit_msg(chat_id, m_id, f"🎥 <b>VIDEO SHOWCASE ({len(vids)} Video)</b>\nKelola video demonstrasi YouTube:", {"inline_keyboard": kb_rows})

    elif action.startswith("vv_"):
        idx = int(action.split("_")[1]); vids = d.get('videos', [])
        if idx < len(vids):
            v = vids[idx]
            kb = {
                "inline_keyboard": [
                    [{"text": "✏️ Judul", "callback_data": f"ed_vd_title_{idx}"}, {"text": "🗑️ Hapus Video", "callback_data": f"dv_{idx}"}],
                    [{"text": "🔙 Kembali ke Video", "callback_data": "m_videos"}]
                ]
            }
            text = f"🎬 <b>VIDEO #{idx+1}</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Judul:</b> {v.get('title')}\n• <b>Link:</b> {v.get('videoUrl')}"
            edit_msg(chat_id, m_id, text, kb)

    elif action.startswith("dv_"):
        idx = int(action.split("_")[1])
        if d and 'videos' in d and idx < len(d['videos']):
            rem = d['videos'].pop(idx); save_data(d)
            kb = {"inline_keyboard": [[{"text": "🚀 Deploy Sekarang", "callback_data": "act_deploy"}], [{"text": "🎥 Daftar Video", "callback_data": "m_videos"}]]}
            edit_msg(chat_id, m_id, f"✅ Video <b>{rem.get('title')}</b> berhasil dihapus!", kb)

    elif action == "add_vid":
        user_states[chat_id] = {"action": "add_vid_1"}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_videos"}]]}
        edit_msg(chat_id, m_id, "🎬 <b>TAMBAH VIDEO (1/2)</b>\nKetik <b>Judul Video</b>:", kb)

    elif action == "m_cards3d":
        c = d.get('cards3D', {}) if d else {}
        kb = {
            "inline_keyboard": [
                [{"text": f"1️⃣ {c.get('skill', {}).get('title', 'Skill')}", "callback_data": "ed_c3_skill"}],
                [{"text": f"2️⃣ {c.get('asset', {}).get('title', 'Asset')}", "callback_data": "ed_c3_asset"}],
                [{"text": f"3️⃣ {c.get('video', {}).get('title', 'Video')}", "callback_data": "ed_c3_video"}],
                [{"text": "🔙 Menu Utama", "callback_data": "b_main"}]
            ]
        }
        edit_msg(chat_id, m_id, "🃏 <b>3 KARTU KANVAS KEDALAMAN 3D</b>\nPilih kartu yang ingin diedit:", kb)

    elif action.startswith("ed_c3_"):
        key = action.replace("ed_c3_", "")
        user_states[chat_id] = {"action": "edit_card3d_title", "card_key": key}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_cards3d"}]]}
        edit_msg(chat_id, m_id, f"🃏 Ketik <b>Judul Baru</b> untuk Kartu [<code>{key}</code>]:", kb)

    elif action.startswith("ed_p_"):
        field = action.replace("ed_p_", "")
        user_states[chat_id] = {"action": "edit_profile_field", "field": field}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_profile"}]]}
        edit_msg(chat_id, m_id, f"✏️ Ketik <b>nilai baru</b> untuk [<code>{field}</code>]:", kb)

    elif action.startswith("ed_c_"):
        field = action.replace("ed_c_", "")
        user_states[chat_id] = {"action": "edit_contact_field", "field": field}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": "m_contact"}]]}
        edit_msg(chat_id, m_id, f"📞 Ketik <b>nilai baru</b> untuk [<code>{field}</code>]:", kb)

    elif action.startswith("ed_pr_"):
        parts = action.split("_"); field = parts[2]; idx = int(parts[3])
        user_states[chat_id] = {"action": "edit_prod_field", "field": field, "idx": idx}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": f"vp_{idx}"}]]}
        edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b> untuk produk #{idx+1}:", kb)

    elif action.startswith("ed_pj_"):
        parts = action.split("_"); field = parts[2]; idx = int(parts[3])
        user_states[chat_id] = {"action": "edit_proj_field", "field": field, "idx": idx}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": f"vproj_{idx}"}]]}
        edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b> untuk proyek #{idx+1}:", kb)

    elif action.startswith("ed_gl_"):
        parts = action.split("_"); field = parts[2]; idx = int(parts[3])
        user_states[chat_id] = {"action": "edit_gal_field", "field": field, "idx": idx}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": f"vg_{idx}"}]]}
        edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b> untuk foto #{idx+1}:", kb)

    elif action.startswith("ed_vd_"):
        parts = action.split("_"); field = parts[2]; idx = int(parts[3])
        user_states[chat_id] = {"action": "edit_vid_field", "field": field, "idx": idx}
        kb = {"inline_keyboard": [[{"text": "❌ Batalkan", "callback_data": f"vv_{idx}"}]]}
        edit_msg(chat_id, m_id, f"✏️ Ketik <b>{field} baru</b> untuk video #{idx+1}:", kb)

def send_finish(chat_id, category, val, back_menu):
    kb = {
        "inline_keyboard": [
            [{"text": "🚀 DEPLOY SEKARANG", "callback_data": "act_deploy"}],
            [{"text": "🔙 Kembali ke Kategori", "callback_data": back_menu}, {"text": "🏠 Menu Utama", "callback_data": "b_main"}]
        ]
    }
    send_msg(chat_id, f"✅ <b>PERUBAHAN DISIMPAN!</b>\n━━━━━━━━━━━━━━━━━━━━━\n• <b>Kategori:</b> {category}\n• <b>Data Baru:</b> <code>{val}</code>\n\nKlik <b>Deploy Sekarang</b> untuk menerapkan ke web!", kb)

def run_loop():
    print("Ultra Fast & Robust Telegram CMS Engine running...")
    offset = 0
    while True:
        try:
            res = api_get("getUpdates", {"offset": offset, "timeout": 20})
            if res.get("ok"):
                updates = res.get("result", [])
                for u in updates:
                    offset = u["update_id"] + 1
                    if "message" in u:
                        handle_message(u["message"])
                    elif "callback_query" in u:
                        handle_callback(u["callback_query"])
            time.sleep(0.1)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_loop()
