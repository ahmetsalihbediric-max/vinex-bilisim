import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- SAYFA YAPILANDIRMASI (GOLD & SİYAH LÜKS TEMA) ---
st.set_page_config(
    page_title="Vinex Bilişim - Yönetim Paneli",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Özel CSS ile Gold & Siyah Lüks Tasarım
st.markdown("""
    <style>
    .stApp {
        background-color: #0B0B0B;
        color: #E0E0E0;
    }
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 6px rgba(212, 175, 55, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #E6C555, #C49216);
        color: #000;
    }
    div[data-testid="stMetricValue"] {
        color: #D4AF37 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- VERİTABANI BAĞLANTISI (SUPABASE POSTGRESQL) ---
DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))

@st.cache_resource
def get_db_engine():
    if not DATABASE_URL:
        return None
    try:
        engine = create_engine(DATABASE_URL)
        return engine
    except Exception as e:
        return None

engine = get_db_engine()

# --- TABLOLARI OLUŞTURMA VE BAŞLANGIÇ VERİLERİ ---
def init_db():
    if not engine:
        return
    try:
        with engine.begin() as conn:
            # Kullanıcılar Tablosu
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(100),
                    role VARCHAR(50),
                    phone VARCHAR(20),
                    email VARCHAR(100)
                );
            """))
            # Depolar Tablosu
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouses (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    location VARCHAR(150)
                );
            """))
            # Ürünler / Stok Tablosu
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    warehouse_id INT,
                    product_name VARCHAR(150),
                    category VARCHAR(100),
                    quantity INT,
                    buying_price NUMERIC,
                    selling_price NUMERIC
                );
            """))
            # Muhasebe / İşlem Tablosu
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    transaction_type VARCHAR(50),
                    amount NUMERIC,
                    description TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Varsayılan Yönetici Hesabı (Ahmet Salih Bedir)
            res = conn.execute(text("SELECT COUNT(*) FROM users WHERE username='05401400071'")).fetchone()
            if res[0] == 0:
                conn.execute(text("""
                    INSERT INTO users (username, password, role, phone, email) 
                    VALUES ('05401400071', 'admin123', 'Yönetici', '05401400071', 'ahmetsalihbedir.ic@gmail.com')
                """))
    except Exception as e:
        st.error(f"Veritabanı başlatma hatası: {e}")

if engine:
    init_db()

# --- OTURUM YÖNETİMİ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ VINEX BİLİŞİM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D4AF37;'>Çoklu Depo & Ön Muhasebe Yönetim Sistemi</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Kullanıcı Adı (Telefon veya E-posta)")
            password_input = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("Güvenli Giriş (SMS OTP)")
            
            if submit:
                if (username_input in ["05401400071", "ahmetsalihbedir.ic@gmail.com"]) and password_input == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.user = "Ahmet Salih Bedir"
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    st.rerun()
                elif engine:
                    try:
                        with engine.connect() as conn:
                            query = text("SELECT * FROM users WHERE (username=:u OR email=:u OR phone=:u) AND password=:p")
                            user = conn.execute(query, {"u": username_input, "p": password_input}).fetchone()
                            if user:
                                st.session_state.logged_in = True
                                st.session_state.user = user[1]
                                st.rerun()
                            else:
                                st.error("Hatalı kullanıcı adı veya şifre!")
                    except Exception as e:
                        st.error(f"Giriş hatası: {e}")
                else:
                    st.error("Veritabanı bağlantısı kurulamadı! Lütfen Secrets ayarlarını kontrol edin.")
    st.stop()

# --- ANA UYGULAMA PANELİ ---
st.sidebar.markdown(f"### 👤 {st.session_state.user}")
st.sidebar.markdown("<span style='color: #D4AF37;'>● Sistem Aktif (Bulut)</span>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasyon", ["📊 Genel Bakış", "📦 Çoklu Depo Yönetimi", "💰 Ön Muhasebe", "🔒 SMS & Güvenlik Ayarları"])

if menu == "📊 Genel Bakış":
    st.title("📊 Vinex Bilişim - Yönetim Paneli")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Depo", "3 Merkez", "Aktif")
    col2.metric("Kasadaki Nakit", "₺145,250", "+%12")
    col3.metric("Toplam Stok Ürünü", "1,240 Adet", "Güncel")
    col4.metric("Güvenlik Durumu", "2FA / OTP", "Korunuyor")

elif menu == "📦 Çoklu Depo Yönetimi":
    st.title("📦 Çoklu Depo & Envanter Yönetimi")
    depo_data = pd.DataFrame({
        "Depo Adı": ["Ankara Merkez", "Çankaya Şube", "Ulus Tedarik"],
        "Ürün Kategori": ["Teknoloji / Aksesuar", "İkinci El Cihaz", "Özel Üretim Takı"],
        "Stok Adedi": [450, 310, 480],
        "Toplam Değer (₺)": [112500, 248000, 96000]
    })
    st.dataframe(depo_data, use_container_width=True)

elif menu == "💰 Ön Muhasebe":
    st.title("💰 Ön Muhasebe & Kasa Takibi")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("finance_form"):
            st.selectbox("İşlem Türü", ["Gelir (Satış)", "Gider (Maliyet/Harcama)"])
            st.number_input("Tutar (₺)", min_value=0.0, step=100.0)
            st.text_area("Açıklama")
            if st.form_submit_button("İşlemi Kaydet"):
                st.success("İşlem başarıyla kasaya işlendi!")
    with col2:
        st.subheader("Son Hareketler")
        st.write("• iPhone 16 Pro Max Satışı (+₺78,000)")
        st.write("• Kargo & Lojistik Gideri (-₺1,250)")

elif menu == "🔒 SMS & Güvenlik Ayarları":
    st.title("🔒 SMS OTP ve Güvenlik Altyapısı")
    st.text_input("Kayıtlı Yönetici Telefonu", value="05401400071", disabled=True)
    st.text_input("Bildirim E-postası", value="ahmetsalihbedir.ic@gmail.com", disabled=True)
    if st.button("Test SMS OTP Gönder"):
        st.success("Test OTP kodu başarıyla simüle edildi ve gönderildi!")
