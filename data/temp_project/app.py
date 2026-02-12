import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Kendi modüllerimiz
from core.services import TransactionService
from core.ai_advisor import AIAdvisor

# Sayfa Ayarları (Wide layout kullanıyoruz ki yan yana sığsın)
st.set_page_config(page_title="SmartBudget AI", page_icon="💰", layout="wide")

# AI Modelini Cache'le
@st.cache_resource
def load_ai_advisor():
    return AIAdvisor(model_filename="qwen2.5-1.5b-instruct-q4_k_m.gguf")

service = TransactionService()

# --- SIDEBAR: EKLEME FORMU ---
with st.sidebar:
    st.header("➕ İşlem Ekle")
    with st.form("entry_form", clear_on_submit=True):
        tx_type = st.selectbox("Tür", ["Gider", "Gelir"])
        categories = ["Kira", "Market", "Fatura", "Ulaşım", "Giyim", "Sağlık", "Eğlence", "Maaş", "Diğer"]
        category = st.selectbox("Kategori", categories)
        amount = st.number_input("Tutar (TL)", min_value=0.0, step=10.0, format="%.2f")
        description = st.text_area("Açıklama")
        
        if st.form_submit_button("Kaydet ✅"):
            if amount > 0:
                service.add_entry(tx_type, category, amount, description)
                st.success("Kaydedildi!")
                st.rerun()
            else:
                st.error("Tutar 0'dan büyük olmalı.")

st.title("💰 SmartBudget: Finansal Yönetim Paneli")
st.markdown("---")

# ==========================================
# BÖLÜM 1: BU AYIN İSTATİSTİKLERİ (EN ÜSTTE)
# ==========================================
st.header(f"📅 Bu Ayın Genel Bakışı ({datetime.now().strftime('%B %Y')})")

# Ekranı ikiye bölüyoruz: Sol (Tablo) - Sağ (Pasta Grafik)
col_month_1, col_month_2 = st.columns([3, 2]) # Sol taraf biraz daha geniş

# --- SOL: İŞLEM TABLOSU ---
with col_month_1:
    st.subheader("📝 İşlem Listesi")
    current_month_df = service.get_current_month_data()

    if not current_month_df.empty:
        # Tarih formatı
        current_month_df['date'] = current_month_df['date'].dt.strftime('%Y-%m-%d')
        
        # TIKLANABİLİR TABLO
        event = st.dataframe(
            current_month_df,
            use_container_width=True,
            hide_index=False,
            on_select="rerun",
            selection_mode="single-row"
        )

        # SİLME İŞLEMİ
        if len(event.selection.rows) > 0:
            selected_row_index = event.selection.rows[0]
            real_index = current_month_df.index[selected_row_index]
            
            st.warning(f"Seçili Kayıt ID: {real_index}")
            if st.button("🗑️ Seçili Kaydı SİL", type="primary"):
                if service.delete_entry(real_index):
                    st.success("Silindi!")
                    st.rerun()
                else:
                    st.error("Hata oluştu.")
    else:
        st.info("Bu ay henüz işlem yok.")

# --- SAĞ: AYLIK HARCAMA DAĞILIMI (PASTA GRAFİK) ---
with col_month_2:
    st.subheader("🍰 Harcama Dağılımı")
    monthly_data = service.get_monthly_expenses(datetime.now().year, datetime.now().month)
    
    if not monthly_data.empty:
        fig, ax = plt.subplots(figsize=(4, 4))
        # Pasta grafiği çizimi
        wedges, texts, autotexts = ax.pie(
            monthly_data, 
            labels=monthly_data.index, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'color': "white", 'fontsize': 10}
        )
        ax.axis('equal') # Daire şeklini koru
        # Arka planı şeffaf yap (Streamlit temasına uysun)
        fig.patch.set_alpha(0)
        st.pyplot(fig)
    else:
        st.info("Bu ay gider kaydı bulunamadı.")

st.markdown("---")

# ==========================================
# BÖLÜM 2: YILLIK VE GENEL İSTATİSTİKLER
# ==========================================
st.header("📈 Yıllık ve Genel Durum")

# 1. KPI KARTLARI (ÖZET)
summary = service.get_summary()
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Toplam Gelir", f"{summary['total_income']:,.2f} ₺")
kpi2.metric("Toplam Gider", f"{summary['total_expense']:,.2f} ₺")
kpi3.metric("Net Bakiye", f"{summary['balance']:,.2f} ₺", delta=summary['balance'])
kpi4.metric("En Çok Harcanan", summary['top_expense_category'])

st.write("") # Boşluk

# 2. YILLIK TREND (SÜTUN GRAFİK - HISTOGRAM)
st.subheader("📊 Yıllık Gelir/Gider Trendi")

# Yıl seçimi için küçük bir alan
sel_year_trend = st.number_input("Analiz Yılı", 2020, 2030, datetime.now().year)
yearly_data = service.get_yearly_trend(sel_year_trend)

if not yearly_data.empty:
    # Renk hatasını önleyen blok
    for col in ["Gelir", "Gider"]:
        if col not in yearly_data.columns:
            yearly_data[col] = 0
    yearly_data = yearly_data[["Gelir", "Gider"]]

    # Grafik
    st.bar_chart(yearly_data, color=["#00CC96", "#FF4B4B"]) # Gelir: Yeşil, Gider: Kırmızı
else:
    st.info(f"{sel_year_trend} yılı için veri bulunamadı.")

st.markdown("---")

# ==========================================
# BÖLÜM 3: YAPAY ZEKA ASİSTANI (GÜNCELLENDİ)
# ==========================================
st.subheader("🤖 AI Finans Danışmanı")
with st.expander("AI Analizini Başlatmak İçin Tıklayın", expanded=True):
    # Butonun hemen üstüne bir açıklama
    st.info("Yapay Zeka, bu ayki harcama kalemlerini (Market, Fatura vb.) inceleyerek yorum yapacak.")
    
    if st.button("Finansal Durumumu Yorumla ✨", type="secondary"):
        advisor = load_ai_advisor()
        if advisor:
            with st.spinner("bu ayki harcamalarınızı inceliyor..."):
                
                # 1. Bu ayın detaylarını çek
                monthly_details = service.get_monthly_category_breakdown()
                
                # 2. Modele gönder (Genel Özet + Aylık Detay)
                advice = advisor.ask_for_advice(summary, monthly_details)
            
            st.success("Tavsiye Hazır:")
            st.write(advice)
        else:
            st.error("Model yüklenemedi.")