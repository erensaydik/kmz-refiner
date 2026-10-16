import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone
import plotly.graph_objects as go
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enlil God Tier Refine", layout="wide", initial_sidebar_state="expanded")

# --- ANİMASYONLU OYUN ARAYÜZÜ (CSS) ---
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
        box-shadow: 5px 0 15px rgba(0,0,0,0.6);
    }

    @keyframes goldShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    .animated-header {
        font-family: 'Cinzel', serif;
        text-align: center;
        padding: 16px;
        margin-bottom: 18px;
        background: linear-gradient(180deg, #1E2631 0%, #11161D 100%);
        border: 2px solid #8A6D3B;
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(185, 147, 90, 0.25), inset 0 0 15px rgba(0,0,0,0.8);
    }

    .animated-header h1 {
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #B9935A 0%, #FFF3D1 50%, #B9935A 100%);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        animation: goldShimmer 5s linear infinite;
        letter-spacing: 2px;
    }

    .animated-header p {
        color: #94A3B8;
        margin: 5px 0 0 0;
        font-size: 13px;
        letter-spacing: 1px;
    }

    @keyframes pulseGold {
        0% { box-shadow: 0 0 8px rgba(212, 175, 55, 0.3), inset 0 0 8px rgba(212, 175, 55, 0.15); border-color: #8A6D3B; }
        50% { box-shadow: 0 0 22px rgba(255, 215, 0, 0.75), inset 0 0 15px rgba(255, 215, 0, 0.3); border-color: #FFD700; }
        100% { box-shadow: 0 0 8px rgba(212, 175, 55, 0.3), inset 0 0 8px rgba(212, 175, 55, 0.15); border-color: #8A6D3B; }
    }

    @keyframes pulseBlue {
        0% { box-shadow: 0 0 8px rgba(56, 189, 248, 0.3), inset 0 0 8px rgba(56, 189, 248, 0.15); border-color: #0284C7; }
        50% { box-shadow: 0 0 22px rgba(56, 189, 248, 0.8), inset 0 0 15px rgba(56, 189, 248, 0.35); border-color: #38BDF8; }
        100% { box-shadow: 0 0 8px rgba(56, 189, 248, 0.3), inset 0 0 8px rgba(56, 189, 248, 0.15); border-color: #0284C7; }
    }

    @keyframes floatIcon {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }

    .god-card-gold {
        background: linear-gradient(135deg, #231D14 0%, #12151A 100%);
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 18px;
        animation: pulseGold 3s infinite ease-in-out;
        margin-bottom: 14px;
    }

    .god-card-blue {
        background: linear-gradient(135deg, #10212B 0%, #12151A 100%);
        border: 2px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        animation: pulseBlue 3s infinite ease-in-out;
        margin-bottom: 14px;
    }

    .item-icon {
        width: 64px;
        height: 64px;
        animation: floatIcon 3.5s ease-in-out infinite;
        filter: drop-shadow(0 5px 8px rgba(0,0,0,0.7));
    }

    .locked-city-box {
        background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #38BDF8;
        border-left: 5px solid #38BDF8;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-size: 14px;
        color: #E2E8F0;
    }

    .stButton>button {
        background: linear-gradient(135deg, #5C4728 0%, #2C2011 100%) !important;
        color: #F3E5AB !important;
        border: 1px solid #B9935A !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DİL VE BAŞLIK ---
lang = st.sidebar.radio("🌐 Dil / Language", ("Türkçe", "English"), horizontal=True)
is_tr = (lang == "Türkçe")

st.markdown(f"""
<div class="animated-header">
    <h1>ENLİL - GOD TIER REFINE SCANNER</h1>
    <p>{"T2'den T8'e Kesintisiz Ham Madde Rafinasyon Radarı" if is_tr else "Seamless T2 to T8 Raw Material Refining Radar"}</p>
</div>
""", unsafe_allow_html=True)

RESOURCES = {
    "🌿 Elyaf (Fiber ➔ Cloth)": {"raw": "FIBER", "refined": "CLOTH", "bonus_city": "Lymhurst", "tr_raw": "Elyaf", "tr_ref": "Kumaş"},
    "⛏️ Cevher (Ore ➔ Metal Bar)": {"raw": "ORE", "refined": "METALBAR", "bonus_city": "Thetford", "tr_raw": "Cevher", "tr_ref": "Külçe"},
    "🐾 Deri (Hide ➔ Leather)": {"raw": "HIDE", "refined": "LEATHER", "bonus_city": "Martlock", "tr_raw": "Ham Deri", "tr_ref": "Deri"},
    "🌲 Odun (Wood ➔ Planks)": {"raw": "WOOD", "refined": "PLANKS", "bonus_city": "Fort Sterling", "tr_raw": "Tomruk", "tr_ref": "Kalas"},
    "🪨 Taş (Stone ➔ Stone Block)": {"raw": "STONE", "refined": "STONEBLOCK", "bonus_city": "Bridgewatch", "tr_raw": "Kaya", "tr_ref": "Taş Blok"}
}

RAW_QTY_BY_TIER = {"T2": 1, "T3": 2, "T4": 2, "T5": 3, "T6": 4, "T7": 5, "T8": 5}
ROYAL_CITIES = ["Lymhurst", "Bridgewatch", "Martlock", "Thetford", "Fort Sterling"]

# --- SOL MENÜ ---
st.sidebar.header("📦 Kaynak Seçimi" if is_tr else "Resource Selection")
selected_res_key = st.sidebar.selectbox("Kaynak Türü:", list(RESOURCES.keys()))
res_meta = RESOURCES[selected_res_key]
locked_refine_city = res_meta["bonus_city"]

st.sidebar.markdown(f"""
<div class="locked-city-box">
    🔒 <b>Rafinasyon Şehri:</b><br>
    <span style="color:#38BDF8; font-size:16px; font-weight:800;">{locked_refine_city} (+%40 Bonus)</span>
</div>
""", unsafe_allow_html=True)

include_caerleon = st.sidebar.checkbox("Caerleon'u Dahil Et", value=False)
active_cities = ROYAL_CITIES + (["Caerleon"] if include_caerleon else [])

auto_cheapest_label = "🌟 Otomatik (En Ucuz Şehir)"
auto_highest_label = "💰 Otomatik (En Pahalı Şehir)"

raw_buy_city_mode = st.sidebar.selectbox("Ham Madde Alış Şehri:", [auto_cheapest_label] + active_cities)
sell_city_mode = st.sidebar.selectbox("İşlenmiş Ürün Satış Şehri:", [auto_highest_label] + active_cities)

rrr_mode = st.sidebar.radio("Geri Dönüş Oranı (RRR):", ("🔥 Focus Yok (%36.7 RRR)", "⚡ Focus İle (%53.9 RRR)"))
rrr_value = 36.7 if "36.7" in rrr_mode else 53.9

premium_tax = st.sidebar.slider("Pazar Vergisi (%)", 0.0, 8.0, 4.0, 0.5)
setup_fee = st.sidebar.slider("Kurulum Ücreti (%)", 0.0, 5.0, 2.5, 0.5)
max_data_age = st.sidebar.slider("Maks. Veri Yaşı (Dakika)", 10, 1440, 300, 10)
batch_size = st.sidebar.number_input("Üretim Adedi", min_value=1, value=1000, step=500)

if st.sidebar.button("🔄 Verileri Yenile", use_container_width=True):
    st.cache_data.clear()

# --- T2'DEN T8'E TÜM SEVİYELERİ OTOMATİK DİZ ---
def make_item_id(tier, base_type, enc):
    if enc == ".0" or tier in ["T2", "T3"]:
        return f"{tier}_{base_type}"
    lvl = enc.replace(".", "")
    return f"{tier}_{base_type}_LEVEL{lvl}@{lvl}"

combos = []
all_tiers = ["T2", "T3", "T4", "T5", "T6", "T7", "T8"]
all_enchants = [".0", ".1", ".2", ".3", ".4"]

for tier in all_tiers:
    for enc in all_enchants:
        if tier in ["T2", "T3"] and enc != ".0":
            continue
        if res_meta["raw"] == "STONE" and enc != ".0":
            continue

        combos.append({
            "tier": tier,
            "enchant": enc,
            "label": f"{tier}{enc}",
            "raw_id": make_item_id(tier, res_meta["raw"], enc),
            "ref_id": make_item_id(tier, res_meta["refined"], enc)
        })

all_query_ids = list(set([c["raw_id"] for c in combos] + [c["ref_id"] for c in combos] + [c["raw_id"].split("@")[0] for c in combos] + [c["ref_id"].split("@")[0] for c in combos]))

# --- API VERİ ÇEKME ---
BASE_URL = "https://www.albion-online-data.com/api/v2/stats/Prices"

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200: return await response.json()
    except: pass
    return []

async def fetch_refining_data(items, locs):
    chunk_size = 70
    urls = [f"{BASE_URL}/{','.join(items[i:i + chunk_size])}?locations={locs}" for i in range(0, len(items), chunk_size)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

def get_data_sync(items, locs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_refining_data(items, locs))
    loop.close()
    return data

def calc_age(date_str):
    if not date_str or date_str.startswith("0001"): return 999999
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - dt).total_seconds() / 60)
    except: return 999999

def get_item_icon(item_id):
    return f"https://render.albiononline.com/v1/item/{item_id}.png"

def normalize_id(item_id):
    if "_LEVEL" in item_id and "@" not in item_id:
        lvl = item_id.split("_LEVEL")[1][0]
        return f"{item_id}@{lvl}"
    return item_id

with st.spinner("⚡ T2'den T8'e Pazar Verileri Taranıyor..."):
    raw_api_data = get_data_sync(all_query_ids, ",".join(active_cities))

if not raw_api_data:
    st.error("API'den veri alınamadı.")
    st.stop()

df = pd.DataFrame(raw_api_data)
df['sell_age'] = df['sell_price_min_date'].apply(calc_age)
df['buy_age'] = df['buy_price_max_date'].apply(calc_age)
df['norm_id'] = df['item_id'].apply(normalize_id)
df = df[df['city'].isin(active_cities)]

def get_market_orders(norm_item_id, city_mode, is_buying_raw=True):
    sub = df[(df['norm_id'] == norm_item_id) & (df['sell_price_min'] > 0) & (df['sell_age'] <= max_data_age)]
    if sub.empty: return 0, 0, "-", 999999
    if city_mode not in [auto_cheapest_label, auto_highest_label]:
        sub = sub[sub['city'] == city_mode]
        if sub.empty: return 0, 0, city_mode, 999999

    best_row = sub.loc[sub['sell_price_min'].idxmin()] if is_buying_raw else sub.loc[sub['sell_price_min'].idxmax()]
    so_price = int(best_row['sell_price_min'])
    bo_price = int(best_row['buy_price_max']) if best_row['buy_age'] <= (max_data_age * 2) else 0
    return so_price, bo_price, best_row['city'], int(best_row['sell_age'])

# --- HESAPLAMA ---
calculated_data = []
rrr_factor = 1 - (rrr_value / 100.0)

for c in combos:
    tier = c["tier"]
    raw_qty = RAW_QTY_BY_TIER[tier]
    
    raw_so, raw_bo, raw_city, raw_age = get_market_orders(c["raw_id"], raw_buy_city_mode, is_buying_raw=True)
    ref_so, ref_bo, sell_city, ref_age = get_market_orders(c["ref_id"], sell_city_mode, is_buying_raw=False)
    
    if raw_so == 0 or ref_so == 0:
        continue
        
    eff_raw_qty = raw_qty * rrr_factor
    cost_per_item = eff_raw_qty * raw_so
    total_batch_cost = int(cost_per_item * batch_size)
    
    so_cut = (premium_tax + setup_fee) / 100.0
    net_rev_so = ref_so * (1 - so_cut)
    unit_profit_so = net_rev_so - cost_per_item
    total_profit_so = int(unit_profit_so * batch_size)
    roi_so = (unit_profit_so / cost_per_item) * 100 if cost_per_item > 0 else 0
    
    if ref_bo > 0:
        bo_cut = premium_tax / 100.0
        net_rev_bo = ref_bo * (1 - bo_cut)
        unit_profit_bo = net_rev_bo - cost_per_item
        total_profit_bo = int(unit_profit_bo * batch_size)
        roi_bo = (unit_profit_bo / cost_per_item) * 100 if cost_per_item > 0 else 0
    else:
        unit_profit_bo, total_profit_bo, roi_bo = 0, 0, 0

    calculated_data.append({
        "Seviye": c["label"],
        "İkon": get_item_icon(c["ref_id"]),
        "Ham İkon": get_item_icon(c["raw_id"]),
        "Eşya": f"{c['label']} {res_meta['tr_ref']}",
        "Ham Madde": f"{c['label']} {res_meta['tr_raw']}",
        "Alış Şehri": raw_city,
        "Ham Fiyat (SO)": raw_so,
        "Satış Şehri": sell_city,
        "Satış Emri (SO)": ref_so,
        "Hemen Sat (BO)": ref_bo,
        "Toplam Maliyet": total_batch_cost,
        "SO Toplam Kâr": total_profit_so,
        "BO Sıcak Para Kârı": total_profit_bo,
        "ROI (SO) %": round(roi_so, 1),
        "Gereken Ham": int(round(eff_raw_qty * batch_size)),
        "Yaş (Dk)": max(raw_age, ref_age)
    })

if not calculated_data:
    st.warning("⚠️ Güncel veri bulunamadı. Veri yaşını artırmayı deneyin.")
    st.stop()

calc_df = pd.DataFrame(calculated_data)

# --- ARAYÜZ ---
left_col, right_col = st.columns([6, 5])

with left_col:
    st.markdown(f"### 📋 T2'den T8'e Kesintisiz Rafinasyon Tablosu ({batch_size:,} Adet)")
    st.dataframe(
        calc_df[[
            "İkon", "Seviye", "Alış Şehri", "Ham Fiyat (SO)", 
            "Satış Şehri", "Satış Emri (SO)", "SO Toplam Kâr", "ROI (SO) %"
        ]],
        use_container_width=True,
        hide_index=True,
        height=580,
        column_config={
            "İkon": st.column_config.ImageColumn("", width="small"),
            "Seviye": st.column_config.TextColumn("Tier"),
            "Alış Şehri": st.column_config.TextColumn("Ham Alış"),
            "Ham Fiyat (SO)": st.column_config.NumberColumn("Ham 🥈", format="%d"),
            "Satış Şehri": st.column_config.TextColumn("Satış"),
            "Satış Emri (SO)": st.column_config.NumberColumn("Satış 🥈", format="%d"),
            "SO Toplam Kâr": st.column_config.NumberColumn("Net Kâr 🥈", format="%d"),
            "ROI (SO) %": st.column_config.NumberColumn("ROI %", format="%.1f%%")
        }
    )

with right_col:
    tier_options = list(calc_df["Seviye"].unique())
    picked_card_tier = st.selectbox("🎯 Detayını İncelemek İstediğin Seviye:", tier_options)

    top1 = calc_df[calc_df["Seviye"] == picked_card_tier].iloc[0]
    so_color = "#10B981" if top1["SO Toplam Kâr"] > 0 else "#EF4444"
    bo_color = "#38BDF8" if top1["BO Sıcak Para Kârı"] > 0 else "#EF4444"

    st.markdown(f"""
    <div class="god-card-gold">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <img src="{top1['Ham İkon']}" class="item-icon">
                <span style="font-size:22px; color:#D4AF37; font-weight:bold;">➔</span>
                <img src="{top1['İkon']}" class="item-icon">
            </div>
            <div style="text-align:right; border-left:1px solid #4A3B23; padding-left:14px;">
                <span style="color:#FFD700; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">⏳ SELL ORDER KÂRI</span><br>
                <span style="color:{so_color}; font-size:22px; font-weight:800;">{top1['SO Toplam Kâr']:,} 🥈</span>
                <span style="color:{so_color}; font-size:13px; font-weight:bold;"> (%{top1['ROI (SO) %']})</span>
            </div>
            <div style="text-align:right; border-left:1px solid #0284C7; padding-left:14px;">
                <span style="color:#38BDF8; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">⚡ SICAK PARA (BO)</span><br>
                <span style="color:{bo_color}; font-size:22px; font-weight:800;">{top1['BO Sıcak Para Kârı']:,} 🥈</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="god-card-blue">
        <div>
            <span style="color:#38BDF8; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">🛒 {batch_size:,} ADET {top1['Seviye']} İÇİN ROTA ÖZETİ</span>
            <ul style="margin:10px 0 0 0; padding-left:18px; color:#E2E8F0; font-size:13.5px; line-height:1.75;">
                <li><b>Ham Madde:</b> <span style="color:#FFD700;">{top1['Alış Şehri']}</span> pazarından <b>{top1['Gereken Ham']:,} adet</b> al.</li>
                <li><b>Rafine Et:</b> <span style="color:#38BDF8;">{locked_refine_city}</span> şehrinde (%{rrr_value} RRR) bas.</li>
                <li><b>Toplam Sermaye:</b> {top1['Toplam Maliyet']:,} 🥈</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
