import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enlil God Tier Refine", layout="wide", initial_sidebar_state="expanded")

# --- ANİMASYONLU OYUN ARAYÜZÜ (CSS KEYFRAMES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Inter:wght@400;600;700&display=swap');

    /* Ana Arka Plan */
    .stApp {
        background: radial-gradient(circle at top, #18202C 0%, #0B0E14 100%) !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Sol Panel */
    [data-testid="stSidebar"] {
        background-color: #11161F !important;
        border-right: 2px solid #4A3B23;
        box-shadow: 5px 0 15px rgba(0,0,0,0.6);
    }

    /* Parlayan ve Akan Altın Başlık Animasyonu */
    @keyframes goldShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    .animated-header {
        font-family: 'Cinzel', serif;
        text-align: center;
        padding: 18px;
        margin-bottom: 25px;
        background: linear-gradient(180deg, #1E2631 0%, #11161D 100%);
        border: 2px solid #8A6D3B;
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(185, 147, 90, 0.25), inset 0 0 15px rgba(0,0,0,0.8);
    }

    .animated-header h1 {
        font-size: 32px;
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
        font-size: 14px;
        letter-spacing: 1px;
    }

    /* Nefes Alan (Pulsing) Altın Çerçeve Animasyonu */
    @keyframes pulseGold {
        0% { box-shadow: 0 0 8px rgba(212, 175, 55, 0.3), inset 0 0 8px rgba(212, 175, 55, 0.15); border-color: #8A6D3B; }
        50% { box-shadow: 0 0 22px rgba(255, 215, 0, 0.75), inset 0 0 15px rgba(255, 215, 0, 0.3); border-color: #FFD700; }
        100% { box-shadow: 0 0 8px rgba(212, 175, 55, 0.3), inset 0 0 8px rgba(212, 175, 55, 0.15); border-color: #8A6D3B; }
    }

    /* Nefes Alan (Pulsing) Siber Mavi Çerçeve Animasyonu */
    @keyframes pulseBlue {
        0% { box-shadow: 0 0 8px rgba(56, 189, 248, 0.3), inset 0 0 8px rgba(56, 189, 248, 0.15); border-color: #0284C7; }
        50% { box-shadow: 0 0 22px rgba(56, 189, 248, 0.8), inset 0 0 15px rgba(56, 189, 248, 0.35); border-color: #38BDF8; }
        100% { box-shadow: 0 0 8px rgba(56, 189, 248, 0.3), inset 0 0 8px rgba(56, 189, 248, 0.15); border-color: #0284C7; }
    }

    /* Yüzen (Floating) İkon Animasyonu */
    @keyframes floatIcon {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
        100% { transform: translateY(0px); }
    }

    .god-card-gold {
        background: linear-gradient(135deg, #231D14 0%, #12151A 100%);
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 18px;
        animation: pulseGold 3s infinite ease-in-out;
        transition: transform 0.3s ease;
        margin-bottom: 15px;
    }

    .god-card-blue {
        background: linear-gradient(135deg, #10212B 0%, #12151A 100%);
        border: 2px solid #38BDF8;
        border-radius: 10px;
        padding: 18px;
        animation: pulseBlue 3s infinite ease-in-out;
        transition: transform 0.3s ease;
        margin-bottom: 15px;
    }

    .god-card-gold:hover, .god-card-blue:hover {
        transform: translateY(-4px) scale(1.01);
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

    /* Buton Animasyonu */
    .stButton>button {
        background: linear-gradient(135deg, #5C4728 0%, #2C2011 100%) !important;
        color: #F3E5AB !important;
        border: 1px solid #B9935A !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #8A6D3B 0%, #4A361D 100%) !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
        transform: scale(1.03);
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SOL PANEL VE DİL SEÇİMİ ---
lang = st.sidebar.radio("🌐 Dil / Language", ("Türkçe", "English"))
is_tr = (lang == "Türkçe")

# Animasyonlu Üst Banner
st.markdown(f"""
<div class="animated-header">
    <h1>ENLİL - GOD TIER REFINE SCANNER</h1>
    <p>{"Albion Online Canlı Rafinasyon & Geri Dönüşüm Hesaplayıcısı" if is_tr else "Albion Online Live Refining & Recycling Calculator"}</p>
</div>
""", unsafe_allow_html=True)

# --- KAYNAK SÖZLÜĞÜ ---
RESOURCES = {
    "Cevher (Ore -> Metal Bar)": {"raw": "ORE", "refined": "METALBAR", "tr": "Külçe", "en": "Metal Bar"},
    "Elyaf (Fiber -> Cloth)": {"raw": "FIBER", "refined": "CLOTH", "tr": "Kumaş", "en": "Cloth"},
    "Deri (Hide -> Leather)": {"raw": "HIDE", "refined": "LEATHER", "tr": "Deri", "en": "Leather"},
    "Odun (Wood -> Planks)": {"raw": "WOOD", "refined": "PLANKS", "tr": "Kalas", "en": "Planks"},
    "Taş (Stone -> Stone Block)": {"raw": "STONE", "refined": "STONEBLOCK", "tr": "Taş Blok", "en": "Stone Block"}
}

TIER_FORMULAS = {
    "T3": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T2"},
    "T4": {"raw_qty": 2, "prev_qty": 1, "prev_tier": "T3"},
    "T5": {"raw_qty": 3, "prev_qty": 1, "prev_tier": "T4"},
    "T6": {"raw_qty": 4, "prev_qty": 1, "prev_tier": "T5"},
    "T7": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T6"},
    "T8": {"raw_qty": 5, "prev_qty": 1, "prev_tier": "T7"},
}

ALL_LOCATIONS = ["Martlock", "Lymhurst", "Bridgewatch", "Thetford", "Fort Sterling", "Caerleon"]

# --- SOL MENÜ FİLTRELERİ ---
st.sidebar.header("⚙️ Filtreler & Ayar Menüsü" if is_tr else "⚙️ Filters & Settings")
selected_res_key = st.sidebar.selectbox("Kaynak Türü" if is_tr else "Resource Type", list(RESOURCES.keys()))
res_meta = RESOURCES[selected_res_key]

refining_city = st.sidebar.selectbox("Rafinasyon Şehri" if is_tr else "Refining City", ALL_LOCATIONS, index=0)
max_data_age = st.sidebar.slider("Maks. Veri Yaşı (Dk)" if is_tr else "Max Data Age (Mins)", 5, 1440, 240, 15)
market_tax = st.sidebar.slider("Pazar Vergisi (%)" if is_tr else "Market Tax (%)", 0.0, 10.0, 4.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("⚒️ Resource Return Rate (RRR)")
rrr_value = st.sidebar.slider("Geri Dönüş Oranı (RRR %)", 0.0, 60.0, 36.7, 0.1, help="Şehir bonusuyla %36.7, Focus ile %53.9")
batch_size = st.sidebar.number_input("Üretim Adedi (Simülasyon)" if is_tr else "Batch Size", min_value=1, value=300, step=50)

# --- ASENKRON VERİ MOTORU ---
BASE_URL = "https://www.albion-online-data.com/api/v2/stats/Prices"

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=12) as response:
            if response.status == 200:
                return await response.json()
    except:
        pass
    return []

async def fetch_refining_data(items, locs):
    chunk_size = 80
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

# --- ID HAVUZU OLUŞTURMA ---
combos = []
for tier in ["T3", "T4", "T5", "T6", "T7", "T8"]:
    enchants = [""] if tier == "T3" else ["", "_LEVEL1", "_LEVEL2", "_LEVEL3", "_LEVEL4"]
    for enc in enchants:
        combos.append({
            "tier": tier,
            "enchant": enc.replace("_LEVEL", "."),
            "raw_id": f"{tier}_{res_meta['raw']}{enc}",
            "ref_id": f"{tier}_{res_meta['refined']}{enc}",
            "prev_id": f"{TIER_FORMULAS[tier]['prev_tier']}_{res_meta['refined']}"
        })

all_item_ids = list(set([c["raw_id"] for c in combos] + [c["ref_id"] for c in combos] + [c["prev_id"] for c in combos]))

if st.sidebar.button("🔄 Verileri Şimdi Yenile" if is_tr else "🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()

with st.spinner("⚡ Enlil Motoru Pazar Verilerini Senkronize Ediyor..."):
    raw_api_data = get_data_sync(all_item_ids, refining_city)

if not raw_api_data:
    st.error("API'den veri alınamadı.")
    st.stop()

df = pd.DataFrame(raw_api_data)
df['age'] = df['sell_price_min_date'].apply(calc_age)
df = df[(df['city'] == refining_city) & (df['sell_price_min'] > 0) & (df['age'] <= max_data_age)]

price_dict = {row['item_id']: row['sell_price_min'] for _, row in df.iterrows()}
age_dict = {row['item_id']: row['age'] for _, row in df.iterrows()}

# --- HESAPLAMA ---
calculated_data = []
rrr_factor = 1 - (rrr_value / 100)

for c in combos:
    tier = c["tier"]
    enc = c["enchant"] if c["enchant"] else ".0"
    formula = TIER_FORMULAS[tier]
    
    raw_p = price_dict.get(c["raw_id"], 0)
    ref_p = price_dict.get(c["ref_id"], 0)
    prev_p = price_dict.get(c["prev_id"], 0)
    
    if raw_p == 0 or ref_p == 0 or prev_p == 0:
        continue
        
    data_age = max(age_dict.get(c["raw_id"], 0), age_dict.get(c["ref_id"], 0), age_dict.get(c["prev_id"], 0))
    
    cost = ((formula["raw_qty"] * rrr_factor) * raw_p) + ((formula["prev_qty"] * rrr_factor) * prev_p)
    revenue = ref_p * (1 - (market_tax / 100))
    net_profit = revenue - cost
    roi = (net_profit / cost) * 100 if cost > 0 else 0
    
    calculated_data.append({
        "Seviye": f"{tier}{enc}",
        "İkon": get_item_icon(c["ref_id"]),
        "Ham İkon": get_item_icon(c["raw_id"]),
        "Eşya": f"{tier}{enc} {res_meta['tr' if is_tr else 'en']}",
        "Ham Fiyat": int(raw_p),
        "Önceki Seviye": int(prev_p),
        "Satış Fiyatı": int(ref_p),
        "Maliyet": int(cost),
        "Birim Kâr": int(net_profit),
        "Toplam Kâr": int(net_profit * batch_size),
        "ROI": round(roi, 2),
        "Yaş (Dk)": data_age
    })

if not calculated_data:
    st.warning("Seçilen kriterlerde güncel fiyat eşleşmesi bulunamadı. Maksimum veri yaşını artırabilirsin.")
    st.stop()

calc_df = pd.DataFrame(calculated_data).sort_values(by="ROI", ascending=False)

# --- GÖRSELDEKİ İKİ SÜTUNLU DASHBOARD DÜZENİ ---
left_col, right_col = st.columns([5, 6])

with left_col:
    st.markdown("### 📋 Seviye Tablosu" if is_tr else "### 📋 Tier Breakdown")
    st.dataframe(
        calc_df[["İkon", "Seviye", "Eşya", "Maliyet", "Satış Fiyatı", "Birim Kâr", "ROI", "Yaş (Dk)"]],
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "İkon": st.column_config.ImageColumn("", width="small"),
            "ROI": st.column_config.NumberColumn("ROI %", format="%.2f %%"),
            "Birim Kâr": st.column_config.NumberColumn("Net Kâr 🥈", format="%d"),
            "Maliyet": st.column_config.NumberColumn("Maliyet 🥈", format="%d"),
            "Satış Fiyatı": st.column_config.NumberColumn("Satış 🥈", format="%d")
        }
    )

with right_col:
    st.markdown("### ⚡ God Tier Recycle & Fırsat Kartları" if is_tr else "### ⚡ God Tier Recycle Cards")
    
    # En yüksek ROI'li ilk 2 fırsatı parlayan animasyonlu kartlara basıyoruz
    top1 = calc_df.iloc[0]
    
    st.markdown(f"""
    <div class="god-card-gold">
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex; align-items:center; gap:15px;">
                <img src="{top1['Ham İkon']}" class="item-icon">
                <div style="text-align:center;">
                    <span style="color:#94A3B8; font-size:13px;">ROI ORANI</span><br>
                    <span style="color:#10B981; font-size:28px; font-weight:800;">%{top1['ROI']}</span><br>
                    <span style="color:#CBD5E1; font-size:12px;">Birim Kâr: {top1['Birim Kâr']:,} 🥈</span>
                </div>
                <img src="{top1['İkon']}" class="item-icon">
            </div>
            <div style="text-align:right; border-left:1px solid #4A3B23; padding-left:20px;">
                <span style="color:#FFD700; font-family:'Cinzel',serif; font-weight:800; font-size:16px;">👑 GOD TIER RECYCLE</span><br>
                <span style="color:#E2E8F0; font-size:14px;">{batch_size} Adet {top1['Seviye']} Üretimi:</span><br>
                <span style="color:#10B981; font-size:24px; font-weight:800;">+{top1['Toplam Kâr']:,} 🥈</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(calc_df) > 1:
        top2 = calc_df.iloc[1]
        st.markdown(f"""
        <div class="god-card-blue">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:15px;">
                    <img src="{top2['Ham İkon']}" class="item-icon">
                    <div style="text-align:center;">
                        <span style="color:#94A3B8; font-size:13px;">ROI ORANI</span><br>
                        <span style="color:#38BDF8; font-size:28px; font-weight:800;">%{top2['ROI']}</span><br>
                        <span style="color:#CBD5E1; font-size:12px;">Birim Kâr: {top2['Birim Kâr']:,} 🥈</span>
                    </div>
                    <img src="{top2['İkon']}" class="item-icon">
                </div>
                <div style="text-align:right; border-left:1px solid #0284C7; padding-left:20px;">
                    <span style="color:#38BDF8; font-family:'Cinzel',serif; font-weight:800; font-size:16px;">💎 RUNNER-UP TIER</span><br>
                    <span style="color:#E2E8F0; font-size:14px;">{batch_size} Adet {top2['Seviye']} Üretimi:</span><br>
                    <span style="color:#38BDF8; font-size:24px; font-weight:800;">+{top2['Toplam Kâr']:,} 🥈</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sağ Alttaki Dynamic Graph (Görseldeki Katmanlı Alan Grafiği)
    st.markdown("#### 📈 Dynamic Graph (Maliyet vs Satış Trendi)")
    plot_df = calc_df.sort_values(by="Seviye")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_df["Seviye"], y=plot_df["Satış Fiyatı"],
        mode='lines+markers', name='Satış Fiyatı',
        line=dict(color='#38BDF8', width=3),
        fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.18)'
    ))
    fig.add_trace(go.Scatter(
        x=plot_df["Seviye"], y=plot_df["Maliyet"],
        mode='lines+markers', name='Efektif Maliyet',
        line=dict(color='#D4AF37', width=3),
        fill='tozeroy', fillcolor='rgba(212, 175, 55, 0.22)'
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(18, 24, 31, 0.7)",
        plot_bgcolor="rgba(18, 24, 31, 0.4)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
