import os
import random
import string
import time
import threading
import urllib.parse
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
import yt_dlp

TOKEN = "8728145184:AAF79pgjmxgv0_RDnPLJIWV2zNMnosAofSQ"
ADMIN_ID = 8520025523

bot = telebot.TeleBot(TOKEN)

users_db = {}
active_coupons = {}

TITLE_TIERS = {
    "title_1": {"name": "[Ejderha] 🐉", "stars": 50, "desc": "🔥 Ejderha nefesiyle rakiplerini yak!"},
    "title_2": {"name": "[Kral] 👑", "stars": 45, "desc": "⚡ Krallığın tahtına kurul!"},
    "title_3": {"name": "[İmparator] ⚡", "stars": 40, "desc": "⚡ İmparatorluk gücünü sohbete yansıt."},
    "title_4": {"name": "[Mafya Babası] 🗡️", "stars": 35, "desc": "🗡️ Karanlık dünyanın iradesi."},
    "title_5": {"name": "[Karasal] 🌊", "stars": 30, "desc": "🌊 Okyanusların ve toprakların efendisi."},
    "title_6": {"name": "[Karanlık] 🖤", "stars": 25, "desc": "🖤 Gölgelerin gizemli gücü."},
    "title_7": {"name": "[Efsane] 🏆", "stars": 20, "desc": "🏆 Efsaneler asla ölmez."},
    "title_8": {"name": "[Şampiyon] 🥇", "stars": 15, "desc": "🥇 Kupaların ve zaferlerin tek sahibi."},
    "title_9": {"name": "[Siber] 💻", "stars": 10, "desc": "💻 Kodların ve sistemin hakimi."},
    "title_10": {"name": "[Kralıyet] 🌟", "stars": 5, "desc": "🌟 Sarayın en soylu unvanı."}
}

RANK_BOOST = {
    "name": "👑 Sıralama Zirve Garantisi (30 Günlük 1. Lik)",
    "stars": 100,
    "stock": 83,
    "desc": "🌟 Bu gücü satın alanlar sonuncu olsa bile 30 gün boyunca sıralamada 1. sırada görünür!"
}

COSTS = {
    "tiktok_vid": 40,
    "yt_long": 80,
    "yt_shorts": 50,
    "ig_reels": 50,
    "fb_vid": 50,
    "tw_vid": 50
}

PEXSULY_STAR_PACKAGES = {
    "pack_1": {"name": "500 PEXSULY", "pexsuly": 500, "stars": 20},
    "pack_2": {"name": "1200 PEXSULY", "pexsuly": 1200, "stars": 45},
    "pack_3": {"name": "3000 PEXSULY", "pexsuly": 3000, "stars": 90},
    "pack_4": {"name": "7500 PEXSULY", "pexsuly": 7500, "stars": 200},
    "pack_5": {"name": "20000 PEXSULY", "pexsuly": 20000, "stars": 450},
    "pack_6": {"name": "50000 PEXSULY (Zirve)", "pexsuly": 50000, "stars": 900},
}

VIP_TIERS = {
    30: {"name": "30 Günlük VIP", "days": 30, "stars": 80, "desc": "✨ PEXSULY harcama maliyetleri %20 indirimli olur."},
    60: {"name": "60 Günlük VIP", "days": 60, "stars": 150, "desc": "✨ Günlük ödüllerden gelen PEXSULY'ler 2 katına çıkar."},
    90: {"name": "90 Günlük VIP", "days": 90, "stars": 220, "desc": "✨ Davet ettiğin arkadaş bonusları 3 kat yatar."},
    120: {"name": "120 Günlük VIP", "days": 120, "stars": 300, "desc": "✨ İndirdiğin medyalar kuyrukta en üste taşınır."},
    150: {"name": "150 Günlük VIP", "days": 150, "stars": 380, "desc": "✨ PEXSULY harcama maliyetleri %40 indirimli olur."},
    180: {"name": "180 Günlük VIP (6 Ay)", "days": 180, "stars": 450, "desc": "✨ Günlük ödül süresi 12 saate düşer, günde 2 kez alırsın."},
    210: {"name": "210 Günlük VIP", "days": 210, "stars": 520, "desc": "✨ Admin kupon dağıttığında gizli bildirim ilk sana gelir."},
    270: {"name": "270 Günlük VIP", "days": 270, "stars": 600, "desc": "✨ Toplu PEXSULY dağıtımlarından ekstra %50 bonus alırsın."},
    365: {"name": "365 Günlük VIP (1 Yıl)", "days": 365, "stars": 800, "desc": "✨ Özel [VIP Üye] rozeti ve yarı yarıya indirimli indirmeler."},
    500: {"name": "500 Günlük VIP", "days": 500, "stars": 1100, "desc": "✨ Sınırsıza yakın VIP ayrıcalıkları."},
    1000: {"name": "1000 Günlük VIP (Efsane)", "days": 1000, "stars": 1800, "desc": "✨ Efsanevi indirimler ve öncelikli kuyruk sistemi."},
    2000: {"name": "2000 Günlük VIP (Kral Ultimate)", "days": 2000, "stars": 3000, "desc": "✨ Tüm platformlarda indirmeler tamamen SINIRSIZ ve BEDAVA!"}
}

MOTIVATION_QUOTES = [
    "🌟 'Rüzgar ne kadar sert eserse essin, sağlam kayayı yerinden oynatamaz. Günün aydın olsun!'",
    "🔥 'Zirvede duranlar oraya gökten düşmedi; tırnaklarıyla kazıyarak tırmandı. Zafer seninle olsun kral!'",
    "🦁 'Aslan kendi krallığında gölgede durmaz. Bugün kendi hikayenin kralı ol!'",
    "💎 'Sabır, kararlılık ve çaba; başarının en güçlü anahtarıdır. Güne enerjik başla!'",
    "🚀 'Büyük hayaller, küçük ama kararlı adımlarla başlar. Bugün o adımı at!'",
    "🏆 'Kaybetmekten korkmayanlar, kazanmanın tadını en çok çıkaranlardır.'",
    "⚡ 'Her yeni gün, baştan yazabileceğin tertemiz bir sayfadır.'"
]

TASK_POOL = [
    {"desc": "📥 2 Tane Video İndir", "target": 2, "type": "downloads"},
    {"desc": "🎡 Şans Çarkını 1 Kez Çevir", "target": 1, "type": "spins"},
    {"desc": "👥 1 Arkadaşını Bota Davet Et", "target": 1, "type": "refs"},
    {"desc": "🎙️ 1 Kez Seslendirici Kullan", "target": 1, "type": "voice"}
]

def get_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "pexsuly": 200,
            "refs": 0,
            "weekly_refs": 0,
            "downloads": 0,
            "last_daily": 0,
            "vip_days": 0,
            "streak": 0,
            "lang": "tr",
            "claimed_vip_ref": 0,
            "username": f"user_{user_id}",
            "special_vip": 0,
            "coupon_active": False,
            "wheel_spins": 3,
            "last_wheel_reset": time.time(),
            "last_quote_day": "",
            "daily_tasks": [],
            "last_task_day": "",
            "task_claimed": False,
            "active_title": "Yok",
            "rank_boost_until": 0
        }
    
    user = users_db[user_id]
    if user_id == ADMIN_ID:
        user["wheel_spins"] = 9393938372828282828282829293
    else:
        if time.time() - user.get("last_wheel_reset", 0) > 86400:
            user["wheel_spins"] = 3
            user["last_wheel_reset"] = time.time()
        
    return user

TEXTS = {
    "tr": {
        "welcome": "🔥 **PEXSULY MEDYA VE EKONOMİ BOTUNA HOŞ GELDİN!**",
        "tiktok_vid": "🎵 TikTok Video İndir (40 Pex)",
        "yt_long": "🎬 YouTube Uzun Video (80 Pex)",
        "yt_shorts": "📱 YouTube Shorts İndir (50 Pex)",
        "ig_reels": "📸 Instagram Reels İndir (50 Pex)",
        "fb_vid": "📘 Facebook Video İndir (50 Pex)",
        "tw_vid": "🐦 Twitter (X) Video İndir (50 Pex)",
        "funny_voice": "🎙️ Komik & Racon Seslendirici (90 Pex)",
        "repeat_text": "📝 Satır Tekrarlayıcı (Satır=5 Pex)",
        "styled_text": "🎲 Şekilli Satır Üretici (Satır=15 Pex)",
        "wheel": "🎡 Şans Çarkı (Çevir & VIP / Pex Kazan)",
        "mystery_box": "🎴 Şanslı Kutu / Kasa Aç (250 Pex)",
        "titles": "👑 Özel Unvan / Başlık Marketi",
        "rank_boost": "🚀 Sıralama 1.lik Gücü (Stok: 83)",
        "weekly_users": "🏆 Haftalık Kullanıcı",
        "invite_vip": "🚀 DAVET ET VIP KAZAN",
        "daily": "🎁 Günlük Ödül & Seri Al",
        "tasks": "🎯 Günlük Görevler",
        "coupon": "🎟️ Kupon Kullan",
        "profile": "👤 Profilim & İstatistikler",
        "stars": "⭐ Yıldız ile PEXSULY Al",
        "vip": "👑 VIP Üyelikleri İncele & Al",
        "leaderboard": "🏆 Sıralama & Ödüller",
        "lang": "🌍 Dil Seçimi (Language)"
    }
}

def main_menu(user_id):
    user = get_user(user_id)
    t = TEXTS.get(user["lang"], TEXTS["tr"])
    vip_text = f"👑 VIP: {user['vip_days']} Gün" if user['vip_days'] > 0 else t["vip"]
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(t["tiktok_vid"], callback_data="dl_tiktok_vid"),
        InlineKeyboardButton(t["yt_long"], callback_data="dl_yt_long"),
        InlineKeyboardButton(t["yt_shorts"], callback_data="dl_yt_shorts"),
        InlineKeyboardButton(t["ig_reels"], callback_data="dl_ig_reels"),
        InlineKeyboardButton(t["fb_vid"], callback_data="dl_fb_vid"),
        InlineKeyboardButton(t["tw_vid"], callback_data="dl_tw_vid"),
        InlineKeyboardButton(t["funny_voice"], callback_data="tool_funny_voice"),
        InlineKeyboardButton(t["repeat_text"], callback_data="tool_repeat_text"),
        InlineKeyboardButton(t["styled_text"], callback_data="tool_styled_text"),
        InlineKeyboardButton(t["wheel"], callback_data="wheel_menu"),
        InlineKeyboardButton(t["mystery_box"], callback_data="mystery_box_menu"),
        InlineKeyboardButton(t["titles"], callback_data="titles_menu"),
        InlineKeyboardButton(t["rank_boost"], callback_data="rank_boost_menu"),
        InlineKeyboardButton(t["tasks"], callback_data="daily_tasks_menu"),
        InlineKeyboardButton(t["weekly_users"], callback_data="weekly_users_menu")
    )
    
    if user["vip_days"] > 0 or user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("📦 Çoklu Medya İndir (VIP)", callback_data="vip_multidl_menu"))

    markup.add(
        InlineKeyboardButton(t["invite_vip"], callback_data="invite_vip_menu"),
        InlineKeyboardButton(t["daily"], callback_data="daily_reward"),
        InlineKeyboardButton(t["coupon"], callback_data="use_coupon"),
        InlineKeyboardButton(t["profile"], callback_data="profile"),
        InlineKeyboardButton(t["stars"], callback_data="buy_pexsuly_stars"),
        InlineKeyboardButton(vip_text, callback_data="vip_menu"),
        InlineKeyboardButton(t["leaderboard"], callback_data="leaderboard_menu"),
        InlineKeyboardButton(t["lang"], callback_data="lang_menu")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if message.from_user.username:
        user["username"] = message.from_user.username
        
    t = TEXTS[user["lang"]]
    
    args = message.text.split()
    if len(args) > 1:
        try:
            ref_id = int(args[1])
            if ref_id != user_id and ref_id in users_db:
                ref_user = get_user(ref_id)
                bonus = 150 if ref_user["vip_days"] >= 90 else 50
                ref_user["refs"] += 1
                ref_user["weekly_refs"] = ref_user.get("weekly_refs", 0) + 1
                ref_user["pexsuly"] += bonus
                
                if ref_user["refs"] >= 7 and ref_user["special_vip"] == 0:
                    ref_user["special_vip"] = 1
                    ref_user["vip_days"] += 360
                    bot.send_message(ref_id, "🎉 Tebrikler Kral! 7 davet sınırına ulaştın ve sistem sana otomatik olarak 360 Günlük VIP bastı!")
                
                bot.send_message(ref_id, f"🎉 Tebrikler! Davet ettiğin biri katıldı, hesabına {bonus} PEXSULY eklendi! (Toplam Davet: {ref_user['refs']})")
        except ValueError:
            pass

    today_str = time.strftime("%Y-%m-%d")
    quote_text = ""
    if user.get("last_quote_day") != today_str:
        user["last_quote_day"] = today_str
        quote_text = f"\n\n🔮 **Günün Motivasyon / Havalı Sözü:**\n_{random.choice(MOTIVATION_QUOTES)}_\n"

    spins_disp = "Sınırsız (Kral)" if user_id == ADMIN_ID else f"{user['wheel_spins']}/3"
    boost_status = "Aktif (1. Sırada)" if time.time() < user['rank_boost_until'] else "Yok"
    text = (
        f"{t['welcome']}{quote_text}\n"
        f"🆔 ID: `{user_id}`\n"
        f"👑 Aktif Unvan: `{user['active_title']}`\n"
        f"⚡ Sıralama Zirve Gücü: `{boost_status}`\n"
        f"💎 Pexsuly: `{user['pexsuly']} PEXSULY`\n"
        f"🔥 Seri: `{user['streak']}/4 Gün`\n"
        f"👑 VIP: `{user['vip_days']} Gün`\n"
        f"🎡 Günlük Çark Hakkı: `{spins_disp}`\n\n"
        "⚡ **Krallığı Yönet ve Gücünü Göster Kral:**"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(user_id), parse_mode="Markdown")

# --- 🎴 ŞANSLI KUTU / KASA AÇILIMI SİSTEMİ (/kasa) ---
@bot.message_handler(commands=['kasa'])
@bot.callback_query_handler(func=lambda call: call.data == 'mystery_box_menu')
def mystery_box_handler(event):
    is_call = isinstance(event, telebot.types.CallbackQuery)
    user_id = event.from_user.id if is_call else event.from_user.id
    chat_id = event.message.chat.id if is_call else event.chat.id
    
    if is_call:
        bot.answer_callback_query(event.id)
        
    user = get_user(user_id)
    cost_text = "ÜCRETSİZ (Admin)" if user_id == ADMIN_ID else "250 PEXSULY"
    
    text = (
        "🎴 **ŞANSLİ KUTU / KASA AÇILIMI**\n\n"
        "Kasayı açarak şansına göre büyük ödüller kazanabilirsin! İçinden şunlar çıkabilir:\n"
        "• 🌟 Standart / Nadir Pexsuly\n"
        "• 👑 VIP Günleri (3 - 50 Gün)\n"
        "• 🎡 Ekstra Şans Çarkı Hakları\n"
        "• 🐉 Efsanevi Özel Profil Unvanları!\n\n"
        f"💰 **Kasa Açma Bedeli:** `{cost_text}`\n"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("🎁 Kasayı Aç!", callback_data="open_mystery_box"))
    markup.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))

    if is_call:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=event.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'open_mystery_box')
def open_mystery_box_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    cost = 0 if user_id == ADMIN_ID else 250
    if user["pexsuly"] < cost:
        bot.answer_callback_query(call.id, "❌ Yetersiz Pexsuly! Kasa açmak için 250 PEX lazım.", show_alert=True)
        return
        
    user["pexsuly"] -= cost
    
    # Kasa ödül mekanizması (Rastgele nadirlik ve ödül)
    roll = random.random()
    if roll < 0.40: # Standart Pexsuly (%40)
        rew_pex = random.randint(100, 600)
        user["pexsuly"] += rew_pex
        result_msg = f"🌟 **STANDART KASA ÇIKIŞI!**\n\nKutudan **{rew_pex} PEXSULY** çıktı!"
    elif roll < 0.70: # Nadir Çark Hakkı / Küçük VIP (%30)
        if random.random() < 0.5:
            user["wheel_spins"] += 3
            result_msg = "🎡 **NADİR KASA ÇIKIŞI!**\n\nKutudan **+3 Ekstra Çark Hakkı** çıktı!"
        else:
            vip_w = random.randint(3, 12)
            user["vip_days"] += vip_w
            result_msg = f"👑 **NADİR KASA ÇIKIŞI!**\n\nKutudan **{vip_w} Günlük VIP** çıktı!"
    elif roll < 0.92: # Efsanevi Büyük Ödül (%22)
        vip_e = random.randint(15, 60)
        user["vip_days"] += vip_e
        result_msg = f"🔥 **EFSANEVİ KASA ÇIKIŞI!**\n\nKutudan **{vip_e} Günlük Efsanevi VIP** çıktı!"
    else: # Mistik / Jackpot (%8) - Unvan veya Devasa Pex
        if random.random() < 0.6:
            title_key = random.choice(list(TITLE_TIERS.keys()))
            t_name = TITLE_TIERS[title_key]["name"]
            user["active_title"] = t_name
            result_msg = f"🐉 **MİSTİK JACKPOT KASA ÇIKIŞI!**\n\nTebrikler Kral! Kutudan nadide **{t_name}** unvanı düştü!"
        else:
            huge_pex = random.randint(5000, 15000)
            user["pexsuly"] += huge_pex
            result_msg = f"💎 **MİSTİK JACKPOT KASA ÇIKIŞI!**\n\nİnanılmaz! Kutudan **{huge_pex} PEXSULY** patladı!"

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔄 Tekrar Aç", callback_data="open_mystery_box"),
        InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back")
    )
    bot.answer_callback_query(call.id, "Kasa açıldı!", show_alert=True)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result_msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['gorevler'])
@bot.callback_query_handler(func=lambda call: call.data == 'daily_tasks_menu')
def daily_tasks_handler(event):
    is_call = isinstance(event, telebot.types.CallbackQuery)
    user_id = event.from_user.id if is_call else event.from_user.id
    chat_id = event.message.chat.id if is_call else event.chat.id
    
    if is_call:
        bot.answer_callback_query(event.id)
        
    user = get_user(user_id)
    today_str = time.strftime("%Y-%m-%d")
    
    if user.get("last_task_day") != today_str or not user.get("daily_tasks"):
        user["last_task_day"] = today_str
        user["daily_tasks"] = random.sample(TASK_POOL, 3)
        user["task_claimed"] = False

    text = "🎯 **GÜNLÜK ÖZEL GÖREVLER PANELSİ**\n\n"
    text += "Her gün görevlerini tamamlayarak devasa bonuslar kazanabilirsin kral!\n\n"
    
    for idx, task in enumerate(user["daily_tasks"], 1):
        text += f"{idx}. {task['desc']} (Hedef: {task['target']})\n"

    text += "\n🎁 **Görev Ödülü:** `746 - 7900 PEXSULY` VEYA `2 - 80 Gün Özel VIP`!\n"
    
    markup = InlineKeyboardMarkup(row_width=1)
    if not user.get("task_claimed", False):
        markup.add(InlineKeyboardButton("🎁 Görev Ödülünü Al", callback_data="claim_daily_tasks"))
    else:
        markup.add(InlineKeyboardButton("✅ Bugüne Ait Ödül Alındı", callback_data="already_claimed_tasks"))
        
    markup.add(InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="main_menu_back"))

    if is_call:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=event.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'claim_daily_tasks')
def claim_daily_tasks_callback(call):
    user = get_user(call.from_user.id)
    if user.get("task_claimed", False):
        bot.answer_callback_query(call.id, "❌ Bugünkü görev ödülünü zaten aldın!", show_alert=True)
        return

    user["task_claimed"] = True
    reward_is_vip = random.random() < 0.35
    
    if reward_is_vip:
        vip_reward = random.randint(2, 80)
        user["vip_days"] += vip_reward
        res_text = f"👑 **MÜKEMMEL GÖREV ÖDÜLÜ!**\n\nGörevleri tamamladığın için hesabına **{vip_reward} Günlük Özel VIP** eklendi!"
    else:
        pex_reward = random.randint(746, 7900)
        user["pexsuly"] += pex_reward
        res_text = f"💎 **DEVASA GÖREV ÖDÜLÜ!**\n\nGörevleri tamamladığın için hesabına **{pex_reward} PEXSULY** eklendi!"

    bot.answer_callback_query(call.id, "Ödül Alındı!", show_alert=True)
    bot.send_message(call.message.chat.id, res_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'tool_funny_voice')
def prompt_funny_voice(call):
    bot.answer_callback_query(call.id)
    user = get_user(call.from_user.id)
    
    if user["pexsuly"] < 90:
        bot.send_message(call.message.chat.id, "❌ **Yetersiz Bakiye!** Bu aracı kullanmak için 90 Pexsuly gerekiyor.", parse_mode="Markdown")
        return

    msg = bot.send_message(
        call.message.chat.id,
        "🎙️ **KOMİK & RACON SESLENDİRİCİ**\n"
        "💰 Ücret: `90 Pexsuly`\n\n"
        "Lütfen seslendirmemi istediğin metni yazıp gönder kral:\n"
        "*(İptal etmek için `/iptal` yazabilirsin)*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_funny_voice)

def process_funny_voice(message):
    if not message.text: return
    if message.text.lower() == '/iptal':
        bot.send_message(message.chat.id, "❌ İşlem iptal edildi.")
        return

    user = get_user(message.from_user.id)
    if user["pexsuly"] < 90:
        bot.send_message(message.chat.id, "❌ Yetersiz Pexsuly!")
        return

    user["pexsuly"] -= 90
    encoded_text = urllib.parse.quote(message.text)
    voice_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=tr&client=tw-ob"

    try:
        bot.send_voice(message.chat.id, voice_url, caption="🎙️ **Sesli Mesaj Oluşturuldu!**\n💎 `-90 PEX` düşüldü.", parse_mode="Markdown")
    except Exception as e:
        user["pexsuly"] += 90
        bot.send_message(message.chat.id, f"❌ Ses oluşturulurken hata çıktı: {str(e)[:50]}")

@bot.callback_query_handler(func=lambda call: call.data == 'buy_pexsuly_stars')
def pexsuly_stars_menu(call):
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup(row_width=1)
    
    if user_id == ADMIN_ID:
        admin_packs = [
            ("💎 999393939393 PEXSULY (ÜCRETSİZ)", 999393939393),
            ("💎 938382828282828282 PEXSULY (ÜCRETSİZ)", 938382828282828282),
            ("💎 938393939493393838393939 PEXSULY (ÜCRETSİZ)", 938393939493393838393939),
            ("💎 934949494949494949494 PEXSULY (ÜCRETSİZ)", 934949494949494949494),
            ("💎 84844949494949494949494949 PEXSULY (ÜCRETSİZ)", 84844949494949494949494949)
        ]
        for idx, (name, amt) in enumerate(admin_packs, 1):
            markup.add(InlineKeyboardButton(name, callback_data=f"adminpex_{amt}"))
    else:
        for k, p in PEXSULY_STAR_PACKAGES.items():
            markup.add(InlineKeyboardButton(f"⭐ {p['name']} ({p['stars']} Yıldız)", callback_data=f"starpex_{k}"))
            
    markup.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="⭐ **Pexsuly Bakiye Yükleme Paneli:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('adminpex_'))
def admin_claim_pexsuly(call):
    if call.from_user.id != ADMIN_ID: return
    amount = int(call.data.split('_')[1])
    user = get_user(ADMIN_ID)
    user["pexsuly"] += amount
    bot.answer_callback_query(call.id, f"Hesabına {amount} PEXSULY Tanımlandı!", show_alert=True)
    bot.send_message(call.message.chat.id, f"👑 **ADMİN BAKIYE YÜKLEMESİ BAŞARILI!**\n\nHesabına tam `{amount} PEXSULY` basıldı kral!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'vip_menu')
def vip_menu_handler(call):
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup(row_width=1)
    
    if user_id == ADMIN_ID:
        markup.add(InlineKeyboardButton("👑 9.500.000 GÜNLÜK ÜST DÜZEY VIP (ÜCRETSİZ)", callback_data="admin_claim_vip"))
    else:
        for days, info in VIP_TIERS.items():
            markup.add(InlineKeyboardButton(f"👑 {days} Günlük VIP ({info['stars']} Yıldız)", callback_data=f"vippreview_{days}"))
            
    markup.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👑 **VIP KADEMELERİ PANELSİ**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'admin_claim_vip')
def admin_claim_vip_callback(call):
    if call.from_user.id != ADMIN_ID: return
    user = get_user(ADMIN_ID)
    user["vip_days"] += 9500000
    bot.answer_callback_query(call.id, "9.500.000 Günlük VIP Tanımlandı!", show_alert=True)
    bot.send_message(call.message.chat.id, f"👑 **EFSANEVİ ADMİN VIP TANIMLANDI!**\n\nHesabına tam **9.500.000 Günlük Üst Düzey Sınırsız VIP** tanımlandı kral! Tüm indirmeler bedava ve sınırsız!", parse_mode="Markdown")

@bot.message_handler(commands=['unvanlar'])
@bot.callback_query_handler(func=lambda call: call.data == 'titles_menu')
def titles_menu_handler(event):
    is_call = isinstance(event, telebot.types.CallbackQuery)
    user_id = event.from_user.id if is_call else event.from_user.id
    chat_id = event.message.chat.id if is_call else event.chat.id
    
    if is_call:
        bot.answer_callback_query(event.id)
        
    user = get_user(user_id)
    text = "👑 **ÖZEL PROFİL BAŞLIĞI / UNVAN MARKETİ**\n\nEjderha'dan başlayan 10 efsanevi unvan!\n\n"
    if user_id == ADMIN_ID:
        text += "⚡ **Admin Ayrıcalığı:** Senin için tüm unvanlar tamamen **ÜCRETSİZ**dir!\n\n"

    markup = InlineKeyboardMarkup(row_width=1)
    for key, info in TITLE_TIERS.items():
        price_text = "ÜCRETSİZ (Admin)" if user_id == ADMIN_ID else f"{info['stars']} Yıldız"
        markup.add(InlineKeyboardButton(f"{info['name']} — {price_text}", callback_data=f"buytitle_{key}"))
        
    markup.add(InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="main_menu_back"))

    if is_call:
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=event.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buytitle_'))
def buy_title_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    title_key = call.data.split('_', 1)[1]
    info = TITLE_TIERS.get(title_key)
    
    if not info:
        bot.answer_callback_query(call.id, "❌ Unvan bulunamadı!", show_alert=True)
        return

    if user_id == ADMIN_ID:
        user["active_title"] = info["name"]
        bot.answer_callback_query(call.id, f"{info['name']} unvanı tanımlandı!", show_alert=True)
        bot.send_message(call.message.chat.id, f"👑 **Tebrikler Kral!** Hesabına **{info['name']}** unvanı eklendi.", parse_mode="Markdown")
    else:
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Unvan: {info['name']}",
            description=info['desc'],
            invoice_payload=f"star_title_{title_key}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=info['name'], amount=info['stars'])]
        )

@bot.callback_query_handler(func=lambda call: call.data == 'rank_boost_menu')
def rank_boost_menu_handler(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    bot.answer_callback_query(call.id)
    
    price_text = "ÜCRETSİZ (Admin)" if user_id == ADMIN_ID else f"{RANK_BOOST['stars']} Yıldız"
    text = (
        f"🚀 **{RANK_BOOST['name']}**\n\n"
        f"{RANK_BOOST['desc']}\n\n"
        f"📦 **Kalan Stok:** `{RANK_BOOST['stock']}`\n"
        f"💰 **Fiyat:** `{price_text}`\n"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"⭐ Satın Al ({price_text})", callback_data="buy_rank_boost"))
    markup.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'buy_rank_boost')
def buy_rank_boost_callback(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if RANK_BOOST['stock'] <= 0 and user_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Üzgünüm, stok tükendi!", show_alert=True)
        return

    if user_id == ADMIN_ID:
        user["rank_boost_until"] = time.time() + (30 * 86400)
        bot.answer_callback_query(call.id, "30 Günlük Sıralama Birinciliği Tanımlandı!", show_alert=True)
        bot.send_message(call.message.chat.id, "👑 **Efsane!** 30 gün boyunca sonuncu olsan bile sıralamada 1. sırada görünüyorsun kral!", parse_mode="Markdown")
    else:
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=RANK_BOOST['name'],
            description=RANK_BOOST['desc'],
            invoice_payload="star_rank_boost",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Zirve Gücü", amount=RANK_BOOST['stars'])]
        )

@bot.message_handler(commands=['herkes'])
def admin_broadcast_gift(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        bot.send_message(message.chat.id, "⚠️ Hatalı kullanım! Örn: `/herkes pex 5000` veya `/herkes vip 30`", parse_mode="Markdown")
        return
    
    gift_type = args[1].lower()
    try:
        amount = int(args[2])
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Miktar sayı olmalıdır!")
        return

    count = 0
    for uid in users_db:
        if gift_type == "pex":
            users_db[uid]["pexsuly"] += amount
            count += 1
        elif gift_type == "vip":
            users_db[uid]["vip_days"] += amount
            count += 1

    if gift_type == "pex":
        bot.send_message(message.chat.id, f"👑 Başarıyla **{count}** kullanıcıya **{amount} PEXSULY** dağıtıldı kral!", parse_mode="Markdown")
    elif gift_type == "vip":
        bot.send_message(message.chat.id, f"👑 Başarıyla **{count}** kullanıcıya **{amount} Günlük VIP** dağıtıldı kral!", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⚠️ Geçersiz tür! `pex` veya `vip` yazmalısın.")

@bot.callback_query_handler(func=lambda call: call.data == 'leaderboard_menu')
def leaderboard_menu_callback(call):
    bot.answer_callback_query(call.id)
    current_time = time.time()
    sorted_users = sorted(users_db.values(), key=lambda x: (1 if x.get("rank_boost_until", 0) > current_time else 0, x["refs"], x["pexsuly"]), reverse=True)[:10]
    
    text = "🏆 **LİDERLİK TABLOSU (ZİRVE SAHİPLERİ EN ÜSTTE)**\n\n"
    for i, u in enumerate(sorted_users, 1):
        title_str = f" {u.get('active_title', '')}" if u.get("active_title", "Yok") != "Yok" else ""
        boost_icon = " ⚡[1.LİK]" if u.get("rank_boost_until", 0) > current_time else ""
        text += f"{i}. @{u.get('username','User')}{title_str}{boost_icon} — 👥 {u.get('refs',0)} Davet | 💎 {u.get('pexsuly',0)} Pex\n"
        
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'weekly_users_menu')
def weekly_users_menu_handler(call):
    bot.answer_callback_query(call.id)
    current_time = time.time()
    sorted_users = sorted(users_db.values(), key=lambda x: (1 if x.get("rank_boost_until", 0) > current_time else 0, x.get("weekly_refs", 0), x.get("pexsuly", 0)), reverse=True)
    top_users = sorted_users[:10]
    text = "🏆 **HAFTALİK KULLANICI LİDERLİK TABLOSU** 🏆\n\nBu haftanın en aktif kullanıcıları ve dev hediyeleri:\n\n"
    badges = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for index, u in enumerate(top_users):
        badge = badges[index] if index < len(badges) else "▫️"
        title_str = f" {u.get('active_title', '')}" if u.get("active_title", "Yok") != "Yok" else ""
        boost_icon = " ⚡[1.LİK]" if u.get("rank_boost_until", 0) > current_time else ""
        text += f"{badge} **@{u.get('username', 'Kullanıcı')}**{title_str}{boost_icon} — 👥 `{u.get('weekly_refs', 0)}` Haftalık Davet | 💎 `{u.get('pexsuly', 0)}` Pex\n"
    text += "\n🎁 **Haftalık Sıralama Ödülleri:**\n🥇 **1. Olana:** 30 - 365 Gün Yıldız Özellikli VIP\n🥈 **2. Olana:** 30 Gün Yıldız Özellikli VIP\n🥉 **3. Olana:** 10 - 20 Günlük Normal veya Maxx VIP\n🎖️ **10 - 100. Arasındakilere:** 500 - 10.000 PEXSULY\n🎖️ **100 - 1000. Arasındakilere:** 200 - 1.735 PEXSULY\n"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data="main_menu_back"))
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

def weekly_reward_auto_distributor():
    while True:
        time.sleep(604800)
        if users_db:
            current_time = time.time()
            sorted_users = sorted(users_db.items(), key=lambda x: (1 if x[1].get("rank_boost_until", 0) > current_time else 0, x[1].get("weekly_refs", 0), x[1].get("pexsuly", 0)), reverse=True)
            for index, (uid, user) in enumerate(sorted_users, start=1):
                try:
                    if index == 1:
                        rw = random.choice([30, 365])
                        user["vip_days"] += rw
                        bot.send_message(uid, f"🎉 **1. OLDUN!** {rw} Günlük Yıldız VIP kazandın!", parse_mode="Markdown")
                    elif index == 2:
                        user["vip_days"] += 30
                        bot.send_message(uid, "🎉 **2. OLDUN!** 30 Günlük Yıldız VIP kazandın!", parse_mode="Markdown")
                    elif index == 3:
                        rw = random.randint(10, 20)
                        user["vip_days"] += rw
                        bot.send_message(uid, f"🎉 **3. OLDUN!** {rw} Günlük VIP kazandın!", parse_mode="Markdown")
                    elif 10 <= index <= 100:
                        pb = random.randint(500, 10000)
                        user["pexsuly"] += pb
                        bot.send_message(uid, f"🎁 **HAFTALIK ÖDÜL!** {pb} PEXSULY kazandın!", parse_mode="Markdown")
                    elif 100 < index <= 1000:
                        pb = random.randint(200, 1735)
                        user["pexsuly"] += pb
                        bot.send_message(uid, f"🎁 **HAFTALIK ÖDÜL!** {pb} PEXSULY kazandın!", parse_mode="Markdown")
                except Exception:
                    pass
                user["weekly_refs"] = 0

threading.Thread(target=weekly_reward_auto_distributor, daemon=True).start()

def auto_random_vip_scheduler():
    while True:
        time.sleep(random.randint(3600, 14400))
        if users_db:
            uid = random.choice(list(users_db.keys()))
            days = random.randint(7, 18)
            user = get_user(uid)
            user["vip_days"] += days
            try:
                bot.send_message(uid, f"🎁 **SÜRPRİZ VIP!** Bot sana {days} Günlük Özel VIP hediye etti!", parse_mode="Markdown")
            except Exception:
                pass

threading.Thread(target=auto_random_vip_scheduler, daemon=True).start()

@bot.callback_query_handler(func=lambda call: call.data in ['tool_repeat_text', 'tool_styled_text'])
def prompt_line_tool(call):
    mode = call.data
    bot.answer_callback_query(call.id)
    cpl = 5 if mode == 'tool_repeat_text' else 15
    msg = bot.send_message(call.message.chat.id, f"🛠️ Satır Araç\n💰 Ücret: Satır Başı {cpl} Pexsuly\n\nMetin ve satır sayısını yaz (Örn: `Ahmet 10`):\nİptal için `/iptal`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_line_tool, mode, cpl)

def process_line_tool(message, mode, cpl):
    if not message.text: return
    if message.text.lower() == '/iptal':
        bot.send_message(message.chat.id, "❌ İptal edildi.")
        return
    parts = message.text.strip().rsplit(' ', 1)
    if len(parts) < 2 or not parts[1].isdigit():
        bot.send_message(message.chat.id, "⚠️ Hatalı biçim! Örn: `Ahmet 10`", parse_mode="Markdown")
        return
    text_to_repeat, line_count = parts[0], int(parts[1])
    if line_count <= 0 or line_count > 182050:
        bot.send_message(message.chat.id, "❌ Maksimum 182.050 satır girebilirsin.")
        return
    total_cost = line_count * cpl
    user = get_user(message.from_user.id)
    if user["pexsuly"] < total_cost:
        bot.send_message(message.chat.id, f"❌ Yetersiz bakiye! Gereken: {total_cost}")
        return
    user["pexsuly"] -= total_cost
    styles = ["{i}: {text}", "{i}) {text}", "⭐ {text} #{i}", "🔥 [{i}] {text}", "🔹 {i}. {text}"]
    lines_output = [text_to_repeat if mode == 'tool_repeat_text' else random.choice(styles).format(i=i, text=text_to_repeat) for i in range(1, line_count + 1)]
    full_text = "\n".join(lines_output)
    if len(full_text) <= 4000:
        bot.send_message(message.chat.id, f"✅ Üretildi! (-{total_cost} PEX)\n\n{full_text}", parse_mode="Markdown")
    else:
        for i in range(0, len(full_text), 3900):
            bot.send_message(message.chat.id, full_text[i:i+3900])
        bot.send_message(message.chat.id, f"✅ Tamamlandı! (-{total_cost} PEX)")

@bot.callback_query_handler(func=lambda call: call.data == 'wheel_menu')
def wheel_menu_handler(call):
    user = get_user(call.from_user.id)
    bot.answer_callback_query(call.id)
    markup = InlineKeyboardMarkup(row_width=1)
    if call.from_user.id == ADMIN_ID or user["wheel_spins"] > 0:
        spins_txt = "Sınırsız (Kral)" if call.from_user.id == ADMIN_ID else str(user['wheel_spins'])
        markup.add(InlineKeyboardButton(f"🎯 Çarkı Çevir (Hak: {spins_txt})", callback_data="spin_wheel_free"))
    else:
        markup.add(InlineKeyboardButton("💎 20 Pexsuly İle Çevir", callback_data="spin_wheel_pex"), InlineKeyboardButton("⭐ 4 Yıldız İle Çevir", callback_data="spin_wheel_stars"))
    markup.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    spins_disp = "Sınırsız (Kral)" if call.from_user.id == ADMIN_ID else f"{user['wheel_spins']}/3"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🎡 **PEXSULY ŞANS ÇARKI**\nKalan Hak: `{spins_disp}`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data in ['spin_wheel_free', 'spin_wheel_pex'])
def execute_spin(call):
    user = get_user(call.from_user.id)
    if call.data == 'spin_wheel_free':
        if call.from_user.id != ADMIN_ID:
            if user["wheel_spins"] <= 0:
                bot.answer_callback_query(call.id, "❌ Ücretsiz hakkın kalmadı!", show_alert=True)
                return
            user["wheel_spins"] -= 1
else:
        if user["pexsuly"] < 20:
            bot.answer_callback_query(call.id, "❌ 20 Pexsuly lazım!", show_alert=True)
            return
        user["pexsuly"] -= 20
    is_vip = random.random() < 0.35
    if is_vip:
        rw = random.randint(10, 64)
        user["vip_days"] += rw
        res = f"👑 **MÜKEMMEL ÖDÜL!** {rw} Günlük VIP kazandın!"
    else:
        rw = random.randint(60, 900)
        user["pexsuly"] += rw
        res = f"💎 **HARİKA ÖDÜL!** {rw} PEXSULY kazandın!"
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔄 Tekrar Çevir", callback_data="wheel_menu"), InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=res, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'spin_wheel_stars')
def spin_wheel_stars_payment(call):
    bot.send_invoice(chat_id=call.message.chat.id, title="Çark Çevirme Hakkı", description="1 kez şans çarkı çevir.", invoice_payload="wheel_spin_star", provider_token="", currency="XTR", prices=[LabeledPrice(label="Çark Hakkı", amount=4)])

@bot.callback_query_handler(func=lambda call: call.data == 'use_coupon')
def use_coupon_callback(call):
    user = get_user(call.from_user.id)
    user["coupon_active"] = True
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🎟️ Kupon kodunu gönder (/iptal ile vazgeç):", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'vip_multidl_menu')
def vip_multidl_handler(call):
    if get_user(call.from_user.id)["vip_days"] <= 0 and call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Yalnızca VIP kullanıcılara özel!", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📦 Çoklu indirme modundasın. Linkleri alt alta gönderebilirsin.")

@bot.callback_query_handler(func=lambda call: call.data == 'invite_vip_menu')
def invite_vip_menu_handler(call):
    user = get_user(call.from_user.id)
    ref_link = f"https://t.me/{bot.get_me().username}?start={call.from_user.id}"
    markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🎁 Ödülü Al", callback_data="claim_invite_vip"), InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🚀 **DAVET ET VIP KAZAN**\n\n7 davete ulaşınca otomatik **360 Gün VIP** kazanırsın!\nMevcut: `{user['refs']}/7`\n\nLinkin:\n`{ref_link}`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'claim_invite_vip')
def claim_invite_vip_handler(call):
    user = get_user(call.from_user.id)
    if user["refs"] < 7 or user["special_vip"] == 1:
        bot.answer_callback_query(call.id, "❌ Şartlar sağlanmadı veya ödül zaten alındı!", show_alert=True)
        return
    user["special_vip"] = 1
    user["vip_days"] += 360
    bot.answer_callback_query(call.id, "Tebrikler! 360 Gün VIP Eklendi!", show_alert=True)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🎊 Tebrikler! 360 Gün VIP eklendi!\nToplam VIP: `{user['vip_days']} Gün`", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Ana Menü", callback_data="main_menu_back")), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'lang_menu')
def lang_menu_handler(call):
    markup = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🇹🇷 Türkçe", callback_data="setlang_tr"), InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"), InlineKeyboardButton("🔙 Geri", callback_data="main_menu_back"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🌍 **Dil Seçin:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('setlang_'))
def set_language(call):
    user = get_user(call.from_user.id)
    user["lang"] = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "Dil güncellendi!")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ Güncellendi:", reply_markup=main_menu(call.from_user.id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'daily_reward')
def daily_reward_callback(call):
    user = get_user(call.from_user.id)
    if time.time() - user["last_daily"] < (43200 if user["vip_days"] >= 180 else 86400):
        bot.answer_callback_query(call.id, "⏳ Ödülünü zaten aldın!", show_alert=True)
        return
    user["streak"] += 1
    if user["streak"] >= 4:
        earned, user["streak"] = 390, 0
        txt = "🎉 4 günlük seriyi tamamladın, 390 PEXSULY kazandın!"
    else:
        earned = 25
        txt = f"🎁 Günlük ödül alındı: +{earned} PEX"
    user["pexsuly"] += earned
    user["last_daily"] = time.time()
    bot.answer_callback_query(call.id, f"+{earned} PEX!", show_alert=True)
    bot.send_message(call.message.chat.id, txt, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'profile')
def profile_callback(call):
    user = get_user(call.from_user.id)
    bot.answer_callback_query(call.id)
    boost_status = "Aktif (1. Sırada)" if time.time() < user['rank_boost_until'] else "Yok"
    bot.send_message(call.message.chat.id, f"👤 **PROFİL**\n🆔 ID: `{call.from_user.id}`\n👑 Aktif Unvan: `{user['active_title']}`\n⚡ Sıralama Zirve Gücü: `{boost_status}`\n💎 Pexsuly: `{user['pexsuly']}`\n📥 İndirilen: `{user['downloads']}`\n🔥 Seri: `{user['streak']}/4`\n👑 VIP: `{user['vip_days']} Gün`", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('starpex_'))
def buy_pexsuly_with_stars(call):
    pack = PEXSULY_STAR_PACKAGES.get(call.data.split('_', 1)[1])
    if pack:
        bot.send_invoice(chat_id=call.message.chat.id, title=pack['name'], description="Pexsuly yüklemesi.", invoice_payload=f"star_pex_{call.data.split('_', 1)[1]}", provider_token="", currency="XTR", prices=[LabeledPrice(label=pack['name'], amount=pack['stars'])])

@bot.callback_query_handler(func=lambda call: call.data.startswith('vippreview_'))
def vip_preview(call):
    info = VIP_TIERS[int(call.data.split('_')[1])]
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(f"⭐ Satın Al ({info['stars']} Yıldız)", callback_data=f"buyvip_{call.data.split('_')[1]}"), InlineKeyboardButton("🔙 Geri", callback_data="vip_menu"))
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"👑 **{info['name']}**\n\n{info['desc']}\n\nFiyat: `{info['stars']} Yıldız`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buyvip_'))
def buy_vip_with_stars(call):
    info = VIP_TIERS.get(int(call.data.split('_')[1]))
    if info:
        bot.send_invoice(chat_id=call.message.chat.id, title=info['name'], description=info['desc'], invoice_payload=f"star_vip_{call.data.split('_')[1]}", provider_token="", currency="XTR", prices=[LabeledPrice(label=info['name'], amount=info['stars'])])

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    payload = message.successful_payment.invoice_payload
    user = get_user(message.from_user.id)
    if payload.startswith("star_pex_"):
        user["pexsuly"] += PEXSULY_STAR_PACKAGES[payload.split('_')[-1]]["pexsuly"]
        bot.send_message(message.chat.id, "🎉 Ödeme başarılı, Pexsuly eklendi!")
    elif payload.startswith("star_vip_"):
        user["vip_days"] = int(payload.split('_')[-1])
        bot.send_message(message.chat.id, "👑 Ödeme başarılı, VIP tanımlandı!")
    elif payload.startswith("star_title_"):
        t_key = payload.split('_')[-1]
        t_info = TITLE_TIERS.get(t_key)
        if t_info:
            user["active_title"] = t_info["name"]
            bot.send_message(message.chat.id, f"👑 Ödeme başarılı! **{t_info['name']}** unvanı tanımlandı!")
    elif payload == "star_rank_boost":
        if RANK_BOOST['stock'] > 0:
            RANK_BOOST['stock'] -= 1
            user["rank_boost_until"] = time.time() + (30 * 86400)
            bot.send_message(message.chat.id, "👑 Ödeme başarılı! 30 gün boyunca sıralamada zirvedesin!")
    elif payload == "wheel_spin_star":
        if random.random() < 0.35:
            rw = random.randint(10, 64)
            user["vip_days"] += rw
            bot.send_message(message.chat.id, f"🎉 Çarktan {rw} Günlük VIP çıktı!", parse_mode="Markdown")
        else:
            rw = random.randint(60, 900)
            user["pexsuly"] += rw
            bot.send_message(message.chat.id, f"🎉 Çarktan {rw} PEXSULY çıktı!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == 'main_menu_back')
def back_menu(call):
    user = get_user(call.from_user.id)
    user["coupon_active"] = False
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔥 **Ana Menüdesin**", reply_markup=main_menu(call.from_user.id), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def prompt_download(call):
    platform = call.data.split('_', 1)[1]
    base_cost = COSTS.get(platform, 40)
    user = get_user(call.from_user.id)
    user["coupon_active"] = False
    cost = 0 if user["vip_days"] >= 2000 else int(base_cost * (0.3 if user["vip_days"] >= 1000 else 0.5 if user["vip_days"] >= 365 else 0.6 if user["vip_days"] >= 150 else 0.8 if user["vip_days"] >= 30 else 1.0))
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"📥 **Video İndirici**\n💎 Gerekli: {cost} PEX\n\nLink gönder (/iptal ile vazgeç):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_media_download, platform, cost)

def process_media_download(message, platform, cost):
    if not message.text: return
    if message.text.lower() == '/iptal':
        bot.send_message(message.chat.id, "❌ İptal edildi.")
        return
    url = message.text.strip()
    user = get_user(message.from_user.id)
    
    if "http" not in url:
        bot.send_message(message.chat.id, "⚠️ Geçersiz link.")
        return

    url_low = url.lower()
    if "tiktok" in platform:
        if "tiktok.com" not in url_low and "vt.tiktok.com" not in url_low and "vm.tiktok.com" not in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece TikTok linkleri içindir!")
            return
    elif "yt_" in platform:
        if "youtube.com" not in url_low and "youtu.be" not in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece YouTube linkleri içindir!")
            return
        if platform == "yt_long" and "shorts" in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Shorts linki buraya atılamaz! Shorts butonunu kullan.")
            return
        if platform == "yt_shorts" and "shorts" not in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece YouTube Shorts içindir!")
            return
    elif platform == "ig_reels":
        if "instagram.com" not in url_low or ("reel" not in url_low and "reels" not in url_low):
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece Instagram Reels linkleri içindir!")
            return
    elif platform == "fb_vid":
        if "facebook.com" not in url_low and "fb.watch" not in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece Facebook video linkleri içindir!")
            return
    elif platform == "tw_vid":
        if "twitter.com" not in url_low and "x.com" not in url_low:
            bot.send_message(message.chat.id, "❌ **HATA:** Bu buton sadece Twitter (X) video linkleri içindir!")
            return

    if user["pexsuly"] < cost:
        bot.send_message(message.chat.id, f"❌ Yetersiz Pexsuly! Gereken: {cost}")
        return
        
    user["pexsuly"] -= cost
    user["downloads"] += 1
    msg = bot.send_message(message.chat.id, "🔄 İndiriliyor...")
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'outtmpl': f"downloads/{message.from_user.id}_%(id)s.%(ext)s",
        'format': 'best',
        'nopart': True,
        'max_filesize': 50 * 1024 * 1024,  'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not os.path.exists(filename):
            files = [f for f in os.listdir("downloads") if f.startswith(str(message.from_user.id))]
            if files: filename = os.path.join("downloads", max(files, key=lambda f: os.path.getctime(os.path.join("downloads", f))))
        with open(filename, 'rb') as f:
            bot.send_video(message.chat.id, f, caption=f"✅ İndirildi! (-{cost} PEX)")
        if os.path.exists(filename): os.remove(filename)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"❌ İndirme hatası: {str(e)[:40]}")
        user["pexsuly"] += cost

@bot.message_handler(commands=['puanver'])
def admin_give_points(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 2: return
    amt = int(args[1])
    for uid in users_db: users_db[uid]["pexsuly"] += amt
    bot.send_message(message.chat.id, f"👑 Herkese {amt} PEXSULY dağıtıldı!")

@bot.message_handler(commands=['hakdagit'])
def admin_create_coupon(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 2: return
    amt = int(args[1])
    code = "PEX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    active_coupons[code] = amt
    bot.send_message(message.chat.id, f"🎁 Kupon: `{code}` ({amt} PEX)", parse_mode="Markdown")

@bot.message_handler(commands=['vipver'])
def admin_give_vip(message):
    if message.from_user.id != ADMIN_ID: return
    args = message.text.split()
    if len(args) < 3: return
    get_user(int(args[1]))["vip_days"] = int(args[2])
    bot.send_message(message.chat.id, "👑 VIP tanımlandı.")

@bot.message_handler(commands=['iptal'])
def cancel_op(message):
    user = get_user(message.from_user.id)
    user["coupon_active"] = False
    bot.send_message(message.chat.id, "İşlem iptal edildi.")

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if not message.text: return
    if message.text.lower() == '/iptal':
        user = get_user(message.from_user.id)
        user["coupon_active"] = False
        bot.send_message(message.chat.id, "❌ İptal edildi.")
        return
    user = get_user(message.from_user.id)
    if user["coupon_active"]:
        user["coupon_active"] = False
        code = message.text.strip()
        if code in active_coupons:
            amount = active_coupons.pop(code)
            user["pexsuly"] += amount
            bot.send_message(message.chat.id, f"🎉 Kupon kullanıldı! +{amount} PEX", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Geçersiz kupon!")
        return

print("PEXSULY Bot Kasa Sistemiyle Birlikte Eksiksiz Çalışıyor!")
bot.infinity_polling()
