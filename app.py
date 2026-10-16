import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone
import math
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enlil Zincirleme Refine", layout="wide", initial_sidebar_state="expanded")

# --- OYUN TEMASI (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #18202C 0%, #0B0E14 100%) !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #11161F !important;
        border-right: 2px solid #4A3B23;
    }

    .header-banner {
        font-family: 'Cinzel', serif;
        text-align: center;
        padding: 15px;
        margin-bottom: 18px;
        background: linear-gradient(180deg, #1E2631 0%, #11161D 100%);
        border: 2px solid #8A6D3B;
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(185, 147, 90, 0.2);
    }

    .header-banner h1 {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        color: #E2C38F !important;
        letter-spacing: 1.5px;
    }

    .header-banner p {
        color: #94A3B8;
        margin: 4px 0 0 0;
        font-size: 13px;
    }

    .locked-city-box {
        background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #38BDF8;
        border-left: 5px solid #38BDF8;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 14px;
        font-size: 14px;
    }

    .step-card {
        background: linear-gradient(135deg, #161E29 0%, #0F141C 100%);
        border: 1px solid #334155;
        border-left: 4px solid #D4AF37;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .profit-card-gold {
        background: linear-gradient(135deg, #231D14 0%, #12151A 100%);
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.25);
        margin-bottom: 14px;
    }

    .profit-card-blue {
        background: linear-gradient(135deg, #10212B 0%, #12151A 100%);
        border: 2px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
        margin-bottom: 14px;
    }

    .fast-cash-alert {
        background: linear-gradient(90deg, #065F46 0%, #064E3B 100%);
        border: 1px solid #10B981;
        color: #A7F3D0;
        padding: 10px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 13.5px;
        margin-top: 8px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #5C4728 0%, #2C2011 100%) !important;
        color: #F3E5AB !important;
        border: 1px solid #B9935A !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
st.markdown("""
<div class="header-banner">
    <h1>🛡️ ENLİL - ZİNCİRLEME (T2 ➔ HEDEF TIER) REFINE HESAPLAYICI</h1>
    <p>Sıfırdan Ham Madde Alış Listesi • Otomatik Bonus Şehri • Sell Order vs Sıcak Para (Buy Order) Kıyaslaması</p>
</div>
""", unsafe_allow_html=True)

# --- KAYNAK TANIMLARI ---
RESOURCES = {
    "🌿 Elyaf / Pamuk (Fiber ➔ Cloth)": {
        "raw": "FIBER", "refined": "CLOTH", "bonus_city": "Lymhurst",
        "raw_name": "Ham Pamuk (Fiber)", "ref_name": "Kumaş (Cloth)"
    },
    "⛏️ Cevher (Ore ➔ Metal Bar)": {
        "raw": "ORE", "refined": "METALBAR", "bonus_city": "Thetford",
        "raw_name": "Cevher (Ore)", "ref_name": "Demir Külçe (Bar)"
    },
    "🐾 Deri (Hide ➔ Leather)": {
        "raw": "HIDE", "refined": "LEATHER", "bonus_city": "Martlock",
        "raw_name": "Ham Deri (Hide)", "ref_name": "İşlenmiş Deri (Leather)"
    },
    "🌲 Odun (Wood ➔ Planks)": {
        "raw": "WOOD", "refined": "PLANKS", "bonus_city": "Fort Sterling",
        "raw_name": "Tomruk (Wood)", "ref_name": "Kalas (Planks)"
    },
    "🪨 Taş (Stone ➔ Stone Block)": {
        "raw": "STONE", "refined": "STONEBLOCK", "bonus_city": "Bridgewatch",
        "raw_name": "Kaya (Stone)", "ref_name": "Taş Blok (Block)"
    }
}

# Her Tier için 1 adet üretimde gereken Ham Madde sayısı
RAW_PER_CRAFT = {2: 1, 3: 2, 4: 2, 5: 3, 6: 4, 7: 5, 8: 5}
ROYAL_CITIES = ["Lymhurst", "Bridgewatch", "Martlock", "Thetford", "Fort Sterling"]

# --- SOL MENÜ: 1. NE ÜRETECEKSİN? ---
st.sidebar.header("🎯 1. Hedef Üretim Seçimi")
selected_res_key = st.sidebar.selectbox("Kaynak Türü:", list(RESOURCES.keys()), index=0)
res_meta = RESOURCES[selected_res_key]
locked_refine_city = res_meta["bonus_city"]

st.sidebar.markdown(f"""
<div class="locked-city-box">
    🔒 <b>Rafinasyon Şehri (Sabit Bonus):</b><br>
    <span style="color:#38BDF8; font-size:16px; font-weight:800;">{locked_refine_city} (+%40 Bonus)</span>
</div>
""", unsafe_allow_html=True)

col_t, col_e = st.sidebar.columns(2)
with col_t:
    target_tier_str = st.selectbox("Hedef Tier:", ["T3", "T4", "T5", "T6", "T7", "T8"], index=2) # Varsayılan T5
    target_tier = int(target_tier_str.replace("T", ""))

with col_e:
    if target_tier == 3 or res_meta["raw"] == "STONE":
        target_enc = st.selectbox("Enchant:", [".0"], disabled=True)
    else:
        target_enc = st.selectbox("Enchant:", [".0", ".1", ".2", ".3", ".4"], index=0)

target_qty = st.sidebar.number_input("Hedef Üretim Adedi (Örn: 5000):", min_value=1, value=5000, step=500)

# --- SOL MENÜ: 2. NEREDEN ALIP NEREDE SATACAKSIN? ---
st.sidebar.markdown("---")
st.sidebar.header("🗺️ 2. Alış ve Satış Şehirleri")

include_caerleon = st.sidebar.checkbox("Caerleon'u Dahil Et", value=False)
active_cities = ROYAL_CITIES + (["Caerleon"] if include_caerleon else [])

auto_cheapest = "🌟 Otomatik (Her Tier İçin En Ucuz Şehir)"
auto_expensive = "💰 Otomatik (En Pahalı Şehir)"

buy_city_mode = st.sidebar.selectbox(
    "Ham Madde Alış Şehri:",
    options=[auto_cheapest] + active_cities,
    index=0,
    help="İster tek bir şehir seç, ister Otomatik bırakıp her tier ham maddeyi en ucuz hangi şehirdeyse oradan çek."
)

sell_city_mode = st.sidebar.selectbox(
    "Son Ürünü Satacağın Şehir:",
    options=[auto_expensive] + active_cities,
    index=0
)

raw_buy_type = st.sidebar.radio(
    "Ham Madde Alım Yöntemi:",
    ("⚡ Direkt Çek (Sell Order Fiyatından)", "⏳ Alış Emri Kur (Buy Order +%2.5 Kurulum)"),
    index=0
)
use_bo_for_raw = ("Buy Order" in raw_buy_type)

# --- SOL MENÜ: 3. RRR VE VERGİ ---
st.sidebar.markdown("---")
st.sidebar.header("⚒️ 3. RRR & Pazar Vergisi")

rrr_choice = st.sidebar.radio(
    f"{locked_refine_city} Geri Dönüş Oranı (RRR):",
    (
        "🔥 Focus Yok (%36.7 RRR - Tüm Kademeler)",
        "⚡ Sadece Son Kademede Focus (Altlar %36.7, Hedef %53.9)",
        "💎 Tüm Kademelerde Focus (%53.9 RRR)"
    ),
    index=0
)

premium_tax = st.sidebar.slider("Pazar Satış Vergisi (% - Premium: 4.0):", 0.0, 8.0, 4.0, 0.5)
setup_fee = st.sidebar.slider("Emir Kurulum Ücreti (% - Standart: 2.5):", 0.0, 5.0, 2.5, 0.5)
max_data_age = st.sidebar.slider("Maks. Veri Yaşı (Dakika):", 10, 1440, 360, 10)

if st.sidebar.button("🔄 Fiyatları Şimdi Yenile", use_container_width=True):
    st.cache_data.clear()

# --- YARDIMCI FONKSİYONLAR ---
def make_item_id(tier_num, base_type, enc_str):
    # Albion kuralı: T2 ve T3 her zaman düz (.0) olur!
    if enc_str == ".0" or tier_num in [2, 3]:
        return f"T{tier_num}_{base_type}"
    lvl = enc_str.replace(".", "")
    return f"T{tier_num}_{base_type}_LEVEL{lvl}@{lvl}"

def normalize_id(item_id):
    if "_LEVEL" in item_id and "@" not in item_id:
        lvl = item_id.split("_LEVEL")[1][0]
        return f"{item_id}@{lvl}"
    return item_id

def get_item_icon(item_id):
    return f"https://render.albiononline.com/v1/item/{item_id}.png"

def calc_age(date_str):
    if not date_str or date_str.startswith("0001"): return 999999
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - dt).total_seconds() / 60)
    except:
        return 999999

# --- TÜM TIER VE ENCHANT ID'LERİNİ ASENKRON ÇEK ---
BASE_URL = "https://www.albion-online-data.com/api/v2/stats/Prices"

all_possible_ids = set()
for t in range(2, 9):
    for e in [".0", ".1", ".2", ".3", ".4"]:
        if t in [2, 3] and e != ".0": continue
        if res_meta["raw"] == "STONE" and e != ".0": continue
        r_id = make_item_id(t, res_meta["raw"], e)
        f_id = make_item_id(t, res_meta["refined"], e)
        all_possible_ids.update([r_id, f_id, r_id.split("@")[0], f_id.split("@")[0]])

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200: return await response.json()
    except: pass
    return []

async def fetch_all_prices(items, locs):
    chunk_size = 70
    urls = [f"{BASE_URL}/{','.join(items[i:i + chunk_size])}?locations={locs}" for i in range(0, len(items), chunk_size)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

def get_data_sync(items, locs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_all_prices(items, locs))
    loop.close()
    return data

with st.spinner("⚡ Albion Pazar Verileri Çekiliyor..."):
    raw_api_data = get_data_sync(list(all_possible_ids), ",".join(active_cities))

if not raw_api_data:
    st.error("API'den veri alınamadı. Lütfen tekrar deneyin.")
    st.stop()

df = pd.DataFrame(raw_api_data)
df['sell_age'] = df['sell_price_min_date'].apply(calc_age)
df['buy_age'] = df['buy_price_max_date'].apply(calc_age)
df['norm_id'] = df['item_id'].apply(normalize_id)
df = df[df['city'].isin(active_cities)]

def get_price_info(norm_item_id, city_mode, is_buying=True):
    sub = df[(df['norm_id'] == norm_item_id) & (df['sell_price_min'] > 0) & (df['sell_age'] <= max_data_age)]
    if sub.empty:
        return 0, 0, "Veri Yok", 999999
    if city_mode not in [auto_cheapest, auto_expensive]:
        sub = sub[sub['city'] == city_mode]
        if sub.empty:
            return 0, 0, f"{city_mode} (Veri Yok)", 999999

    best_row = sub.loc[sub['sell_price_min'].idxmin()] if is_buying else sub.loc[sub['sell_price_min'].idxmax()]
    so_p = int(best_row['sell_price_min'])
    bo_p = int(best_row['buy_price_max']) if best_row['buy_age'] <= (max_data_age * 2) else 0
    return so_p, bo_p, best_row['city'], int(best_row['sell_age'])

# --- ZİNCİRLEME (T2 ➔ HEDEF TIER) HESAPLAMA FONKSİYONU ---
def calculate_cascade_chain(final_tier, final_enc, final_qty):
    """
    Hedeflenen (Örn: 5000 adet T5) ürünü hiç işlenmiş malzeme satın almadan,
    T2'den başlayarak üretmek için her Tier'dan kaç adet ham madde gerektiğini geriye doğru hesaplar.
    """
    required_refined_by_tier = {}
    required_refined_by_tier[final_tier] = final_qty

    # Hedef Tier'dan T2'ye doğru geriye sararak ara kademelerde kaç işlenmiş ürün gerektiğini bul
    for t in range(final_tier, 2, -1):
        if "Tüm Kademelerde Focus" in rrr_choice:
            rrr_t = 0.539
        elif "Sadece Son Kademede Focus" in rrr_choice and t == final_tier:
            rrr_t = 0.539
        else:
            rrr_t = 0.367
            
        # t seviyesinde Q adet üretmek için (t-1) seviyesinden Q * (1 - RRR) adet işlenmiş ürün gerekir
        required_refined_by_tier[t - 1] = math.ceil(required_refined_by_tier[t] * (1.0 - rrr_t))

    # Şimdi T2'den Hedef Tier'a kadar sırayla gereken Ham Madde miktarlarını ve maliyetleri çıkar
    chain_steps = []
    total_raw_cost = 0

    for t in range(2, final_tier + 1):
        if "Tüm Kademelerde Focus" in rrr_choice:
            rrr_t = 0.539
        elif "Sadece Son Kademede Focus" in rrr_choice and t == final_tier:
            rrr_t = 0.539
        else:
            rrr_t = 0.367

        # Albion Kuralı: T2 ve T3 her zaman .0 (Düz) olur, T4 ve üstü hedef enchant'ta olur!
        step_enc = ".0" if t in [2, 3] else final_enc
        raw_id = make_item_id(t, res_meta["raw"], step_enc)
        ref_id = make_item_id(t, res_meta["refined"], step_enc)

        needed_refined_out = required_refined_by_tier[t]
        raw_per_unit = RAW_PER_CRAFT[t]
        
        # Bu kademede satın alınması gereken NET Ham Madde
        raw_needed_qty = math.ceil(needed_refined_out * raw_per_unit * (1.0 - rrr_t))

        so_price, bo_price, city_name, age_mins = get_price_info(raw_id, buy_city_mode, is_buying=True)

        if use_bo_for_raw and bo_price > 0:
            effective_unit_price = bo_price * (1.0 + (setup_fee / 100.0))
        else:
            effective_unit_price = so_price

        step_cost = int(raw_needed_qty * effective_unit_price)
        total_raw_cost += step_cost

        chain_steps.append({
            "Adım": f"{t - 1}. Adım (T{t})",
            "Tier_Num": t,
            "Ham İkon": get_item_icon(raw_id),
            "İşlenmiş İkon": get_item_icon(ref_id),
            "Alınacak Ham Madde": f"T{t}{step_enc} {res_meta['raw_name']}",
            "Gereken Ham Adet": raw_needed_qty,
            "Alış Şehri": city_name,
            "Direkt Al (SO)": so_price,
            "Alış Emri (BO)": bo_price,
            "Kademe Maliyeti": step_cost,
            "Çıkan Ara Ürün": f"{needed_refined_out:,} adet T{t}{step_enc} {res_meta['ref_name']}" + (" 🎯 (HEDEF)" if t == final_tier else " (Üst Tier İçin)"),
            "Çıkan Adet": needed_refined_out,
            "RRR %": round(rrr_t * 100, 1),
            "Yaş (Dk)": age_mins
        })

    # Son Ürünün Satış Hesabı
    final_ref_id = make_item_id(final_tier, res_meta["refined"], final_enc)
    sell_so, sell_bo, sell_city, sell_age = get_price_info(final_ref_id, sell_city_mode, is_buying=False)

    # 1. Sell Order ile Satış (Beklemeli: Vergi + Kurulum Ücreti)
    so_cut = (premium_tax + setup_fee) / 100.0
    gross_so = sell_so * final_qty
    net_rev_so = int(gross_so * (1.0 - so_cut))
    net_profit_so = net_rev_so - total_raw_cost
    roi_so = (net_profit_so / total_raw_cost) * 100 if total_raw_cost > 0 else 0

    # 2. Buy Order'a Direkt Çakma (Sıcak Para: Sadece Vergi, Kurulum Ücreti Yok!)
    bo_cut = premium_tax / 100.0
    if sell_bo > 0:
        gross_bo = sell_bo * final_qty
        net_rev_bo = int(gross_bo * (1.0 - bo_cut))
        net_profit_bo = net_rev_bo - total_raw_cost
        roi_bo = (net_profit_bo / total_raw_cost) * 100 if total_raw_cost > 0 else 0
    else:
        net_rev_bo, net_profit_bo, roi_bo = 0, 0, 0

    return {
        "steps": chain_steps,
        "total_cost": total_raw_cost,
        "final_ref_id": final_ref_id,
        "sell_city": sell_city,
        "sell_so": sell_so,
        "sell_bo": sell_bo,
        "net_rev_so": net_rev_so,
        "net_profit_so": net_profit_so,
        "roi_so": round(roi_so, 1),
        "net_rev_bo": net_rev_bo,
        "net_profit_bo": net_profit_bo,
        "roi_bo": round(roi_bo, 1),
        "diff_so_bo": net_profit_so - net_profit_bo if sell_bo > 0 else 0,
        "sell_age": sell_age
    }

# --- ANA HESAPLAMAYI ÇALIŞTIR ---
result = calculate_cascade_chain(target_tier, target_enc, target_qty)
steps_df = pd.DataFrame(result["steps"])

# --- EKRAN DÜZENİ ---
tab1, tab2 = st.tabs([
    f"🛒 {target_qty:,} Adet T{target_tier}{target_enc} İçin Zincirleme Ham Madde Listesi (T2 ➔ T{target_tier})",
    "📊 Hangi Tier Daha Kârlı? (T3 ➔ T8 Zincirleme Kıyaslama)"
])

with tab1:
    left_col, right_col = st.columns([6.2, 4.8])

    with left_col:
        st.markdown(f"### 📦 1. Satın Alınacak Ham Maddeler (T2'den T{target_tier}'e Sırayla)")
        st.caption(f"**{target_qty:,} adet T{target_tier}{target_enc} {res_meta['ref_name']}** üretmek için pazardan hiç işlenmiş ürün almadan toplaman gereken tam ham madde listesi:")

        # Görsel Adım Kartları (T2, T3, T4, T5...)
        for s in result["steps"]:
            st.markdown(f"""
            <div class="step-card">
                <div style="display:flex; align-items:center; gap:14px;">
                    <img src="{s['Ham İkon']}" width="52">
                    <div>
                        <span style="color:#FFD700; font-weight:800; font-size:16px;">{s['Gereken Ham Adet']:,} Adet {s['Alınacak Ham Madde']} Al</span><br>
                        <span style="color:#94A3B8; font-size:13px;">📍 Şehir: <b style="color:#E2E8F0;">{s['Alış Şehri']}</b> | Direkt (SO): <b>{s['Direkt Al (SO)']:,} 🥈</b> | Emir (BO): <b>{s['Alış Emri (BO)']:,} 🥈</b></span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="color:#38BDF8; font-weight:700; font-size:14px;">➔ {s['Çıkan Ara Ürün']}</span><br>
                    <span style="color:#CBD5E1; font-size:13px;">Bu Kademe Tutar: <b style="color:#FBBF24;">{s['Kademe Maliyeti']:,} 🥈</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📋 Toplu Alışveriş Tablosu")
        st.dataframe(
            steps_df[[
                "Ham İkon", "Alınacak Ham Madde", "Gereken Ham Adet", 
                "Alış Şehri", "Direkt Al (SO)", "Alış Emri (BO)", 
                "Kademe Maliyeti", "Çıkan Ara Ürün"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ham İkon": st.column_config.ImageColumn("", width="small"),
                "Gereken Ham Adet": st.column_config.NumberColumn("Alınacak Adet", format="%d"),
                "Direkt Al (SO)": st.column_config.NumberColumn("Direkt Fiyat (SO)", format="%d 🥈"),
                "Alış Emri (BO)": st.column_config.NumberColumn("Emir Fiyatı (BO)", format="%d 🥈"),
                "Kademe Maliyeti": st.column_config.NumberColumn("Toplam Tutar", format="%d 🥈"),
            }
        )

    with right_col:
        st.markdown("### 💰 2. Toplam Maliyet & Satış Kârı (SO vs BO)")

        so_color = "#10B981" if result["net_profit_so"] > 0 else "#EF4444"
        bo_color = "#38BDF8" if result["net_profit_bo"] > 0 else "#EF4444"

        # Hızlı Nakit (Buy Order) Tavsiyesi
        fast_cash_msg = ""
        if result["sell_bo"] > 0 and result["net_profit_bo"] > 0:
            ratio = (result["net_profit_bo"] / result["net_profit_so"]) * 100 if result["net_profit_so"] > 0 else 100
            if ratio >= 85 or result["net_profit_bo"] >= result["net_profit_so"]:
                fast_cash_msg = f"""
                <div class="fast-cash-alert">
                    ⚡ <b>SICAK PARA FIRSATI:</b> Bekleyerek {result['net_profit_so']:,} 🥈 kazanacağına, 
                    ürünleri direkt Buy Order'a çakıp saniyesinde <b>{result['net_profit_bo']:,} 🥈</b> sıcak parayı cebine koyabilirsin! 
                    (Aradaki fark sadece {result['diff_so_bo']:,} 🥈)
                </div>
                """

        # KART 1: GENEL MALİYET VE HEDEF ÖZETİ
        st.markdown(f"""
        <div class="profit-card-gold">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <img src="{get_item_icon(result['final_ref_id'])}" width="68">
                    <div>
                        <span style="color:#FFD700; font-family:'Cinzel',serif; font-weight:800; font-size:18px;">
                            {target_qty:,}x T{target_tier}{target_enc} {res_meta['ref_name']}
                        </span><br>
                        <span style="color:#94A3B8; font-size:13px;">
                            🔒 Refine Şehri: <b style="color:#38BDF8;">{locked_refine_city}</b> | 
                            📍 Satış Şehri: <b style="color:#10B981;">{result['sell_city']}</b>
                        </span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="color:#94A3B8; font-size:12px;">TOPLAM HAM MADDE MALİYETİ (T2➔T{target_tier})</span><br>
                    <span style="color:#FBBF24; font-size:24px; font-weight:800;">{result['total_cost']:,} 🥈</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KART 2: SELL ORDER (BEKLEMELİ) VS BUY ORDER (HEMEN SAT)
        st.markdown(f"""
        <div class="profit-card-blue">
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <div style="border-right:1px solid #334155; padding-right:12px;">
                    <span style="color:#FFD700; font-weight:800; font-size:15px;">⏳ 1. SATIŞ EMRİ KUR (SELL ORDER)</span><br>
                    <span style="color:#94A3B8; font-size:12.5px;">Birim Satış: <b>{result['sell_so']:,} 🥈</b> (-%{premium_tax+setup_fee} kesinti)</span><br>
                    <span style="color:#CBD5E1; font-size:13px;">Net Ele Geçen: <b>{result['net_rev_so']:,} 🥈</b></span><br><br>
                    <span style="color:#94A3B8; font-size:12px;">BEKLEMELİ NET KÂR:</span><br>
                    <span style="color:{so_color}; font-size:24px; font-weight:800;">{result['net_profit_so']:,} 🥈</span>
                    <span style="color:{so_color}; font-weight:bold;"> (%{result['roi_so']})</span>
                </div>
                <div style="padding-left:5px;">
                    <span style="color:#38BDF8; font-weight:800; font-size:15px;">⚡ 2. DİREKT SAT (BUY ORDER'A ÇAK)</span><br>
                    <span style="color:#94A3B8; font-size:12.5px;">Birim Alış Emri: <b>{result['sell_bo']:,} 🥈</b> (Sadece -%{premium_tax} vergi)</span><br>
                    <span style="color:#CBD5E1; font-size:13px;">Anında Ele Geçen: <b>{result['net_rev_bo']:,} 🥈</b></span><br><br>
                    <span style="color:#94A3B8; font-size:12px;">ANINDA SICAK PARA KÂRI:</span><br>
                    <span style="color:{bo_color}; font-size:24px; font-weight:800;">{result['net_profit_bo']:,} 🥈</span>
                    <span style="color:{bo_color}; font-weight:bold;"> (%{result['roi_bo']})</span>
                </div>
            </div>
            {fast_cash_msg}
        </div>
        """, unsafe_allow_html=True)

        # Kademe Maliyet Dağılım Grafiği
        st.markdown("#### 📊 Hangi Tier Ham Maddeye Ne Kadar Para Gidiyor?")
        fig = go.Figure(go.Bar(
            x=steps_df["Alınacak Ham Madde"],
            y=steps_df["Kademe Maliyeti"],
            text=[f"{q:,} Adet<br>({c:,} 🥈)" for q, c in zip(steps_df["Gereken Ham Adet"], steps_df["Kademe Maliyeti"])],
            textposition="auto",
            marker_color="#D4AF37"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(18, 24, 31, 0.7)",
            plot_bgcolor="rgba(18, 24, 31, 0.4)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=230,
            yaxis_title="Maliyet (Gümüş)"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown(f"### 🏆 {target_qty:,} Adet Üretim İçin Tüm Seviyelerin (T3 ➔ T8) Zincirleme Kâr Kıyaslaması")
    st.caption("Her satır, o seviyedeki ürünü T2'den başlayarak sıfırdan ürettiğinde cebinden çıkacak toplam ham madde maliyetini ve bırakacağı net kârı gösterir.")
    
    comp_rows = []
    for t_num in [3, 4, 5, 6, 7, 8]:
        for e_str in [".0", ".1", ".2", ".3"]:
            if t_num == 3 and e_str != ".0": continue
            if res_meta["raw"] == "STONE" and e_str != ".0": continue
            res_c = calculate_cascade_chain(t_num, e_str, target_qty)
            if res_c["sell_so"] > 0 and res_c["total_cost"] > 0:
                comp_rows.append({
                    "İkon": get_item_icon(res_c["final_ref_id"]),
                    "Hedef Ürün": f"T{t_num}{e_str} {res_meta['ref_name']}",
                    "Satış Şehri": res_c["sell_city"],
                    "T2➔T" + str(t_num) + " Toplam Maliyet": res_c["total_cost"],
                    "Satış Emri (SO) Birim": res_c["sell_so"],
                    "Hemen Sat (BO) Birim": res_c["sell_bo"],
                    "⏳ Beklemeli Net Kâr (SO)": res_c["net_profit_so"],
                    "⚡ Sıcak Para Net Kâr (BO)": res_c["net_profit_bo"],
                    "ROI (SO) %": res_c["roi_so"]
                })
                
    if comp_rows:
        comp_df = pd.DataFrame(comp_rows).sort_values(by="⏳ Beklemeli Net Kâr (SO)", ascending=False)
        st.dataframe(
            comp_df,
            use_container_width=True,
            hide_index=True,
            height=550,
            column_config={
                "İkon": st.column_config.ImageColumn("", width="small"),
                "T2➔T" + str(t_num) + " Toplam Maliyet": st.column_config.NumberColumn("Toplam Maliyet (T2'den)", format="%d 🥈"),
                "Satış Emri (SO) Birim": st.column_config.NumberColumn("Birim SO 🥈", format="%d"),
                "Hemen Sat (BO) Birim": st.column_config.NumberColumn("Birim BO 🥈", format="%d"),
                "⏳ Beklemeli Net Kâr (SO)": st.column_config.NumberColumn("⏳ Beklemeli Kâr", format="%d 🥈"),
                "⚡ Sıcak Para Net Kâr (BO)": st.column_config.NumberColumn("⚡ Sıcak Para Kârı", format="%d 🥈"),
                "ROI (SO) %": st.column_config.NumberColumn("ROI %", format="%.1f%%")
            }
        )
