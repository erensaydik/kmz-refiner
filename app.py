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
        margin-bottom: 20px;
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
        padding: 16px;
        animation: pulseGold 3s infinite ease-in-out;
        transition: transform 0.3s ease;
        margin-bottom: 14px;
    }

    .god-card-blue {
        background: linear-gradient(135deg, #10212B 0%, #12151A 100%);
        border: 2px solid #38BDF8;
        border-radius: 10px;
        padding: 16px;
        animation: pulseBlue 3s infinite ease-in-out;
        transition: transform 0.3s ease;
        margin-bottom: 14px;
    }

    .god-card-gold:hover, .god-card-blue:hover {
        transform: translateY(-3px) scale(1.01);
    }

    .item-icon {
        width: 64px;
        height: 64px;
        animation: floatIcon 3.5s ease-in-out infinite;
        filter: drop-shadow(0 5px 8px rgba(0,0,0,0.7));
        transition: transform 0.2s ease;
    }

    .item-icon:hover {
        transform: scale(1.18) rotate(3deg);
        filter: drop-shadow(0 0 12px rgba(255, 215, 0, 0.8));
    }

    .bonus-badge {
        background: linear-gradient(90deg, #1E3A8A 0%, #0F172A 100%);
        border-left: 4px solid #38BDF8;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 15px;
        font-size: 14px;
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
    <p>{"Albion Online Çoklu Şehir Rafinasyon & Geri Dönüşüm Hesaplayıcısı" if is_tr else "Albion Online Multi-City Refining & Recycling Calculator"}</p>
</div>
""", unsafe_allow_html=True)

# --- KAYNAK SÖZLÜĞÜ VE BONUS ŞEHİRLERİ ---
RESOURCES = {
    "🌿 Elyaf (Fiber -> Cloth)": {
        "raw": "FIBER", "refined": "CLOTH", "bonus_city": "Lymhurst",
        "tr_raw": "Elyaf", "tr_ref": "Kumaş", "en_raw": "Fiber", "en_ref": "Cloth"
    },
    "⛏️ Cevher (Ore -> Metal Bar)": {
        "raw": "ORE", "refined": "METALBAR", "bonus_city": "Thetford",
        "tr_raw": "Cevher", "tr_ref": "Külçe", "en_raw": "Ore", "en_ref": "Metal Bar"
    },
    "🐾 Deri (Hide -> Leather)": {
        "raw": "HIDE", "refined": "LEATHER", "bonus_city": "Martlock",
        "tr_raw": "Ham Deri", "tr_ref": "Deri", "en_raw": "Hide", "en_ref": "Leather"
    },
    "🌲 Odun (Wood -> Planks)": {
        "raw": "WOOD", "refined": "PLANKS", "bonus_city": "Fort Sterling",
        "tr_raw": "Tomruk", "tr_ref": "Kalas", "en_raw": "Wood", "en_ref": "Planks"
    },
    "🪨 Taş (Stone -> Stone Block)": {
        "raw": "STONE", "refined": "STONEBLOCK", "bonus_city": "Bridgewatch",
        "tr_raw": "Kaya", "tr_ref": "Taş Blok", "en_raw": "Stone", "en_ref": "Stone Block"
    }
}

TIER_FORMULAS = {
    "T3": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T2"},
    "T4": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T3"},
    "T5": {"raw_qty": 3, "prev_qty": 1, "prev_tier": "T4"},
    "T6": {"raw_qty": 4, "prev_qty": 1, "prev_tier": "T5"},
    "T7": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T6"},
    "T8": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T7"},
}

ROYAL_CITIES = ["Lymhurst", "Bridgewatch", "Martlock", "Thetford", "Fort Sterling"]

# --- SOL PANEL: 1. KAYNAK VE TIER SEÇİMİ ---
st.sidebar.header("📦 1. Kaynak & Seviye Seçimi" if is_tr else "📦 1. Resource & Tier Filter")
selected_res_key = st.sidebar.selectbox("Üretilecek Kaynak:" if is_tr else "Resource Type:", list(RESOURCES.keys()))
res_meta = RESOURCES[selected_res_key]

selected_tiers = st.sidebar.multiselect(
    "Seviyeler (Tier):" if is_tr else "Select Tiers:",
    options=["T3", "T4", "T5", "T6", "T7", "T8"],
    default=["T4", "T5", "T6", "T7", "T8"]
)

selected_enchants = st.sidebar.multiselect(
    "Büyü Seviyesi (Enchant):" if is_tr else "Select Enchants:",
    options=[".0", ".1", ".2", ".3", ".4"],
    default=[".0", ".1", ".2", ".3"]
)

# --- SOL PANEL: 2. ALIŞ VE SATIŞ ŞEHİRLERİ ---
st.sidebar.markdown("---")
st.sidebar.header("🗺️ 2. Alış & Satış Şehirleri" if is_tr else "🗺️ 2. Buy & Sell Cities")

include_caerleon = st.sidebar.checkbox("Caerleon'u Dahil Et (Kırmızı Bölge)" if is_tr else "Include Caerleon", value=False)
active_cities = ROYAL_CITIES + (["Caerleon"] if include_caerleon else [])

auto_cheapest_label = "🌟 Otomatik (En Ucuz Şehir)" if is_tr else "🌟 Auto (Cheapest City)"
auto_highest_label = "💰 Otomatik (En Pahalı Şehir)" if is_tr else "💰 Auto (Highest Price City)"

raw_buy_city_mode = st.sidebar.selectbox(
    "Hammadde Alış Şehri:" if is_tr else "Raw Material Buy City:",
    options=[auto_cheapest_label] + active_cities,
    index=0
)

prev_buy_city_mode = st.sidebar.selectbox(
    "Önceki Seviye İşlenmiş Alış Şehri:" if is_tr else "Prev Tier Refined Buy City:",
    options=[auto_cheapest_label] + active_cities,
    index=0
)

sell_city_mode = st.sidebar.selectbox(
    "İşlenmiş Ürün Satış Şehri:" if is_tr else "Refined Product Sell City:",
    options=[auto_highest_label] + active_cities,
    index=0
)

# --- SOL PANEL: 3. RRR VE VERGİ AYARLARI ---
st.sidebar.markdown("---")
st.sidebar.header("⚒️ 3. RRR & Vergi Ayarları" if is_tr else "⚒️ 3. RRR & Tax Settings")

rrr_preset = st.sidebar.selectbox(
    "Geri Dönüş (RRR) Senaryosu:" if is_tr else "RRR Preset:",
    (
        "Bonuslu Şehir - Focus Yok (%36.7)",
        "Bonuslu Şehir + Focus (%53.9)",
        "Sıradan Şehir - Focus Yok (%15.2)",
        "Sıradan Şehir + Focus (%43.5)",
        "Özel RRR Değeri Gir"
    ),
    index=0
)

if "36.7" in rrr_preset: rrr_value = 36.7
elif "53.9" in rrr_preset: rrr_value = 53.9
elif "15.2" in rrr_preset: rrr_value = 15.2
elif "43.5" in rrr_preset: rrr_value = 43.5
else: rrr_value = st.sidebar.slider("Özel RRR (%):", 0.0, 60.0, 36.7, 0.1)

market_tax = st.sidebar.slider("Satış Vergisi (%)" if is_tr else "Market Tax (%)", 0.0, 10.0, 4.0, 0.1, help="Premium ile doğrudan satış %4, Satış Emri (Sell Order) kurulum dahil %6.5")
station_fee_per_item = st.sidebar.number_input("Birim Başı İstasyon Vergisi (Gümüş)" if is_tr else "Station Fee per Item", min_value=0, value=0, step=10)
max_data_age = st.sidebar.slider("Maks. Veri Yaşı (Dakika)" if is_tr else "Max Data Age (Mins)", 10, 1440, 300, 10)
batch_size = st.sidebar.number_input("Üretim Adedi (Simülasyon)" if is_tr else "Batch Size", min_value=1, value=300, step=50)

if st.sidebar.button("🔄 Verileri Şimdi Yenile" if is_tr else "🔄 Refresh Market Data", use_container_width=True):
    st.cache_data.clear()

# --- BONUS ŞEHRİ BİLGİ BARI ---
st.markdown(f"""
<div class="bonus-badge">
    💡 <b>{"İdeal Rafinasyon (Üretim) Şehri" if is_tr else "Ideal Refining City"}:</b> 
    <span style="color:#38BDF8; font-weight:bold;">{res_meta['bonus_city']}</span> 
    ({"%40 Üretim Bonusu -> %36.7 RRR (Focus'suz) / %53.9 RRR (Focus'lu)" if is_tr else "+40% Refining Bonus -> 36.7% RRR (No Focus) / 53.9% RRR (Focus)"})
</div>
""", unsafe_allow_html=True)

if not selected_tiers or not selected_enchants:
    st.warning("👈 Lütfen sol menüden en az bir Seviye (Tier) ve Büyü (Enchant) seçin.")
    st.stop()

# --- DOĞRU ALBION ID VE KOMBINASYON MOTORU ---
def make_item_id(tier, base_type, enc):
    if enc == ".0" or tier in ["T2", "T3"]:
        return f"{tier}_{base_type}"
    lvl = enc.replace(".", "")
    # Albion Data Project'te enchantlı kaynakların gerçek ID formatı: T4_ORE_LEVEL1@1
    return f"{tier}_{base_type}_LEVEL{lvl}@{lvl}"

combos = []
for tier in selected_tiers:
    for enc in selected_enchants:
        # T3 ve Taş (Stone) için sadece .0 (Düz) rafinasyon standarttır
        if tier == "T3" and enc != ".0":
            continue
        if res_meta["raw"] == "STONE" and enc != ".0":
            continue

        raw_id = make_item_id(tier, res_meta["raw"], enc)
        ref_id = make_item_id(tier, res_meta["refined"], enc)
        
        prev_tier = TIER_FORMULAS[tier]["prev_tier"]
        # ALBION KURALI: T4.1/4.2/4.3/4.4 üretirken düz T3.0 kullanılır. T5+ enchantlı üretirken önceki tier da aynı enchantta olur!
        prev_enc = ".0" if tier in ["T3", "T4"] else enc
        prev_id = make_item_id(prev_tier, res_meta["refined"], prev_enc)

        combos.append({
            "tier": tier,
            "enchant": enc,
            "label": f"{tier}{enc}",
            "raw_id": raw_id,
            "ref_id": ref_id,
            "prev_id": prev_id,
            "prev_label": f"{prev_tier}{prev_enc}"
        })

# Tüm olası ID'leri topla (T2'den T8'e)
all_query_ids = set()
for c in combos:
    all_query_ids.update([c["raw_id"], c["ref_id"], c["prev_id"]])
    # API uyumluluğu için @1 olmayan versiyonlarını da sorguya ekle
    all_query_ids.update([c["raw_id"].split("@")[0], c["ref_id"].split("@")[0], c["prev_id"].split("@")[0]])

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
    chunk_size = 65
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
    # T4_ORE_LEVEL1 gelirse T4_ORE_LEVEL1@1 ile eşleşmesi için normalize et
    if "_LEVEL" in item_id and "@" not in item_id:
        lvl = item_id.split("_LEVEL")[1][0]
        return f"{item_id}@{lvl}"
    return item_id

with st.spinner("⚡ Tüm Şehirlerin Pazar Verileri Asenkron Taranıyor..."):
    raw_api_data = get_data_sync(all_item_ids, ",".join(active_cities))

if not raw_api_data:
    st.error("API'den veri alınamadı. Lütfen tekrar deneyin.")
    st.stop()

df = pd.DataFrame(raw_api_data)
df['age'] = df['sell_price_min_date'].apply(calc_age)
df['norm_id'] = df['item_id'].apply(normalize_id)

# Geçerli fiyatları filtrele
valid_df = df[(df['city'].isin(active_cities)) & (df['sell_price_min'] > 0) & (df['age'] <= max_data_age)]

# Şehir bazlı en iyi fiyatları bulucu yardımcı fonksiyon
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

# --- HESAPLAMA MOTORU ---
calculated_data = []
rrr_factor = 1 - (rrr_value / 100.0)

for c in combos:
    tier = c["tier"]
    formula = TIER_FORMULAS[tier]
    
    raw_p, raw_city, raw_age = get_best_price(c["raw_id"], raw_buy_city_mode, find_min=True)
    prev_p, prev_city, prev_age = get_best_price(c["prev_id"], prev_buy_city_mode, find_min=True)
    ref_p, sell_city, ref_age = get_best_price(c["ref_id"], sell_city_mode, find_min=False)
    
    if raw_p == 0 or prev_p == 0 or ref_p == 0:
        continue
        
    max_age_row = max(raw_age, prev_age, ref_age)
    
    # Efektif malzeme gereksinimi (Geri dönüşüm hesaba katılarak)
    eff_raw_qty = formula["raw_qty"] * rrr_factor
    eff_prev_qty = formula["prev_qty"] * rrr_factor
    
    cost = (eff_raw_qty * raw_p) + (eff_prev_qty * prev_p) + station_fee_per_item
    revenue = ref_p * (1 - (market_tax / 100.0))
    net_profit = revenue - cost
    roi = (net_profit / cost) * 100 if cost > 0 else 0
    
    calculated_data.append({
        "Seviye": c["label"],
        "Tier": tier,
        "Enchant": c["enchant"],
        "İkon": get_item_icon(c["ref_id"]),
        "Ham İkon": get_item_icon(c["raw_id"]),
        "Önceki İkon": get_item_icon(c["prev_id"]),
        "Eşya": f"{c['label']} {res_meta['tr_ref' if is_tr else 'en_ref']}",
        "Ham Madde": f"{c['label']} {res_meta['tr_raw' if is_tr else 'en_raw']}",
        "Önceki Seviye Adı": f"{c['prev_label']} {res_meta['tr_ref' if is_tr else 'en_ref']}",
        "Ham Alış Şehri": raw_city,
        "Ham Fiyat": raw_p,
        "Önceki Alış Şehri": prev_city,
        "Önceki Fiyat": prev_p,
        "Satış Şehri": sell_city,
        "Satış Fiyatı": ref_p,
        "Efektif Maliyet": int(cost),
        "Birim Kâr": int(net_profit),
        "Toplam Kâr": int(net_profit * batch_size),
        "ROI": round(roi, 2),
        "Gereken Ham (Toplam)": int(round(eff_raw_qty * batch_size)),
        "Gereken Önceki (Toplam)": int(round(eff_prev_qty * batch_size)),
        "Yaş (Dk)": max_age_row
    })

if not calculated_data:
    st.warning("⚠️ Seçtiğin Tier/Enchant ve Şehir filtrelerinde güncel fiyat verisi bulunamadı. Sol menüden 'Maks. Veri Yaşı' süresini artırmayı veya şehirleri 'Otomatik' yapmayı dene.")
    st.stop()

calc_df = pd.DataFrame(calculated_data).sort_values(by="Birim Kâr", ascending=False)

# --- GÖRSELDEKİ 2 SEKMELİ YAPI ---
tab1, tab2 = st.tabs([
    "📊 Tek Seviye Detayı & Canlı Kartlar" if is_tr else "📊 Single Tier Detail & Live Cards",
    "🛡️ Seviye Karşılaştırması & Rotalar" if is_tr else "🛡️ Tier Comparison & Routes"
])

with tab1:
    left_col, right_col = st.columns([5.5, 5.5])

    with left_col:
        st.markdown("### 📋 Rafinasyon Kâr Tablosu" if is_tr else "### 📋 Refining Profit Table")
        st.dataframe(
            calc_df[[
                "İkon", "Seviye", "Ham Alış Şehri", "Ham Fiyat", 
                "Önceki Alış Şehri", "Önceki Fiyat", "Satış Şehri", 
                "Satış Fiyatı", "Birim Kâr", "ROI"
            ]],
            use_container_width=True,
            hide_index=True,
            height=540,
            column_config={
                "İkon": st.column_config.ImageColumn("", width="small"),
                "Seviye": st.column_config.TextColumn("Tier"),
                "Ham Alış Şehri": st.column_config.TextColumn("Ham Şehir"),
                "Ham Fiyat": st.column_config.NumberColumn("Ham 🥈", format="%d"),
                "Önceki Alış Şehri": st.column_config.TextColumn("Önceki Şehir"),
                "Önceki Fiyat": st.column_config.NumberColumn("Önceki 🥈", format="%d"),
                "Satış Şehri": st.column_config.TextColumn("Satış Şehri"),
                "Satış Fiyatı": st.column_config.NumberColumn("Satış 🥈", format="%d"),
                "Birim Kâr": st.column_config.NumberColumn("Net Kâr 🥈", format="%d"),
                "ROI": st.column_config.NumberColumn("ROI %", format="%.1f%%")
            }
        )

    with right_col:
        # KULLANICININ İSTEDİĞİ SEVİYEYİ KARTTA İNCELEME SEÇENEĞİ
        tier_options = ["🏆 En Yüksek Kârlıyı Göster"] + list(calc_df["Seviye"].unique())
        picked_card_tier = st.selectbox("🎯 Kartta İncelenecek Seviyeyi Seç (Örn: T4.0):" if is_tr else "🎯 Select Tier to Inspect:", tier_options)

        if picked_card_tier == "🏆 En Yüksek Kârlıyı Göster":
            top1 = calc_df.iloc[0]
        else:
            top1 = calc_df[calc_df["Seviye"] == picked_card_tier].iloc[0]

        kar_renk_1 = "#10B981" if top1["Birim Kâr"] > 0 else "#EF4444"

        # 1. ALTIN KART: SEÇİLEN VEYA EN İYİ FIRSAT DETAYI
        st.markdown(f"""
        <div class="god-card-gold">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <img src="{top1['Ham İkon']}" class="item-icon" title="{top1['Ham Madde']}">
                    <span style="font-size:22px; color:#D4AF37; font-weight:bold;">+</span>
                    <img src="{top1['Önceki İkon']}" class="item-icon" title="{top1['Önceki Seviye Adı']}">
                    <span style="font-size:22px; color:#D4AF37; font-weight:bold;">➔</span>
                    <img src="{top1['İkon']}" class="item-icon" title="{top1['Eşya']}">
                </div>
                <div style="text-align:center; padding:5px 10px;">
                    <span style="color:#94A3B8; font-size:12px;">YATIRIM GETİRİSİ (ROI)</span><br>
                    <span style="color:{kar_renk_1}; font-size:28px; font-weight:800;">%{top1['ROI']}</span><br>
                    <span style="color:#CBD5E1; font-size:13px;">Birim Kâr: <b>{top1['Birim Kâr']:,} 🥈</b></span>
                </div>
                <div style="text-align:right; border-left:1px solid #4A3B23; padding-left:15px;">
                    <span style="color:#FFD700; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">👑 {top1['Eşya']}</span><br>
                    <span style="color:#E2E8F0; font-size:13px;">{batch_size} Adet Üretim Net Kârı:</span><br>
                    <span style="color:{kar_renk_1}; font-size:24px; font-weight:800;">{top1['Toplam Kâr']:,} 🥈</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. MAVİ KART: TAM ALIŞVERİŞ VE ROTA REHBERİ
        st.markdown(f"""
        <div class="god-card-blue">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:#38BDF8; font-family:'Cinzel',serif; font-weight:800; font-size:15px;">🛒 {batch_size} ADET {top1['Seviye']} İÇİN ALIŞVERİŞ & ROTA LİSTESİ</span>
                    <ul style="margin:8px 0 0 0; padding-left:18px; color:#E2E8F0; font-size:13.5px; line-height:1.7;">
                        <li><b>1. Hammadde Al:</b> <span style="color:#FFD700;">{top1['Ham Alış Şehri']}</span> pazarından <b>{top1['Gereken Ham (Toplam)']:,} adet</b> {top1['Ham Madde']} al <i>(Birim: {top1['Ham Fiyat']:,} 🥈)</i></li>
                        <li><b>2. Önceki Tier Al:</b> <span style="color:#FFD700;">{top1['Önceki Alış Şehri']}</span> pazarından <b>{top1['Gereken Önceki (Toplam)']:,} adet</b> {top1['Önceki Seviye Adı']} al <i>(Birim: {top1['Önceki Fiyat']:,} 🥈)</i></li>
                        <li><b>3. Rafine Et:</b> <span style="color:#38BDF8;">{res_meta['bonus_city']}</span> şehrinde (%{rrr_value} RRR ile) işle.</li>
                        <li><b>4. Satış Yap:</b> <span style="color:#10B981;">{top1['Satış Şehri']}</span> pazarında <b>{top1['Satış Fiyatı']:,} 🥈</b> fiyattan sat!</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. SAĞ ALT DYNAMIC GRAPH (Maliyet vs Satış Trendi)
        st.markdown("#### 📈 Dynamic Graph (Maliyet vs Net Gelir)")
        plot_df = calc_df.sort_values(by="Seviye")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_df["Seviye"], y=plot_df["Satış Fiyatı"],
            mode='lines+markers', name='Satış Fiyatı 🥈',
            line=dict(color='#38BDF8', width=3),
            fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.18)'
        ))
        fig.add_trace(go.Scatter(
            x=plot_df["Seviye"], y=plot_df["Efektif Maliyet"],
            mode='lines+markers', name='Efektif Maliyet 🥈',
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
    st.markdown("### 🏆 Seviye Bazlı Kâr ve Şehir Rotaları Karşılaştırması")
    
    fig_bar = px.bar(
        calc_df.sort_values(by="Seviye"),
        x="Seviye",
        y="Birim Kâr",
        color="ROI",
        hover_data=["Ham Alış Şehri", "Önceki Alış Şehri", "Satış Şehri", "Efektif Maliyet", "Satış Fiyatı"],
        labels={"Birim Kâr": "Birim Başı Net Kâr (Gümüş) 🥈", "Seviye": "Tier / Enchant"},
        template="plotly_dark",
        color_continuous_scale="Tealgrn"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.dataframe(
        calc_df[[
            "Seviye", "Eşya", "Ham Alış Şehri", "Ham Fiyat", 
            "Önceki Alış Şehri", "Önceki Fiyat", "Satış Şehri", "Satış Fiyatı", 
            "Efektif Maliyet", "Birim Kâr", "Toplam Kâr", "ROI", "Yaş (Dk)"
        ]],
        use_container_width=True,
        hide_index=True
    )
