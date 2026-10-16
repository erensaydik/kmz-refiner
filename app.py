import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone
import plotly.graph_objects as go
import plotly.express as px

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enlil God Tier Refine", layout="wide", initial_sidebar_state="expanded")

# --- ANİMASYONLU OYUN ARAYÜZÜ (CSS KEYFRAMES) ---
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
        transition: transform 0.3s ease;
        margin-bottom: 14px;
    }

    .god-card-blue {
        background: linear-gradient(135deg, #10212B 0%, #12151A 100%);
        border: 2px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        animation: pulseBlue 3s infinite ease-in-out;
        transition: transform 0.3s ease;
        margin-bottom: 14px;
    }

    .god-card-gold:hover, .god-card-blue:hover {
        transform: translateY(-3px) scale(1.01);
    }

    .item-icon {
        width: 68px;
        height: 68px;
        animation: floatIcon 3.5s ease-in-out infinite;
        filter: drop-shadow(0 5px 8px rgba(0,0,0,0.7));
        transition: transform 0.2s ease;
    }

    .item-icon:hover {
        transform: scale(1.18) rotate(3deg);
        filter: drop-shadow(0 0 12px rgba(255, 215, 0, 0.8));
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
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8A6D3B 0%, #4A361D 100%) !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
        transform: scale(1.02);
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DİL VE BAŞLIK ---
lang = st.sidebar.radio("🌐 Dil / Language", ("Türkçe", "English"), horizontal=True)
is_tr = (lang == "Türkçe")

st.markdown(f"""
<div class="animated-header">
    <h1>ENLİL - GOD TIER REFINE SCANNER</h1>
    <p>{"Albion Online Ham Madde Rafinasyon & Kâr Radarı" if is_tr else "Albion Online Raw Material Refining & Profit Radar"}</p>
</div>
""", unsafe_allow_html=True)

# --- KAYNAK SÖZLÜĞÜ VE KİLİTLİ BONUS ŞEHİRLERİ ---
RESOURCES = {
    "🌿 Elyaf (Fiber ➔ Cloth)": {
        "raw": "FIBER", "refined": "CLOTH", "bonus_city": "Lymhurst",
        "tr_raw": "Elyaf", "tr_ref": "Kumaş", "en_raw": "Fiber", "en_ref": "Cloth"
    },
    "⛏️ Cevher (Ore ➔ Metal Bar)": {
        "raw": "ORE", "refined": "METALBAR", "bonus_city": "Thetford",
        "tr_raw": "Cevher", "tr_ref": "Külçe", "en_raw": "Ore", "en_ref": "Metal Bar"
    },
    "🐾 Deri (Hide ➔ Leather)": {
        "raw": "HIDE", "refined": "LEATHER", "bonus_city": "Martlock",
        "tr_raw": "Ham Deri", "tr_ref": "Deri", "en_raw": "Hide", "en_ref": "Leather"
    },
    "🌲 Odun (Wood ➔ Planks)": {
        "raw": "WOOD", "refined": "PLANKS", "bonus_city": "Fort Sterling",
        "tr_raw": "Tomruk", "tr_ref": "Kalas", "en_raw": "Wood", "en_ref": "Planks"
    },
    "🪨 Taş (Stone ➔ Stone Block)": {
        "raw": "STONE", "refined": "STONEBLOCK", "bonus_city": "Bridgewatch",
        "tr_raw": "Kaya", "tr_ref": "Taş Blok", "en_raw": "Stone", "en_ref": "Stone Block"
    }
}

# Her seviye için gereken saf ham madde miktarı
RAW_QTY_BY_TIER = {
    "T2": 1,
    "T3": 2,
    "T4": 2,
    "T5": 3,
    "T6": 4,
    "T7": 5,
    "T8": 5,
}

ROYAL_CITIES = ["Lymhurst", "Bridgewatch", "Martlock", "Thetford", "Fort Sterling"]

# --- SOL PANEL: 1. KAYNAK VE SEVİYE SEÇİMİ ---
st.sidebar.header("📦 1. Kaynak & Seviye Seçimi" if is_tr else "📦 1. Resource & Tier Filter")
selected_res_key = st.sidebar.selectbox("Üretilecek Kaynak:" if is_tr else "Resource Type:", list(RESOURCES.keys()))
res_meta = RESOURCES[selected_res_key]
locked_refine_city = res_meta["bonus_city"]

# Kilitli Refine Şehri Gösterimi (Değiştirilemez)
st.sidebar.markdown(f"""
<div class="locked-city-box">
    🔒 <b>{"Rafinasyon Şehri (Sabit)" if is_tr else "Refining City (Locked)"}:</b><br>
    <span style="color:#38BDF8; font-size:16px; font-weight:800;">{locked_refine_city} (+%40 Bonus)</span>
</div>
""", unsafe_allow_html=True)

selected_tiers = st.sidebar.multiselect(
    "Seviyeler (Tier):" if is_tr else "Select Tiers:",
    options=["T2", "T3", "T4", "T5", "T6", "T7", "T8"],
    default=["T4", "T5", "T6", "T7", "T8"]
)

selected_enchants = st.sidebar.multiselect(
    "Büyü Seviyesi (Enchant):" if is_tr else "Select Enchants:",
    options=[".0", ".1", ".2", ".3", ".4"],
    default=[".0", ".1", ".2", ".3"]
)

# --- SOL PANEL: 2. ALIŞ VE SATIŞ ŞEHİRLERİ (SADECE HAM MADDE VE SATIŞ) ---
st.sidebar.markdown("---")
st.sidebar.header("🗺️ 2. Alış & Satış Şehirleri" if is_tr else "🗺️ 2. Buy & Sell Cities")

include_caerleon = st.sidebar.checkbox("Caerleon'u Dahil Et" if is_tr else "Include Caerleon", value=False)
active_cities = ROYAL_CITIES + (["Caerleon"] if include_caerleon else [])

auto_cheapest_label = "🌟 Otomatik (En Ucuz Şehir)" if is_tr else "🌟 Auto (Cheapest City)"
auto_highest_label = "💰 Otomatik (En Pahalı Şehir)" if is_tr else "💰 Auto (Highest Price City)"

raw_buy_city_mode = st.sidebar.selectbox(
    "Ham Madde Alış Şehri:" if is_tr else "Raw Material Buy City:",
    options=[auto_cheapest_label] + active_cities,
    index=0
)

sell_city_mode = st.sidebar.selectbox(
    "İşlenmiş Ürün Satış Şehri:" if is_tr else "Refined Product Sell City:",
    options=[auto_highest_label] + active_cities,
    index=0
)

# --- SOL PANEL: 3. BONUS ŞEHİR RRR VE VERGİ ---
st.sidebar.markdown("---")
st.sidebar.header("⚒️ 3. Bonus RRR & Vergi" if is_tr else "⚒️ 3. Bonus RRR & Tax")

rrr_mode = st.sidebar.radio(
    f"{locked_refine_city} Geri Dönüş Oranı (RRR):" if is_tr else f"{locked_refine_city} RRR Mode:",
    (
        "🔥 Focus Yok (%36.7 RRR)",
        "⚡ Focus İle (%53.9 RRR)"
    ),
    index=0
)
rrr_value = 36.7 if "36.7" in rrr_mode else 53.9

market_tax = st.sidebar.slider("Pazar Satış Vergisi (%)" if is_tr else "Market Tax (%)", 0.0, 10.0, 4.0, 0.1)
max_data_age = st.sidebar.slider("Maks. Veri Yaşı (Dakika)" if is_tr else "Max Data Age (Mins)", 10, 1440, 300, 10)
batch_size = st.sidebar.number_input("Üretim Adedi (Simülasyon)" if is_tr else "Batch Size", min_value=1, value=300, step=50)

if st.sidebar.button("🔄 Verileri Şimdi Yenile" if is_tr else "🔄 Refresh Market Data", use_container_width=True):
    st.cache_data.clear()

if not selected_tiers or not selected_enchants:
    st.warning("👈 Lütfen sol menüden en az bir Seviye (Tier) ve Büyü (Enchant) seçin.")
    st.stop()

# --- DOĞRU ALBION ID ÜRETİCİ (SADECE HAM MADDE VE İŞLENMİŞ ÜRÜN) ---
def make_item_id(tier, base_type, enc):
    if enc == ".0" or tier in ["T2", "T3"]:
        return f"{tier}_{base_type}"
    lvl = enc.replace(".", "")
    return f"{tier}_{base_type}_LEVEL{lvl}@{lvl}"

combos = []
for tier in selected_tiers:
    for enc in selected_enchants:
        # T2, T3 ve Taş (Stone) için sadece .0 (Düz) bulunur
        if tier in ["T2", "T3"] and enc != ".0":
            continue
        if res_meta["raw"] == "STONE" and enc != ".0":
            continue

        raw_id = make_item_id(tier, res_meta["raw"], enc)
        ref_id = make_item_id(tier, res_meta["refined"], enc)

        combos.append({
            "tier": tier,
            "enchant": enc,
            "label": f"{tier}{enc}",
            "raw_id": raw_id,
            "ref_id": ref_id
        })

all_query_ids = set()
for c in combos:
    all_query_ids.update([c["raw_id"], c["ref_id"]])
    all_query_ids.update([c["raw_id"].split("@")[0], c["ref_id"].split("@")[0]])

all_item_ids = list(all_query_ids)

# --- ASENKRON VERİ ÇEKME MOTORU ---
BASE_URL = "https://www.albion-online-data.com/api/v2/stats/Prices"

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                return await response.json()
    except:
        pass
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
    except:
        return 999999

def get_item_icon(item_id):
    return f"https://render.albiononline.com/v1/item/{item_id}.png"

def normalize_id(item_id):
    if "_LEVEL" in item_id and "@" not in item_id:
        lvl = item_id.split("_LEVEL")[1][0]
        return f"{item_id}@{lvl}"
    return item_id

with st.spinner("⚡ Pazar Verileri Asenkron Taranıyor..."):
    raw_api_data = get_data_sync(all_item_ids, ",".join(active_cities))

if not raw_api_data:
    st.error("API'den veri alınamadı. Lütfen tekrar deneyin.")
    st.stop()

df = pd.DataFrame(raw_api_data)
df['age'] = df['sell_price_min_date'].apply(calc_age)
df['norm_id'] = df['item_id'].apply(normalize_id)

valid_df = df[(df['city'].isin(active_cities)) & (df['sell_price_min'] > 0) & (df['age'] <= max_data_age)]

def get_best_price(norm_item_id, city_mode, find_min=True):
    sub = valid_df[valid_df['norm_id'] == norm_item_id]
    if sub.empty:
        return 0, "-", 999999
    if city_mode not in [auto_cheapest_label, auto_highest_label]:
        sub = sub[sub['city'] == city_mode]
        if sub.empty:
            return 0, city_mode, 999999
    
    if find_min:
        best_row = sub.loc[sub['sell_price_min'].idxmin()]
    else:
        best_row = sub.loc[sub['sell_price_min'].idxmax()]
        
    return int(best_row['sell_price_min']), best_row['city'], int(best_row['age'])

# --- SADECE HAM MADDE BAZLI HESAPLAMA MOTORU ---
calculated_data = []
rrr_factor = 1 - (rrr_value / 100.0)

for c in combos:
    tier = c["tier"]
    raw_qty = RAW_QTY_BY_TIER[tier]
    
    raw_p, raw_city, raw_age = get_best_price(c["raw_id"], raw_buy_city_mode, find_min=True)
    ref_p, sell_city, ref_age = get_best_price(c["ref_id"], sell_city_mode, find_min=False)
    
    if raw_p == 0 or ref_p == 0:
        continue
        
    max_age_row = max(raw_age, ref_age)
    
    # Efektif Ham Madde Gereksinimi (RRR Geri Dönüşümü Düşülmüş Net Miktar)
    eff_raw_qty = raw_qty * rrr_factor
    
    cost = eff_raw_qty * raw_p
    revenue = ref_p * (1 - (market_tax / 100.0))
    net_profit = revenue - cost
    roi = (net_profit / cost) * 100 if cost > 0 else 0
    
    calculated_data.append({
        "Seviye": c["label"],
        "İkon": get_item_icon(c["ref_id"]),
        "Ham İkon": get_item_icon(c["raw_id"]),
        "Eşya": f"{c['label']} {res_meta['tr_ref' if is_tr else 'en_ref']}",
        "Ham Madde": f"{c['label']} {res_meta['tr_raw' if is_tr else 'en_raw']}",
        "Alış Şehri": raw_city,
        "Ham Fiyat": raw_p,
        "Refine Şehri": locked_refine_city,
        "Satış Şehri": sell_city,
        "Satış Fiyatı": ref_p,
        "Maliyet": int(cost),
        "Birim Kâr": int(net_profit),
        "Toplam Kâr": int(net_profit * batch_size),
        "ROI": round(roi, 2),
        "Gereken Ham (Toplam)": int(round(eff_raw_qty * batch_size)),
        "Normal Ham (Birim)": raw_qty,
        "Yaş (Dk)": max_age_row
    })

if not calculated_data:
    st.warning("⚠️ Seçtiğin Tier/Enchant ve Şehir filtrelerinde güncel fiyat verisi bulunamadı. Sol menüden 'Maks. Veri Yaşı' süresini artırmayı dene.")
    st.stop()

calc_df = pd.DataFrame(calculated_data).sort_values(by="Birim Kâr", ascending=False)

# --- 2 SEKMELİ DASHBOARD ---
tab1, tab2 = st.tabs([
    "📊 Tek Seviye Detayı & Canlı Kartlar" if is_tr else "📊 Single Tier Detail & Live Cards",
    "🛡️ Seviye Karşılaştırması" if is_tr else "🛡️ Tier Comparison"
])

with tab1:
    left_col, right_col = st.columns([5.5, 5.5])

    with left_col:
        st.markdown(f"### 📋 Rafinasyon Tablosu (🔒 {locked_refine_city})")
        st.dataframe(
            calc_df[[
                "İkon", "Seviye", "Alış Şehri", "Ham Fiyat", 
                "Satış Şehri", "Satış Fiyatı", "Maliyet", "Birim Kâr", "ROI"
            ]],
            use_container_width=True,
            hide_index=True,
            height=540,
            column_config={
                "İkon": st.column_config.ImageColumn("", width="small"),
                "Seviye": st.column_config.TextColumn("Tier"),
                "Alış Şehri": st.column_config.TextColumn("Ham Alış"),
                "Ham Fiyat": st.column_config.NumberColumn("Ham 🥈", format="%d"),
                "Satış Şehri": st.column_config.TextColumn("Satış Şehri"),
                "Satış Fiyatı": st.column_config.NumberColumn("Satış 🥈", format="%d"),
                "Maliyet": st.column_config.NumberColumn("Maliyet 🥈", format="%d"),
                "Birim Kâr": st.column_config.NumberColumn("Net Kâr 🥈", format="%d"),
                "ROI": st.column_config.NumberColumn("ROI %", format="%.1f%%")
            }
        )

    with right_col:
        tier_options = ["🏆 En Yüksek Kârlıyı Göster"] + list(calc_df["Seviye"].unique())
        picked_card_tier = st.selectbox("🎯 Kartta İncelenecek Seviyeyi Seç (Örn: T4.0):" if is_tr else "🎯 Select Tier to Inspect:", tier_options)

        if picked_card_tier == "🏆 En Yüksek Kârlıyı Göster":
            top1 = calc_df.iloc[0]
        else:
            top1 = calc_df[calc_df["Seviye"] == picked_card_tier].iloc[0]

        kar_renk_1 = "#10B981" if top1["Birim Kâr"] > 0 else "#EF4444"

        # 1. ALTIN KART: HAM MADDE ➔ İŞLENMİŞ ÜRÜN
        st.markdown(f"""
        <div class="god-card-gold">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;">
                <div style="display:flex; align-items:center; gap:15px;">
                    <img src="{top1['Ham İkon']}" class="item-icon" title="{top1['Ham Madde']}">
                    <span style="font-size:26px; color:#D4AF37; font-weight:bold;">➔</span>
                    <img src="{top1['İkon']}" class="item-icon" title="{top1['Eşya']}">
                </div>
                <div style="text-align:center; padding:5px 10px;">
                    <span style="color:#94A3B8; font-size:12px;">ROI ORANI (%{rrr_value} RRR)</span><br>
                    <span style="color:{kar_renk_1}; font-size:28px; font-weight:800;">%{top1['ROI']}</span><br>
                    <span style="color:#CBD5E1; font-size:13px;">Birim Kâr: <b>{top1['Birim Kâr']:,} 🥈</b></span>
                </div>
                <div style="text-align:right; border-left:1px solid #4A3B23; padding-left:15px;">
                    <span style="color:#FFD700; font-family:'Cinzel',serif; font-weight:800; font-size:16px;">👑 {top1['Eşya']}</span><br>
                    <span style="color:#E2E8F0; font-size:13px;">{batch_size} Adet Üretim Net Kârı:</span><br>
                    <span style="color:{kar_renk_1}; font-size:24px; font-weight:800;">{top1['Toplam Kâr']:,} 🥈</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. MAVİ KART: SADECE HAM MADDE ALIŞ -> BONUS ŞEHİR REFINE -> SATIŞ ROTASI
        st.markdown(f"""
        <div class="god-card-blue">
            <div>
                <span style="color:#38BDF8; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">🛒 {batch_size} ADET {top1['Seviye']} İÇİN ROTA & HAM MADDE LİSTESİ</span>
                <ul style="margin:10px 0 0 0; padding-left:18px; color:#E2E8F0; font-size:14px; line-height:1.8;">
                    <li><b>1. Ham Madde Al:</b> <span style="color:#FFD700; font-weight:bold;">{top1['Alış Şehri']}</span> pazarından toplam <b>{top1['Gereken Ham (Toplam)']:,} adet</b> {top1['Ham Madde']} çek <i>(Tanesi: {top1['Ham Fiyat']:,} 🥈)</i></li>
                    <li><b>2. Bonuslu Şehirde İşle:</b> <span style="color:#38BDF8; font-weight:bold;">{locked_refine_city}</span> şehrinde <b>%{rrr_value} RRR</b> ile rafine et.</li>
                    <li><b>3. Satış Yap:</b> Çıkan {batch_size} adet {top1['Eşya']} ürününü <span style="color:#10B981; font-weight:bold;">{top1['Satış Şehri']}</span> pazarında tanesi <b>{top1['Satış Fiyatı']:,} 🥈</b> fiyattan okut!</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. DYNAMIC GRAPH
        st.markdown("#### 📈 Dynamic Graph (Ham Maliyet vs Satış Fiyatı)")
        plot_df = calc_df.sort_values(by="Seviye")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_df["Seviye"], y=plot_df["Satış Fiyatı"],
            mode='lines+markers', name='Satış Fiyatı 🥈',
            line=dict(color='#38BDF8', width=3),
            fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.18)'
        ))
        fig.add_trace(go.Scatter(
            x=plot_df["Seviye"], y=plot_df["Maliyet"],
            mode='lines+markers', name='Ham Madde Maliyeti 🥈',
            line=dict(color='#D4AF37', width=3),
            fill='tozeroy', fillcolor='rgba(212, 175, 55, 0.22)'
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(18, 24, 31, 0.7)",
            plot_bgcolor="rgba(18, 24, 31, 0.4)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=220,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown(f"### 🏆 Tüm Seviyelerin Kârlılık Karşılaştırması (🔒 {locked_refine_city})")
    
    fig_bar = px.bar(
        calc_df.sort_values(by="Seviye"),
        x="Seviye",
        y="Birim Kâr",
        color="ROI",
        hover_data=["Alış Şehri", "Satış Şehri", "Maliyet", "Satış Fiyatı"],
        labels={"Birim Kâr": "Birim Başı Net Kâr (Gümüş) 🥈", "Seviye": "Tier / Enchant"},
        template="plotly_dark",
        color_continuous_scale="Tealgrn"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.dataframe(
        calc_df[[
            "Seviye", "Eşya", "Alış Şehri", "Ham Fiyat", 
            "Refine Şehri", "Satış Şehri", "Satış Fiyatı", 
            "Maliyet", "Birim Kâr", "Toplam Kâr", "ROI", "Yaş (Dk)"
        ]],
        use_container_width=True,
        hide_index=True
    )
