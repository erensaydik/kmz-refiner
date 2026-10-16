import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone
import plotly.express as px

# --- SAYFA AYARLARI & ÖZEL OYUN TASARIMI (CSS) ---
st.set_page_config(page_title="Enlil God Tier Refine", layout="wide", initial_sidebar_state="expanded")

# Albion Online temasına uygun, altın/bronz parıltılı ve metalik karanlık UI
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #0E1216 !important;
        color: #D1D5DB !important;
        font-family: 'Cinzel', 'Inter', sans-serif;
    }
    
    /* Sol Panel (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #12181F !important;
        border-right: 2px solid #3A2F1E;
    }
    
    /* Altın-Bronz Başlıklar */
    h1, h2, h3 {
        color: #B9935A !important;
        text-shadow: 0 0 10px rgba(185, 147, 90, 0.3);
    }
    
    /* Butonlar */
    .stButton>button {
        background: linear-gradient(135deg, #4A3B23 0%, #2A1F10 100%) !important;
        color: #E2C38F !important;
        border: 1px solid #755B31 !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #614D2E 0%, #3B2B16 100%) !important;
        border-color: #B9935A !important;
        box-shadow: 0 0 8px rgba(185, 147, 90, 0.5);
        color: #FFF !important;
    }
    
    /* Kartlar (Metrik kutuları) */
    div[data-testid="stMetricValue"] {
        color: #E2C38F !important;
        font-size: 24px !important;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
    }
    .metric-card {
        background-color: #161D27;
        border: 1px solid #3A2F1E;
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    
    /* Input ve Sliderlar */
    .stSlider [data-baseweb="slider"] {
        background-color: #1C2331;
    }
    .stSlider [data-baseweb="slider"] div {
        color: #B9935A !important;
    }
    
    /* Özel Uyarılar */
    .stAlert {
        background-color: #1C1917 !important;
        border: 1px solid #78350F !important;
        color: #FDBA74 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DİL SEÇİMİ VE GÖRÜNÜM ---
lang = st.sidebar.radio("🌐 Dil / Language", ("Türkçe", "English"))
is_tr = (lang == "Türkçe")

st.title("🛡️ ENLİL - GOD TIER REFINE SCANNER" if is_tr else "🛡️ ENLİL - GOD TIER REFINING SCANNER")
st.markdown("*Ham Kaynaklardan İşlenmiş Bloklara: En Karlı Rafinasyonu Asenkron Güçle Analiz Et.*" if is_tr else "*From Raw Materials to Processed Blocks: Analyze the Most Profitable Refining with Async Power.*")

# --- KAYNAK VE TIER SÖZLÜKLERİ ---
RESOURCES = {
    "Cevher (Ore -> Bar)": {
        "raw": "ORE", "refined": "METALBAR", "icon_raw": "ORE", "icon_ref": "METALBAR",
        "tr": {"raw_name": "Cevher", "ref_name": "Külçe"},
        "en": {"raw_name": "Ore", "ref_name": "Bar"}
    },
    "Elyaf (Fiber -> Cloth)": {
        "raw": "FIBER", "refined": "CLOTH", "icon_raw": "FIBER", "icon_ref": "CLOTH",
        "tr": {"raw_name": "Elyaf", "ref_name": "Kumaş"},
        "en": {"raw_name": "Fiber", "ref_name": "Cloth"}
    },
    "Deri (Hide -> Leather)": {
        "raw": "HIDE", "refined": "LEATHER", "icon_raw": "HIDE", "icon_ref": "LEATHER",
        "tr": {"raw_name": "Ham Deri", "ref_name": "Deri"},
        "en": {"raw_name": "Hide", "ref_name": "Leather"}
    },
    "Odun (Wood -> Planks)": {
        "raw": "WOOD", "refined": "PLANKS", "icon_raw": "WOOD", "icon_ref": "PLANKS",
        "tr": {"raw_name": "Tomruk", "ref_name": "Kalas"},
        "en": {"raw_name": "Wood", "ref_name": "Plank"}
    },
    "Taş (Stone -> Stone Block)": {
        "raw": "STONE", "refined": "STONEBLOCK", "icon_raw": "STONE", "icon_ref": "STONEBLOCK",
        "tr": {"raw_name": "Kaya", "ref_name": "Blok"},
        "en": {"raw_name": "Stone", "ref_name": "Block"}
    }
}

# Albion Online'ın katı formül gereksinimleri (Gerekli hammadde ve bir önceki tier işlenmiş malzeme)
TIER_FORMULAS = {
    "T3": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T2"},
    "T4": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T3"},
    "T5": {"raw_qty": 3, "prev_qty": 1, "prev_tier": "T4"},
    "T6": {"raw_qty": 4, "prev_qty": 1, "prev_tier": "T5"},
    "T7": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T6"},
    "T8": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T7"},
}

ALL_LOCATIONS = ["Lymhurst", "Bridgewatch", "Martlock", "Thetford", "Fort Sterling", "Caerleon"]

# --- SOL PANEL (FİLTRELER VE AYARLAR) ---
st.sidebar.header("⚙️ Genel Ayarlar" if is_tr else "⚙️ General Settings")
max_data_age = st.sidebar.slider("Maks. Gecikme (Dakika)" if is_tr else "Max Delay (Mins)", 5, 1440, 120, 15)
market_tax = st.sidebar.slider("Pazar Vergisi (%)" if is_tr else "Market Tax (%)", 0.0, 10.0, 4.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.header("⚒️ Rafinasyon Geri Dönüş Oranı (RRR)" if is_tr else "⚒️ Resource Return Rate (RRR)")
# RRR Değeri doğrudan kâr oranlarını çarpar (Geri dönüşüm)
rrr_preset = st.sidebar.selectbox(
    "Geri Dönüş (RRR) Senaryosu:" if is_tr else "RRR Presets:",
    (
        "Geri Dönüş Yok (%0)" if is_tr else "No Return (%0)",
        "Sıradan Şehir (%15.2)" if is_tr else "Normal City (%15.2)",
        "Bonuslu Şehir (%36.7)" if is_tr else "City Bonus (%36.7)",
        "Odaklanma (Focus) İle (%43.5)" if is_tr else "Focus Without Bonus (%43.5)",
        "Odaklanma + Şehir Bonusu (%53.9)" if is_tr else "Focus + City Bonus (%53.9)",
        "Özel Değer Belirle" if is_tr else "Custom Value"
    ),
    index=2
)

if "Özel" in rrr_preset or "Custom" in rrr_preset:
    rrr_value = st.sidebar.slider("Özel RRR %", 0.0, 60.0, 36.7, 0.1)
else:
    preset_map = {
        "Yok": 0.0, "No": 0.0,
        "Sıradan": 15.2, "Normal": 15.2,
        "Bonuslu": 36.7, "City": 36.7,
        "Odaklanma (Focus)": 43.5, "Focus Without": 43.5,
        "Odaklanma +": 53.9, "Focus +": 53.9
    }
    rrr_value = [v for k, v in preset_map.items() if k in rrr_preset][0]

st.sidebar.markdown("---")
st.sidebar.header("🌎 Pazar Lokasyonu" if is_tr else "🌎 Market Location")
refining_city = st.sidebar.selectbox("Rafinasyonun Yapılacağı Şehir" if is_tr else "Refining City", ALL_LOCATIONS, index=2)

st.sidebar.markdown("---")
st.sidebar.header("🌿 Rafinasyon Detayları" if is_tr else "🌿 Refining Details")
selected_res_key = st.sidebar.selectbox("Kaynak Türü" if is_tr else "Resource Type", list(RESOURCES.keys()))
res_meta = RESOURCES[selected_res_key]

# --- ASENKRON VERİ ÇEKME MOTORU ---
BASE_URL = "https://www.albion-online-data.com/api/v2/stats/Prices"

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=12) as response:
            if response.status == 200: return await response.json()
    except: pass
    return []

async def fetch_refining_data(items, locs):
    # Çift istek engeli ve güvenli kümeleme
    chunk_size = 80
    urls = [f"{BASE_URL}/{','.join(items[i:i + chunk_size])}?locations={locs}" for i in range(0, len(items), chunk_size)]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

def get_data_sync(items, locs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_all_data_async_with_retry(items, locs))
    loop.close()
    return data

async def fetch_all_data_async_with_retry(items, locs):
    return await fetch_refining_data(items, locs)

def calc_age(date_str):
    if not date_str or date_str.startswith("0001"): return 999999
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return int((datetime.now(timezone.utc) - dt).total_seconds() / 60)
    except: return 999999

# Oyun içi ikonları Albion CDN'den çek
def get_item_icon(item_id):
    return f"https://render.albiononline.com/v1/item/{item_id}.png"

# --- TÜM COMBOS VE ID ÜRETİMİ ---
combos = []
for tier in ["T3", "T4", "T5", "T6", "T7", "T8"]:
    # Enchant seviyeleri (.0, .1, .2, .3, .4)
    enchants = [""] if tier == "T3" else ["", "_LEVEL1", "_LEVEL2", "_LEVEL3", "_LEVEL4"]
    for enc in enchants:
        # Ham Kaynak, İşlenmiş Kaynak ve Bir Önceki Seviyenin flat (ençantsız) işlenmişi
        combos.append({
            "tier": tier,
            "enchant": enc.replace("_LEVEL", "."),
            "raw_id": f"{tier}_{res_meta['raw']}{enc}",
            "ref_id": f"{tier}_{res_meta['refined']}{enc}",
            "prev_id": f"{TIER_FORMULAS[tier]['prev_tier']}_{res_meta['refined']}" # Albion Kuralı: Enchantlı dahi olsa önceki tier her zaman flat (.0) istenir
        })

# Benzersiz tüm ID'leri listele ve API'ye gönder
all_item_ids = list(set([c["raw_id"] for c in combos] + [c["ref_id"] for c in combos] + [c["prev_id"] for c in combos]))

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🔄 Verileri Yenile" if is_tr else "🔄 Refresh Prices", use_container_width=True):
        st.cache_data.clear()

with st.spinner("⚔️ Albion Pazar Verileri Asenkron Çekiliyor..." if is_tr else "⚔️ Fetching Albion Market Data..."):
    raw_api_data = get_data_sync(all_item_ids, refining_city)

if not raw_api_data:
    st.error("⚠️ Albion API'sinden fiyatlar alınamadı! Şehri veya filtreleri değiştirip tekrar deneyin." if is_tr else "⚠️ Failed to fetch prices from Albion API!")
    st.stop()

# Fiyat veritabanını DataFrame'e basıp filtrele
df = pd.DataFrame(raw_api_data)
df['age'] = df['sell_price_min_date'].apply(calc_age)

# Şehre göre en güncel, sıfır olmayan fiyat eşleşmelerini çıkar (Eğer sıfırsa bayatlıktan eleriz)
df = df[(df['city'] == refining_city) & (df['sell_price_min'] > 0) & (df['age'] <= max_data_age)]

# Hızlı erişim için sözlük oluştur
price_dict = {}
age_dict = {}
for _, row in df.iterrows():
    price_dict[row['item_id']] = row['sell_price_min']
    age_dict[row['item_id']] = row['age']

# --- RAFİNASYON HESAPLAMA MOTORU (MATEMATİKSEL MÜKEMMELLİK) ---
calculated_data = []

for c in combos:
    tier = c["tier"]
    enc = c["enchant"] if c["enchant"] else ".0"
    formula = TIER_FORMULAS[tier]
    
    raw_p = price_dict.get(c["raw_id"], 0)
    ref_p = price_dict.get(c["ref_id"], 0)
    prev_p = price_dict.get(c["prev_id"], 0)
    
    # Tüm verileri mevcut olmayanları listeye alma
    if raw_p == 0 or ref_p == 0 or prev_p == 0:
        continue
        
    # Gecikme süreleri (Hangisi en eskiyse onu baz alırız)
    data_age = max(age_dict.get(c["raw_id"], 0), age_dict.get(c["ref_id"], 0), age_dict.get(c["prev_id"], 0))
    
    # 🌟 Matematiksel Geri Dönüşüm (Continuous Recycling) Formülü:
    # RRR (Geri Dönüşüm) sayesinde, her 1 adet işleme için gereken net hammadde (1 - RRR) kadar azalır!
    # Çünkü geri dönen malzemeler tekrar üretim döngüsüne katılır.
    rrr_factor = 1 - (rrr_value / 100)
    
    raw_qty_needed = formula["raw_qty"] * rrr_factor
    prev_qty_needed = formula["prev_qty"] * rrr_factor
    
    # Gümüş olarak maliyet
    maliyet = (raw_qty_needed * raw_p) + (prev_qty_needed * prev_p)
    gelir = ref_p * (1 - (market_tax / 100))
    
    net_kar = gelir - maliyet
    roi = (net_kar / maliyet) * 100 if maliyet > 0 else 0
    
    calculated_data.append({
        "Eşya Seviyesi": f"{tier}{enc}",
        "Ham Kaynak": c["raw_id"],
        "İşlenmiş Kaynak": c["ref_id"],
        "Malzeme": format_item_name(f"{tier}_{res_meta['raw']}{c['enchant']}"),
        "Ham Fiyat": raw_p,
        "Önceki Seviye Fiyat": prev_p,
        "İşlenmiş Fiyat": ref_p,
        "Efektif Maliyet": int(maliyet),
        "Net Kâr": int(net_kar),
        "Kâr Oranı (ROI)": roi,
        "En Son Güncelleme": f"{data_age} dk önce" if is_tr else f"{data_age}m ago",
        "raw_p_id": c["raw_id"],
        "ref_p_id": c["ref_id"],
        "prev_p_id": c["prev_id"]
    })

# --- ARAYÜZÜN OYUNCU MODUNA UYARLANMASI ---
def format_item_name(item_id):
    tier_part = item_id[:2]
    tier_str = tier_part.replace("T", "Seviye ") if is_tr else tier_part.replace("T", "Tier ")
    
    enchant = ""
    base_id = item_id[2:]
    if "@" in item_id:
        parts = item_id.split("@")
        base_id = parts[0][2:]
        enchant = f" .{parts[1]}"
    elif "_LEVEL" in item_id:
        parts = item_id.split("_LEVEL")
        base_id = parts[0][2:]
        enchant = f" .{parts[1]}"
        
    name_dict = ITEM_NAMES_TR if is_tr else ITEM_NAMES_EN
    item_name = name_dict.get(base_id, base_id)
    return f"{tier_str} {item_name}{enchant}"

# --- SEKMELİ ANALİZ GÖRÜNÜMÜ ---
tab1, tab2 = st.tabs(["📊 Tek Seviye Rafinasyon Analizi" if is_tr else "📊 Single Level Refining", "🛡️ Çoklu Seviye Karşılaştırması" if is_tr else "🛡️ Multi-Level Comparison"])

with tab1:
    if not calculated_data:
        st.warning("Seçtiğin şehir ve kriterler için geçerli/güncel fiyat verisi bulunamadı." if is_tr else "No valid/fresh price data found for selected criteria.")
    else:
        # Seviye seçici
        calculated_df = pd.DataFrame(calculated_data)
        selected_tier_name = st.selectbox("Detaylarını Görmek İstediğin Seviye (Tier):" if is_tr else "Select Tier for Deep Analysis:", calculated_df["Eşya Seviyesi"].unique())
        
        # Seçilen seviyenin detaylı kâr/maliyet kartı
        row = calculated_df[calculated_df["Eşya Seviyesi"] == selected_tier_name].iloc[0]
        
        # Oyun İçi İkonlar ve Büyük Görsel Kart
        st.markdown(f"### 🛡️ {row['Malzeme']} ({selected_tier_name}) Analizi")
        
        col_raw, col_prev, col_result = st.columns([3, 3, 4])
        
        with col_raw:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color:#B9935A; font-weight:bold;">🍀 Ham Kaynak (Raw Material)</p>
                <img src="{get_item_icon(row['raw_p_id'])}" width="64" style="margin-bottom:10px;">
                <p><b>Seviye Fiyatı:</b> {row['Ham Fiyat']:,} 🥈</p>
                <p><b>Gerekli Miktar:</b> {TIER_FORMULAS[selected_tier_name[:2]]['raw_qty']} adet (Geri Dönüşle Düşer)</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_prev:
            st.markdown(f"""
            <div class="metric-card">
                <p style="color:#B9935A; font-weight:bold;">🧱 Bir Önceki Seviye (Flat Refined)</p>
                <img src="{get_item_icon(row['prev_p_id'])}" width="64" style="margin-bottom:10px;">
                <p><b>Eşya Fiyatı:</b> {row['Önceki Seviye Fiyat']:,} 🥈</p>
                <p><b>Gerekli Miktar:</b> {TIER_FORMULAS[selected_tier_name[:2]]['prev_qty']} adet</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_result:
            kar_renk = "#10B981" if row["Net Kâr"] > 0 else "#EF4444"
            st.markdown(f"""
            <div class="metric-card" style="border: 2px solid #B9935A;">
                <p style="color:#B9935A; font-weight:bold; font-size:18px;">✨ Rafinasyon Sonucu (Refined Product)</p>
                <img src="{get_item_icon(row['ref_p_id'])}" width="64" style="margin-bottom:10px;">
                <p><b>Pazar Satış Fiyatı:</b> {row['İşlenmiş Fiyat']:,} 🥈</p>
                <p><b>Efektif Maliyet (Vergi Hariç):</b> {row['Efektif Maliyet']:,} 🥈</p>
                <p><b>Net Kâr:</b> <span style="color:{kar_renk}; font-size:22px; font-weight:bold;">{row['Net Kâr']:,} 🥈</span></p>
                <p><b>Yatırımın Getirisi (ROI):</b> <span style="color:{kar_renk}; font-weight:bold;">% {row['Kâr Oranı (ROI)']:.2f}</span></p>
                <p style="font-size:12px; color:#9CA3AF;">Veri Yaşı: {row['En Son Güncelleme']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    if not calculated_data:
        st.warning("Karşılaştırma yapabilmek için yeterli veri yok." if is_tr else "Not enough data for comparison.")
    else:
        # Tablo ve Görsel Grafik
        st.markdown("### 🏆 Tüm Seviyelerin Kârlılık Karşılaştırması")
        
        comp_df = pd.DataFrame(calculated_data)
        
        # Karşılaştırma Grafiği (M3 ve Bulut İçin Optimize Plotly)
        fig = px.bar(
            comp_df,
            x="Eşya Seviyesi",
            y="Net Kâr",
            color="Kâr Oranı (ROI)",
            hover_name="Malzeme",
            labels={"Eşya Seviyesi": "Seviye (Tier)", "Net Kâr": "Kâr (Gümüş) 🥈"},
            template="plotly_dark",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Karşılaştırma Detay Tablosu (Doğrudan Oyuna Özgü)
        display_comp = comp_df[['Eşya Seviyesi', 'Malzeme', 'Ham Fiyat', 'Önceki Seviye Fiyat', 'İşlenmiş Fiyat', 'Efektif Maliyet', 'Net Kâr', 'Kâr Oranı (ROI)', 'En Son Güncelleme']].copy()
        
        display_comp['Ham Fiyat'] = display_comp['Ham Fiyat'].apply(lambda x: f"{x:,} 🥈")
        display_comp['Önceki Seviye Fiyat'] = display_comp['Önceki Seviye Fiyat'].apply(lambda x: f"{x:,} 🥈")
        display_comp['İşlenmiş Fiyat'] = display_comp['İşlenmiş Fiyat'].apply(lambda x: f"{x:,} 🥈")
        display_comp['Efektif Maliyet'] = display_comp['Efektif Maliyet'].apply(lambda x: f"{x:,} 🥈")
        display_comp['Net Kâr'] = display_comp['Net Kâr'].apply(lambda x: f"{x:,} 🥈")
        display_comp['Kâr Oranı (ROI)'] = display_comp['Kâr Oranı (ROI)'].round(2)
        
        if is_tr:
            display_comp.columns = ['Seviye', 'Eşya', 'Ham Fiyat', 'Önceki Seviye Fiyat', 'İşlenmiş Fiyat', 'Maliyet', 'Net Kâr', 'Kâr Oranı (ROI) %', 'Güncelleme']
        else:
            display_comp.columns = ['Tier', 'Item', 'Raw Price', 'Prev Tier Price', 'Refined Price', 'Cost', 'Net Profit', 'ROI %', 'Delay']
            
        st.dataframe(
            display_comp, 
            use_container_width=True, 
            hide_index=True,
            column_config={display_comp.columns[7]: st.column_config.NumberColumn(format="%.2f%%")}
        )
