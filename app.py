import streamlit as st
import requests
import pandas as pd
import urllib.parse
import math
from datetime import datetime, timezone

# --- APPLE & FINTECH PLATFORM AYARLARI ---
st.set_page_config(
    page_title="KMZ Studio — Albion Arbitraj Terminali",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- APPLE HUMAN INTERFACE DESIGN SYSTEM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Temel Platform Ayarları */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
        background-color: #000000;
        color: #f5f5f7;
        -webkit-font-smoothing: antialiased;
        letter-spacing: -0.01em;
    }

    #MainMenu, footer, .stDeployButton, [data-testid="stDecoration"] {
        display: none !important;
    }

    .stApp {
        background: #000000 !important;
        background-image: radial-gradient(circle at 50% -20%, rgba(58, 58, 60, 0.3) 0%, transparent 60%) !important;
    }

    /* Sol Menü (Sidebar) Blur Efekti */
    [data-testid="stSidebar"] {
        background-color: rgba(28, 28, 30, 0.75) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Üst Navigasyon Barı */
    .apple-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: rgba(28, 28, 30, 0.45);
        backdrop-filter: blur(30px) saturate(180%);
        -webkit-backdrop-filter: blur(30px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 28px;
    }
    .apple-logo-text {
        font-size: 21px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #f5f5f7;
    }
    .apple-sub {
        font-size: 13px;
        color: #86868b;
        margin-left: 10px;
        font-weight: 400;
    }
    .apple-badge {
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        background: rgba(255, 255, 255, 0.08);
        color: #d1d1d6;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        font-family: 'JetBrains Mono', monospace;
    }

    /* Cam Kart Yapısı */
    .apple-card {
        background: rgba(28, 28, 30, 0.4);
        backdrop-filter: blur(25px) saturate(180%);
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 22px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .apple-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Analiz Paneli */
    .analysis-panel {
        background: rgba(10, 132, 255, 0.08);
        border: 1px solid rgba(10, 132, 255, 0.25);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }

    /* Metrik Izgaraları */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    .apple-metric-label {
        font-size: 11px;
        font-weight: 500;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 8px;
    }
    .apple-metric-val {
        font-size: 26px;
        font-weight: 600;
        letter-spacing: -0.8px;
        color: #f5f5f7;
        font-family: 'JetBrains Mono', monospace;
    }
    .apple-metric-sub {
        font-size: 12px;
        color: #86868b;
        margin-top: 6px;
    }

    /* Zaman Etiketleri */
    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        padding: 3px 6px;
        border-radius: 4px;
        margin-top: 8px;
        display: inline-block;
    }
    .time-fresh { background: rgba(48, 209, 88, 0.12); color: #30d158; border: 1px solid rgba(48, 209, 88, 0.2); }
    .time-stale { background: rgba(255, 159, 10, 0.12); color: #ff9f0a; border: 1px solid rgba(255, 159, 10, 0.2); }

    /* İnput ve Form Özelleştirmeleri */
    div[data-baseweb="input"] {
        background-color: rgba(44, 44, 46, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #0a84ff !important;
        box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.2) !important;
    }

    /* Aksiyon Butonu */
    .stButton>button {
        background: #0071e3 !important;
        color: #ffffff !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: #0077ed !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI & COĞRAFİ BİLGİLER ---
CITY_BONUSES = {
    "Lif (Fiber)": "Lymhurst",
    "Odun (Wood)": "Fort Sterling",
    "Cevher (Ore)": "Thetford",
    "Deri (Hide)": "Martlock",
    "Taş (Stone)": "Bridgewatch"
}

RESOURCE_INTERNAL = {
    "Lif (Fiber)": {"raw": "FIBER", "refined": "CLOTH", "tr_raw": "Ham Lif", "tr_ref": "Kumaş"},
    "Odun (Wood)": {"raw": "WOOD", "refined": "PLANKS", "tr_raw": "Ham Odun", "tr_ref": "Kalas"},
    "Cevher (Ore)": {"raw": "ORE", "refined": "METALBAR", "tr_raw": "Ham Cevher", "tr_ref": "Külçe"},
    "Deri (Hide)": {"raw": "HIDE", "refined": "LEATHER", "tr_raw": "Ham Deri", "tr_ref": "İşlenmiş Deri"},
    "Taş (Stone)": {"raw": "ROCK", "refined": "STONEBLOCK", "tr_raw": "Ham Taş", "tr_ref": "Taş Blok"}
}

FAME_VALUES = {
    "T2": 1.5, "T3": 7.5, "T4": 22.5, "T5": 90, "T6": 270, "T7": 645, "T8": 1350
}

# --- BAŞLIK BÖLÜMÜ ---
st.markdown("""
<div class="apple-nav">
    <div style="display: flex; align-items: center;">
        <span class="apple-logo-text">KMZ Studio</span>
        <span class="apple-sub">Enterprise Finans ve Tedarik Analiz Terminali</span>
    </div>
    <div style="display: flex; gap: 8px;">
        <span class="apple-badge">v9.0 Kusursuz Sürüm</span>
        <span class="apple-badge" style="color: #30d158; border-color: rgba(48, 209, 88, 0.2);">● Çevrimiçi</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- KONTROL PANELİ (SİDEBAR) ---
st.sidebar.markdown("### ⚙️ Sistem Konfigürasyonu")

if st.sidebar.button("Piyasa Verilerini Senkronize Et", use_container_width=True):
    st.cache_data.clear()

server = st.sidebar.selectbox("Bölgesel Sunucu", ["europe", "west", "east"], index=0)
selected_resource = st.sidebar.selectbox("Materyal Sınıfı", list(CITY_BONUSES.keys()))

col_t, col_e = st.sidebar.columns(2)
with col_t:
    selected_tier = st.selectbox("Hedef Seviye", [f"T{i}" for i in range(2, 9)], index=3)
with col_e:
    enchant_choice = st.selectbox("Işıma (Enchant)", [".0 (Düz)", ".1 (Yeşil)", ".2 (Mavi)", ".3 (Mor)", ".4 (Altın)"], index=0)
    enchant_lvl = int(enchant_choice[1])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ Vergi ve Emir Politikası")

sell_as_order = st.sidebar.toggle(
    "Satış Emri İle Sat (Sell Order)", 
    value=True, 
    help="Aktifken pazar tahtasına ilan bırakırsınız (Kurulum vergisi eklenir). Kapalıyken bekleyen alıcılara anında satarsınız."
)
buy_order_mode = st.sidebar.checkbox("Tedariki 'Alış Emri' (Buy Order) İle Yap", value=False)
has_premium = st.sidebar.checkbox("Premium Vergi İndirimi Geçerli", value=True)

base_tax = 0.04 if has_premium else 0.08
setup_tax = 0.025 if sell_as_order else 0.0
total_market_tax = base_tax + setup_tax

use_focus = st.sidebar.checkbox("Odaklanma Puanı (Focus) Kullan", value=False)
default_rrr = 53.9 if use_focus else 36.7
rrr_percent = st.sidebar.number_input("Materyal Geri Dönüş Oranı (RRR %)", min_value=0.0, max_value=100.0, value=default_rrr, step=0.1)
rrr = rrr_percent / 100.0
focus_per_unit = st.sidebar.number_input("Birim Başına Focus Maliyeti", min_value=1, max_value=2000, value=112, step=1) if use_focus else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Coğrafi Konumlar")
cities = ["Bridgewatch", "Fort Sterling", "Lymhurst", "Martlock", "Thetford", "Caerleon"]
buy_city = st.sidebar.selectbox("Tedarik Şehri", cities, index=1)
refine_city = st.sidebar.selectbox("İşleme İstasyonu", cities, index=cities.index(CITY_BONUSES[selected_resource]))
sell_city = st.sidebar.selectbox("Hedef Pazar", cities, index=cities.index(CITY_BONUSES[selected_resource]))

station_fee = st.sidebar.number_input("Tesis Kullanım Bedeli (%)", min_value=0, max_value=9999, value=335, step=5)

ideal_city = CITY_BONUSES[selected_resource]
if refine_city != ideal_city:
    st.markdown(f"""
    <div style="background: rgba(255, 159, 10, 0.1); border: 1px solid rgba(255, 159, 10, 0.3); border-radius: 8px; padding: 10px 14px; margin-top: 10px;">
        <span style="font-weight: 500; font-size: 12px; color: #ff9f0a;">Verimlilik Uyarısı:</span> 
        <span style="font-size: 12px; color: #d1d1d6;">{selected_resource} için maksimum verim {ideal_city} şehrindedir. Mevcut konum ({refine_city}) kârlılığı düşürebilir.</span>
    </div>
    """, unsafe_allow_html=True)

# --- MATEMATİKSEL MOTOR & ZİNCİR TARİFLERİ ---
RECIPES = {
    "T2": {"raw": 1, "lower": 0}, "T3": {"raw": 2, "lower": 1}, "T4": {"raw": 2, "lower": 1},
    "T5": {"raw": 3, "lower": 1}, "T6": {"raw": 4, "lower": 1}, "T7": {"raw": 5, "lower": 1},
    "T8": {"raw": 5, "lower": 1},
}
ITEM_VALUES = {"T2": 2, "T3": 6, "T4": 14, "T5": 38, "T6": 102, "T7": 262, "T8": 582}
RAW_WEIGHTS = {"T2": 0.3, "T3": 0.5, "T4": 0.7, "T5": 0.9, "T6": 1.2, "T7": 1.5, "T8": 1.9}

tier_num = int(selected_tier[1])
raw_prefix = RESOURCE_INTERNAL[selected_resource]["raw"]
refined_prefix = RESOURCE_INTERNAL[selected_resource]["refined"]
tr_refined_name = RESOURCE_INTERNAL[selected_resource]["tr_ref"]
tr_raw_name = RESOURCE_INTERNAL[selected_resource]["tr_raw"]

target_amount = st.number_input(
    f"Hedeflenen Üretim Hacmi ({selected_tier}{'' if enchant_lvl == 0 else '.' + str(enchant_lvl)} {tr_refined_name})",
    min_value=1,
    value=2500,
    step=100
)

tier_data = {}
current_target = target_amount
total_crafting_fee_zh = 0 
total_weight_zh = 0.0
total_fame_zh = 0

for t in range(tier_num, 1, -1):
    tier_key = f"T{t}"
    t_enc = enchant_lvl if t >= 4 else 0
    crafts_needed = current_target

    enchant_mult = 1 if t_enc == 0 else (2 ** t_enc)
    item_val = ITEM_VALUES[tier_key] * enchant_mult
    tier_craft_cost = crafts_needed * item_val * 0.1125 * (station_fee / 100)
    total_crafting_fee_zh += tier_craft_cost

    base_fame = FAME_VALUES[tier_key] * enchant_mult
    total_fame_zh += crafts_needed * base_fame

    raw_mult = RECIPES[tier_key]["raw"]
    raw_needed = int(round(current_target * raw_mult * (1 - rrr)))

    if t_enc > 0:
        api_req_ids = [
            f"{tier_key}_{raw_prefix}_LEVEL{t_enc}@{t_enc}",
            f"{tier_key}_{raw_prefix}@{t_enc}"
        ]
        display_name = f"{tier_key}.{t_enc} {tr_raw_name}"
    else:
        api_req_ids = [f"{tier_key}_{raw_prefix}"]
        display_name = f"{tier_key} {tr_raw_name}"

    lower_tier_key = f"T{t-1}" if t > 2 else None
    lower_enc = enchant_lvl if (t-1) >= 4 else 0
    lower_refined_api_ids = []
    
    if lower_tier_key:
        if lower_enc > 0:
             lower_refined_api_ids = [
                f"{lower_tier_key}_{refined_prefix}_LEVEL{lower_enc}@{lower_enc}",
                f"{lower_tier_key}_{refined_prefix}@{lower_enc}"
             ]
        else:
             lower_refined_api_ids = [f"{lower_tier_key}_{refined_prefix}"]

    tier_data[tier_key] = {
        "amount": raw_needed,
        "enchant": t_enc,
        "display": display_name,
        "api_ids": api_req_ids,
        "lower_refined_api_ids": lower_refined_api_ids,
        "lower_tier_needed": int(round(current_target * RECIPES[tier_key]["lower"] * (1 - rrr))) if lower_tier_key else 0
    }

    total_weight_zh += raw_needed * RAW_WEIGHTS[tier_key]

    lower_mult = RECIPES[tier_key]["lower"]
    if lower_mult > 0:
        current_target = current_target * lower_mult * (1 - rrr)

if enchant_lvl > 0:
    sell_api_ids = [
        f"T{tier_num}_{refined_prefix}_LEVEL{enchant_lvl}@{enchant_lvl}",
        f"T{tier_num}_{refined_prefix}@{enchant_lvl}"
    ]
    sell_display_name = f"T{tier_num}.{enchant_lvl} {tr_refined_name}"
    primary_sell_id = sell_api_ids[0]
else:
    sell_api_ids = [f"T{tier_num}_{refined_prefix}"]
    sell_display_name = f"T{tier_num} {tr_refined_name}"
    primary_sell_id = sell_api_ids[0]

all_buy_ids = [aid for data in tier_data.values() for aid in data["api_ids"]]
all_lower_refined_ids = [aid for data in tier_data.values() for aid in data["lower_refined_api_ids"]]
all_fetch_ids = list(set(all_buy_ids + all_lower_refined_ids + sell_api_ids))

all_cities = list(set([buy_city, sell_city, "Caerleon"]))

# --- CANLI PİYASA APİ BAĞLANTILARI ---
@st.cache_data(ttl=60)
def fetch_market_data(server_name, item_ids, cities_list):
    if not item_ids or not cities_list: return []
    ids_str = urllib.parse.quote(",".join(item_ids))
    cities_str = urllib.parse.quote(",".join(cities_list))
    url = f"https://{server_name}.albion-online-data.com/api/v2/stats/Prices/{ids_str}.json?locations={cities_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

@st.cache_data(ttl=60)
def fetch_order_depth(server_name, item_id, city_name):
    url = f"https://{server_name}.albion-online-data.com/api/v2/stats/view/{item_id}.json?locations={city_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

def format_time_diff(date_str):
    if not date_str or date_str.startswith("0001"):
        return "Bilinmiyor", False
    try:
        clean_str = date_str.split(".")[0].replace("Z", "")
        dt = datetime.fromisoformat(clean_str).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (now - dt).total_seconds()
        
        if diff < 3600:
            return f"{int(diff // 60)} dk önce", True
        elif diff < 86400:
            return f"{int(diff // 3600)} saat önce", True
        else:
            return f"{int(diff // 86400)} gün önce", False
    except Exception:
        return "Bilinmiyor", False

with st.spinner("Piyasa verileri eşzamanlanıyor..."):
    raw_api_data = fetch_market_data(server, all_fetch_ids, all_cities)
    depth_data = fetch_order_depth(server, primary_sell_id, sell_city)

buy_prices_raw = {}
buy_time_labels = {}
buy_prices_refined_lower = {} 

sell_order_price = 0
sell_instant_price = 0
sell_time_label = ("Bilinmiyor", False)
black_market_buy_price = 0

for entry in raw_api_data:
    item = entry.get("item_id")
    city = entry.get("city")
    sell_min = entry.get("sell_price_min", 0)
    buy_max = entry.get("buy_price_max", 0)
    sell_date = entry.get("sell_price_min_date", "")

    if city == buy_city:
        p_raw = sell_min if sell_min > 0 else buy_max
        for t_k, t_v in tier_data.items():
            if item in t_v["api_ids"] and p_raw > 0:
                if t_k not in buy_prices_raw or p_raw < buy_prices_raw[t_k]:
                    buy_prices_raw[t_k] = p_raw
                    buy_time_labels[t_k] = format_time_diff(sell_date)
            
            if item in t_v["lower_refined_api_ids"] and p_raw > 0:
                if t_k not in buy_prices_refined_lower or p_raw < buy_prices_refined_lower[t_k]:
                    buy_prices_refined_lower[t_k] = p_raw

    if city == sell_city and (item in sell_api_ids):
        if sell_min > 0 and (sell_order_price == 0 or sell_min < sell_order_price):
            sell_order_price = sell_min
            sell_time_label = format_time_diff(sell_date)
        if buy_max > 0 and (sell_instant_price == 0 or buy_max > sell_instant_price):
            sell_instant_price = buy_max
            
    if city == "Black Market" and (item in sell_api_ids):
        if buy_max > 0 and (black_market_buy_price == 0 or buy_max > black_market_buy_price):
            black_market_buy_price = buy_max

if sell_as_order:
    calculated_sell_price = sell_order_price if sell_order_price > 0 else sell_instant_price
else:
    calculated_sell_price = sell_instant_price if sell_instant_price > 0 else sell_order_price

# --- BÖLÜM 1: ZİNCİR REÇETE PORTFÖYÜ ---
st.markdown("<p style='font-size: 12px; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 20px; margin-bottom: 12px;'>I. Hammadde Tedarik Çizelgesi (Tam Zincir)</p>", unsafe_allow_html=True)
cols = st.columns(len(tier_data))

for i, (t_k, t_v) in enumerate(tier_data.items()):
    t_label, is_fresh = buy_time_labels.get(t_k, ("Bilinmiyor", False))
    time_class = "time-fresh" if is_fresh else "time-stale"
    
    cols[i].markdown(f"""
    <div class="apple-card" style="text-align: center;">
        <div style="font-size: 12px; font-weight: 500; color: #86868b;">{t_v['display']}</div>
        <div style="font-size: 26px; font-weight: 700; color: #f5f5f7; margin: 4px 0; letter-spacing: -0.5px;">{t_v['amount']:,}</div>
        <div style="font-size: 11px; color: #48484a; font-family: monospace;">{t_k}_{raw_prefix}</div>
        <span class="time-badge {time_class}">{t_label}</span>
    </div>
    """, unsafe_allow_html=True)

# --- BÖLÜM 2: PİYASA FİYATLARI VE MÜDAHALE FORMU ---
st.markdown("<p style='font-size: 12px; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 30px; margin-bottom: 12px;'>II. Canlı Fiyatlandırma Paneli (Gümüş)</p>", unsafe_allow_html=True)

with st.form("price_input_form"):
    num_cols = len(tier_data) + 2 if tier_num >= 3 else len(tier_data) + 1
    input_cols = st.columns(num_cols)
    price_inputs = {}

    for i, (t_k, t_v) in enumerate(tier_data.items()):
        api_p = int(buy_prices_raw.get(t_k, 0))
        if buy_order_mode and api_p > 0:
            api_p = int(api_p * 0.85)
        price_inputs[t_k] = input_cols[i].number_input(f"Birim Maliyet: {t_v['display']}", value=api_p, step=1)

    lower_tier_price_input = 0
    if tier_num >= 3:
        target_key = f"T{tier_num}"
        lower_tier_key = f"T{tier_num-1}"
        lower_enc = enchant_lvl if (tier_num-1) >= 4 else 0
        lower_ref_display = f"{lower_tier_key}.{lower_enc} {tr_refined_name}" if lower_enc > 0 else f"{lower_tier_key} {tr_refined_name}"
        
        api_lower_ref_p = int(buy_prices_refined_lower.get(target_key, 0))
        if buy_order_mode and api_lower_ref_p > 0:
            api_lower_ref_p = int(api_lower_ref_p * 0.85)
            
        lower_tier_price_input = input_cols[-2].number_input(f"Ara Mamul: {lower_ref_display}", value=api_lower_ref_p, step=1)

    sell_label = f"Satış Fiyatı: {sell_display_name}"
    sell_price_input = input_cols[-1].number_input(sell_label, value=int(calculated_sell_price), step=1)
    
    submit_prices = st.form_submit_button("Hesaplamaları Senkronize Et", use_container_width=True)

# Piyasa Derinliği Özet Barı
st.markdown(f"""
<div style="display: flex; gap: 12px; margin-top: -6px; margin-bottom: 24px; flex-wrap: wrap;">
    <span class="apple-badge">Minimum Satış Emri: <b>{sell_order_price:,} 🥈</b></span>
    <span class="apple-badge">Maksimum Alış Teklifi: <b>{sell_instant_price:,} 🥈</b></span>
    <span class="apple-badge" style="background: rgba(10, 132, 255, 0.12); color: #0a84ff; border-color: rgba(10, 132, 255, 0.2);">Karaborsa Alış Fiyatı: <b>{black_market_buy_price:,} 🥈</b></span>
</div>
""", unsafe_allow_html=True)

# --- BÖLÜM 3: TEDARİK STRATEJİSİ (MAKE VS BUY) ---
cost_zh = 0
cost_buy_lower = 0
savings = 0
make_vs_buy_decision = "Tam Zincir Rafinasyon"

if tier_num >= 3:
    target_key = f"T{tier_num}"
    target_data = tier_data[target_key]
    
    # Tam Zincir Üretim
    cost_zh_raw = sum([t_v["amount"] * price_inputs[t_k] for t_k, t_v in tier_data.items()])
    cost_zh = cost_zh_raw + total_crafting_fee_zh
    
    # Ara Mamul Tedariki ile Üretim
    cost_buy_lower_raw = target_data["amount"] * price_inputs[target_key]
    cost_buy_lower_refined = target_data["lower_tier_needed"] * lower_tier_price_input
    
    enc_m = 1 if target_data["enchant"] == 0 else (2 ** target_data["enchant"])
    fee_only_top = target_amount * (ITEM_VALUES[target_key] * enc_m) * 0.1125 * (station_fee / 100)
    
    cost_buy_lower = cost_buy_lower_raw + cost_buy_lower_refined + fee_only_top
    
    if cost_buy_lower > 0 and cost_zh > 0:
        if cost_buy_lower < cost_zh:
            make_vs_buy_decision = "Ara Mamul Tedariki (Hazır Al)"
            savings = cost_zh - cost_buy_lower
        else:
            make_vs_buy_decision = "Tam Zincir Rafinasyon (Sıfırdan Üret)"
            savings = cost_buy_lower - cost_zh
    else:
        make_vs_buy_decision = "Veri Bekleniyor"

if tier_num >= 3 and cost_zh > 0 and cost_buy_lower > 0:
    st.markdown(f"""
    <div class="analysis-panel">
        <div style="font-size: 11px; font-weight: 600; color: #0a84ff; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;">Stratejik Tedarik Optimizasyonu</div>
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 14px; color: #e2e8f0; margin-bottom: 4px;">Tam Zincir Rafinasyon Maliyeti: <span style="font-family: 'JetBrains Mono', monospace; font-weight: 500; color: #d1d1d6;">{cost_zh:,.0f} 🥈</span></div>
                <div style="font-size: 14px; color: #e2e8f0;">Ara Mamul Satın Alımı ile Maliyet: <span style="font-family: 'JetBrains Mono', monospace; font-weight: 500; color: #d1d1d6;">{cost_buy_lower:,.0f} 🥈</span></div>
            </div>
            <div style="text-align: right; background: rgba(0,0,0,0.25); padding: 12px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 11px; color: #86868b; margin-bottom: 2px;">SİSTEM ÖNERİSİ</div>
                <div style="font-size: 18px; font-weight: 600; color: {'#30d158' if make_vs_buy_decision == 'Ara Mamul Tedariki (Hazır Al)' else '#f5f5f7'};">{make_vs_buy_decision}</div>
                <div style="font-size: 12px; color: #30d158; margin-top: 4px;">Fiyat Avantajı: {savings:,.0f} 🥈</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("Gelişmiş Seçenekler: Yan Ürün Hasılatı (İşçi Defterleri)"):
    use_journals = st.checkbox("Üretim esnasında 'Generalist Journal' doldurulacak", value=False)
    journal_extra_profit = 0
    if use_journals:
        j1, j2 = st.columns(2)
        empty_j = j1.number_input("Boş Defter Tedarik Fiyatı", value=1500, step=100)
        full_j = j2.number_input("Dolu Defter Satış Fiyatı", value=7500, step=100)
        journals_filled = int(target_amount / 120)
        journal_extra_profit = max(0, journals_filled * (full_j - empty_j))
        st.caption(f"Öngörülen Dolum Hacmi: {journals_filled} Birim | Ekstra Yan Ürün Net Kârı: +{journal_extra_profit:,.0f} 🥈")

# --- BÖLÜM 4: FİNANSAL TABLO & BİLANÇO ---
total_raw_cost = sum([tier_data[t_k]["amount"] * price_inputs[t_k] for t_k in tier_data.keys()])
gross_revenue = target_amount * sell_price_input
total_tax_amount = gross_revenue * total_market_tax
net_revenue = gross_revenue - total_tax_amount 

total_profit = net_revenue - total_raw_cost - total_crafting_fee_zh + journal_extra_profit
margin = (total_profit / gross_revenue * 100) if gross_revenue > 0 else 0.0

total_gross_costs = total_raw_cost + total_crafting_fee_zh - journal_extra_profit
break_even_price = math.ceil(total_gross_costs / (target_amount * (1 - total_market_tax))) if target_amount > 0 else 0

st.markdown("<p style='font-size: 12px; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 20px; margin-bottom: 12px;'>III. Kurumsal Finansal Bilanço (Tam Zincir)</p>", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-grid">
    <div class="apple-card">
        <div class="apple-metric-label">Hammadde Maliyeti</div>
        <div class="apple-metric-val">{total_raw_cost:,.0f} <span style="font-size: 16px; color: #86868b;">🥈</span></div>
    </div>
    <div class="apple-card">
        <div class="apple-metric-label">Tesis Kullanım Bedeli</div>
        <div class="apple-metric-val">-{total_crafting_fee_zh:,.0f} <span style="font-size: 16px; color: #86868b;">🥈</span></div>
    </div>
    <div class="apple-card">
        <div class="apple-metric-label">Brüt Pazar Hasılatı</div>
        <div class="apple-metric-val">{net_revenue:,.0f} <span style="font-size: 16px; color: #86868b;">🥈</span></div>
    </div>
    <div class="apple-card" style="background: rgba(48, 209, 88, 0.05); border-color: rgba(48, 209, 88, 0.2);">
        <div class="apple-metric-label" style="color: #30d158;">Net Kâr Dağılımı</div>
        <div class="apple-metric-val" style="color: #30d158;">{total_profit:,.0f} <span style="font-size: 16px;">🥈</span></div>
        <div class="apple-metric-sub" style="color: #30d158;">%{margin:.1f} Özkaynak Kârlılığı</div>
    </div>
</div>
""", unsafe_allow_html=True)

i1, i2 = st.columns(2)
with i1:
    st.markdown(f"""
    <div class="apple-card" style="padding: 14px 18px;">
        <span style="font-size: 11px; color: #86868b; text-transform: uppercase; font-weight: 500;">Başabaş Noktası (Break-Even)</span>
        <div style="font-size: 18px; font-weight: 600; color: #f5f5f7; margin-top: 4px;">{break_even_price:,} 🥈 <span style="font-size: 12px; color: #6e6e73; font-weight: 400;">/ birim asgari satış tutarı</span></div>
    </div>
    """, unsafe_allow_html=True)
with i2:
    st.markdown(f"""
    <div class="apple-card" style="padding: 14px 18px;">
        <span style="font-size: 11px; color: #86868b; text-transform: uppercase; font-weight: 500;">Tahmini Şöhret (Fame)</span>
        <div style="font-size: 18px; font-weight: 600; color: #f5f5f7; margin-top: 4px;">+{total_fame_zh:,.0f} Fame <span style="font-size: 12px; color: #6e6e73; font-weight: 400;">deneyim puanı</span></div>
    </div>
    """, unsafe_allow_html=True)

if use_focus:
    total_focus_used = target_amount * focus_per_unit
    spf = (total_profit / total_focus_used) if total_focus_used > 0 else 0
    st.markdown(f"""
    <div style="background: rgba(10, 132, 255, 0.05); border: 1px solid rgba(10, 132, 255, 0.15); border-radius: 12px; padding: 12px 18px; margin-top: 14px;">
        <span style="font-weight: 500; font-size: 13px; color: #0a84ff;">Odaklanma (Focus) Verimlilik Raporu:</span> 
        <span style="font-size: 13px; color: #d1d1d6;">Harcanan: <b>{total_focus_used:,} Focus</b> | Verim: <b>{spf:.1f} Gümüş / Focus</b></span>
    </div>
    """, unsafe_allow_html=True)

# --- BÖLÜM 5: EMİR DEFTERİ (ORDER BOOK) ---
st.markdown("<p style='font-size: 12px; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 30px; margin-bottom: 12px;'>IV. Piyasa Derinliği ve Emir Defteri (Son İşlemler)</p>", unsafe_allow_html=True)

if depth_data:
    df_raw = pd.DataFrame(depth_data)
    col_sell_order, col_buy_order = st.columns(2)
    
    with col_sell_order:
        st.markdown("<span style='font-size: 11px; color: #ff453a; font-weight: 600; letter-spacing: 0.5px;'>SATIŞ EMİRLERİ (ASK)</span>", unsafe_allow_html=True)
        if "sell_price_min" in df_raw.columns:
            df_sells = df_raw[df_raw["sell_price_min"] > 0][["city", "sell_price_min", "sell_price_min_date"]].copy()
            df_sells.columns = ["Lokasyon", "Birim Fiyat", "Zaman Damgası"]
            df_sells = df_sells.sort_values(by="Birim Fiyat", ascending=True).head(10)
            st.dataframe(df_sells, use_container_width=True, hide_index=True)
        else:
            st.caption("Aktif satış emri bulunmamaktadır.")

    with col_buy_order:
        st.markdown("<span style='font-size: 11px; color: #30d158; font-weight: 600; letter-spacing: 0.5px;'>ALIŞ TEKLİFLERİ (BID)</span>", unsafe_allow_html=True)
        if "buy_price_max" in df_raw.columns:
            df_buys = df_raw[df_raw["buy_price_max"] > 0][["city", "buy_price_max", "buy_price_max_date"]].copy()
            df_buys.columns = ["Lokasyon", "Birim Fiyat", "Zaman Damgası"]
            df_buys = df_buys.sort_values(by="Birim Fiyat", ascending=False).head(10)
            st.dataframe(df_buys, use_container_width=True, hide_index=True)
        else:
            st.caption("Aktif alış teklifi bulunmamaktadır.")
else:
    st.info("Bu varlık için bölgesel emir defteri verisi şu an mevcut değil.")

# --- BÖLÜM 6: LOJİSTİK VE YÜK HESABI ---
st.markdown("<p style='font-size: 12px; font-weight: 600; color: #86868b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 30px; margin-bottom: 12px;'>V. Lojistik ve Sevkiyat Planlaması</p>", unsafe_allow_html=True)
c_w1, c_w2 = st.columns(2)

MOUNTS = {
    "T8 Elder's Taşıma Öküzü (3,347 kg)": 3347,
    "T7 Grandmaster's Öküzü (2,700 kg)": 2700,
    "T6 Master's Öküzü (2,150 kg)": 2150,
    "T5 Expert's Öküzü (1,650 kg)": 1650,
    "Taşıma Mamutu (28,000 kg)": 28000,
    "Özel Yük Kapasitesi Girin": 0
}
selected_mount = c_w1.selectbox("Nakliye Bineği Sınıfı", list(MOUNTS.keys()), index=0)

if selected_mount == "Özel Yük Kapasitesi Girin":
    mount_cap = c_w1.number_input("Taşıma Kapasitesi (kg)", min_value=1, value=3347, step=50)
else:
    mount_cap = MOUNTS[selected_mount]

eat_pork_pie = c_w1.checkbox("Pork Pie Etkisi Geçerli (+%30 Taşıma Kapasitesi)", value=False)
if eat_pork_pie:
    mount_cap = int(mount_cap * 1.30)

trips_needed = math.ceil(total_weight_zh / mount_cap) if mount_cap > 0 else 1

with c_w2:
    st.markdown(f"""
    <div class="apple-card" style="padding: 16px 20px;">
        <div style="font-size: 11px; font-weight: 500; color: #86868b; text-transform: uppercase;">Toplam Sevkiyat Hacmi</div>
        <div style="font-size: 22px; font-weight: 600; color: #f5f5f7; margin-top: 2px;">{total_weight_zh:,.1f} kg</div>
        <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 10px 0;">
        <div style="font-size: 11px; font-weight: 500; color: #86868b; text-transform: uppercase;">Gereken Lojistik Seferi</div>
        <div style="font-size: 22px; font-weight: 600; color: #0a84ff; margin-top: 2px;">{trips_needed} Tur <span style="font-size: 12px; color: #6e6e73; font-weight: 400;">({mount_cap:,} kg kapasite)</span></div>
    </div>
    """, unsafe_allow_html=True)

# Mesafe Analizi
distances = {
    "Fort Sterling": {"Lymhurst": 4, "Thetford": 5, "Martlock": 7, "Bridgewatch": 6},
    "Thetford": {"Fort Sterling": 5, "Lymhurst": 7, "Martlock": 4, "Bridgewatch": 5},
    "Martlock": {"Thetford": 4, "Fort Sterling": 7, "Lymhurst": 6, "Bridgewatch": 3},
    "Bridgewatch": {"Martlock": 3, "Thetford": 5, "Fort Sterling": 6, "Lymhurst": 4},
    "Lymhurst": {"Bridgewatch": 4, "Martlock": 6, "Thetford": 7, "Fort Sterling": 4}
}

if buy_city != sell_city and buy_city != "Caerleon" and sell_city != "Caerleon":
    zones = distances[buy_city][sell_city]
    one_trip_time = zones * 1.5
    total_time = trips_needed * one_trip_time
    st.caption(f"📍 **Güzergah:** {buy_city} ➔ {sell_city} ({zones} Sektör) • Tahmini Nakliye Süresi: **~{total_time:.1f} Dakika**")
elif buy_city == "Caerleon" or sell_city == "Caerleon":
    st.markdown("""
    <div style="background: rgba(255, 69, 58, 0.08); border: 1px solid rgba(255, 69, 58, 0.2); border-radius: 12px; padding: 10px 14px; margin-top: 10px;">
        <span style="font-weight: 600; color: #ff453a;">Güvenlik İhlali Riski:</span> Caerleon güzergahı Red Zone (PVP) içermektedir. Nakliyede zırhlı binek kullanımı zorunludur.
    </div>
    """, unsafe_allow_html=True)

# --- ALT BİLGİ ---
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; color: #48484a; font-size: 12px; padding: 12px 0;">
    <div>KMZ Studio • Kurumsal Arbitraj Terminali v9.0</div>
    <div>Tüm sistemler aktiftir.</div>
</div>
""", unsafe_allow_html=True)

