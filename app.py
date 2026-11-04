import random
import streamlit as st
import pandas as pd

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

# --- OTURUM & BELLEK YÖNETİMİ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "otp_code" not in st.session_state:
    st.session_state.otp_code = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# Bellek İçi Kullanıcı Listesi
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "05401400071": {
            "password": "admin123", 
            "role": "Genel Yönetici", 
            "department": "Yönetim Kurulu",
            "email": "ahmetsalihbedir.ic@gmail.com", 
            "name": "Ahmet Salih Bedir",
            "status": "Aktif"
        }
    }

# Bellek İçi Depo & Ürün Listesi
if "inventory_db" not in st.session_state:
    st.session_state.inventory_db = [
        {
            "Barkod": "VNX-1001",
            "Ürün Adı": "iPhone 16 Pro Max 256GB",
            "Depo": "Çankaya Şube",
            "Kategori": "İkinci El Cihaz",
            "Adet": 12,
            "Kritik Sınır": 3,
            "Birim Fiyat (₺)": 78000.0,
            "Açıklama": "Kutulu, garantili cihaz"
        },
        {
            "Barkod": "VNX-1002",
            "Ürün Adı": "Özel Tasarım Oltu Taşı Tesbih",
            "Depo": "Ulus Tedarik",
            "Kategori": "Hanedan Koleksiyon",
            "Adet": 45,
            "Kritik Sınır": 5,
            "Birim Fiyat (₺)": 2500.0,
            "Açıklama": "Gümüş kazaz işçilikli"
        },
        {
            "Barkod": "VNX-1003",
            "Ürün Adı": "MagSafe Kablosuz Şarj Standı",
            "Depo": "Ankara Merkez",
            "Kategori": "Aksesuar",
            "Adet": 50,
            "Kritik Sınır": 5,
            "Birim Fiyat (₺)": 650.0,
            "Açıklama": "Hızlı şarj standı"
        }
    ]

# Bellek İçi Finansal İşlemler Listesi
if "transactions_db" not in st.session_state:
    st.session_state.transactions_db = [
        {
            "Tür": "Gelir (Satış)",
            "Kategori": "Cihaz Satışı",
            "Ödeme Yöntemi": "Kredi Kartı",
            "Tutar (₺)": 78000.0,
            "Açıklama": "iPhone 16 Pro Max satışı"
        },
        {
            "Tür": "Gider (Maliyet)",
            "Kategori": "Lojistik / Kargo",
            "Ödeme Yöntemi": "Nakit",
            "Tutar (₺)": 1250.0,
            "Açıklama": "Şubeler arası sevkiyat"
        }
    ]

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ VINEX BİLİŞİM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D4AF37;'>Çoklu Depo & Ön Muhasebe Yönetim Sistemi</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Yönetici Girişi")
            username_input = st.text_input("Kullanıcı Adı (Telefon veya E-posta)", value="05401400071")
            password_input = st.text_input("Şifre", type="password", value="admin123")
            submit = st.form_submit_button("Güvenli Giriş Yap")
            
            if submit:
                user_info = st.session_state.users_db.get(username_input)
                if user_info and user_info["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.user = user_info["name"]
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre! (Yönetici: 05401400071 / admin123)")
    st.stop()

# --- ANA UYGULAMA PANELİ ---
st.sidebar.markdown(f"### 👤 {st.session_state.user}")
st.sidebar.markdown("<span style='color: #D4AF37;'>● Sistem Aktif (Entegre Mod)</span>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasyon", ["📊 Genel Bakış", "📦 Çoklu Depo & Ürün Ekle", "👥 Kullanıcı Yönetimi", "💰 Ön Muhasebe & Kasa İşlemleri", "🔒 SMS & Güvenlik (OTP)"])

if menu == "📊 Genel Bakış":
    st.title("📊 Vinex Bilişim - Yönetim Paneli")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Depo", "3 Lokasyon", "Aktif")
    col2.metric("Kasadaki Nakit", "₺145,250", "+%12")
    col3.metric("Kayıtlı Personel", f"{len(st.session_state.users_db)} Kişi", "Yetkili")
    col4.metric("Kasa İşlem Kaydı", f"{len(st.session_state.transactions_db)} Adet", "Güncel")

elif menu == "📦 Çoklu Depo & Ürün Ekle":
    st.title("📦 Çoklu Depo & Envanter Yönetimi")
    
    col_tab, col_add = st.columns([2, 1])
    
    with col_tab:
        st.subheader("Mevcut Depo Envanteri")
        df_inv = pd.DataFrame(st.session_state.inventory_db)
        st.dataframe(df_inv, use_container_width=True)
        
    with col_add:
        st.subheader("➕ Yeni Ürün Ekle")
        with st.form("detailed_product_form"):
            p_barcode = st.text_input("Barkod Numarası", "VNX-1004")
            p_name = st.text_input("Ürün / Model Adı", "Örn: Galaxy Watch Ultra")
            p_depot = st.selectbox("Depo Lokasyonu", ["Ankara Merkez", "Çankaya Şube", "Ulus Tedarik"])
            p_cat = st.text_input("Kategori", "Aksesuar")
            p_qty = st.number_input("Stok Adedi", min_value=1, value=25)
            p_crit = st.number_input("Kritik Uyarı Sınırı", min_value=1, value=3)
            p_price = st.number_input("Birim Satış Fiyatı (₺)", min_value=1.0, value=12500.0)
            p_desc = st.text_area("Açıklama", "Ürün detayları...")
            
            if st.form_submit_button("Ürünü Kaydet"):
                st.session_state.inventory_db.append({
                    "Barkod": p_barcode,
                    "Ürün Adı": p_name,
                    "Depo": p_depot,
                    "Kategori": p_cat,
                    "Adet": p_qty,
                    "Kritik Sınır": p_crit,
                    "Birim Fiyat (₺)": p_price,
                    "Açıklama": p_desc
                })
                st.success("Ürün başarıyla depoya eklendi!")
                st.rerun()

elif menu == "👥 Kullanıcı Yönetimi":
    st.title("👥 Personel & Yetki Yönetim Merkezi")
    
    col_list, col_new = st.columns(2)
    
    with col_list:
        st.subheader("Sistemdeki Yetkili Personeller")
        user_list_data = [{"Kullanıcı / Tel": k, "Ad Soyad": v["name"], "Rol": v["role"], "Departman": v["department"]} for k, v in st.session_state.users_db.items()]
        st.dataframe(pd.DataFrame(user_list_data), use_container_width=True)
        
    with col_new:
        st.subheader("➕ Yeni Personel Tanımla")
        with st.form("detailed_user_form"):
            u_phone = st.text_input("Telefon Numarası")
            u_name = st.text_input("Ad Soyad")
            u_email = st.text_input("E-posta")
            u_dept = st.selectbox("Departman", ["Yönetim", "Depo", "Muhasebe", "Satış"])
            u_role = st.selectbox("Rol", ["Yönetici", "Depo Sorumlusu", "Muhasebeci"])
            u_pass = st.text_input("Şifre", type="password")
            
            if st.form_submit_button("Personeli Kaydet"):
                if u_phone and u_pass and u_name:
                    st.session_state.users_db[u_phone] = {
                        "password": u_pass,
                        "role": u_role,
                        "department": u_dept,
                        "email": u_email,
                        "name": u_name,
                        "status": "Aktif"
                    }
                    st.success("Personel başarıyla kaydedildi!")
                    st.rerun()
                else:
                    st.error("Zorunlu alanları doldurun!")

elif menu == "💰 Ön Muhasebe & Kasa İşlemleri":
    st.title("💰 Ön Muhasebe, Kasa ve Stok Entegrasyonlu Satış")
    st.markdown("---")
    
    col_form, col_table = st.columns([1, 2])
    
    with col_form:
        st.subheader("➕ Yeni İşlem & Satış Girişi")
        with st.form("integrated_finance_form"):
            t_type = st.selectbox("İşlem Türü", ["Gelir (Satış)", "Gider (Maliyet)"])
            t_cat = st.selectbox("İşlem Kategorisi", [
                "Cihaz Satışı", 
                "Özel Koleksiyon (Tesbih/Epoksi)", 
                "Aksesuar Satışı", 
                "Kira & Fatura", 
                "Lojistik / Kargo", 
                "Maaş & Personel", 
                "Diğer Harcamalar"
            ])
            
            # Eğer tür Gelir (Satış) ise depodaki ürünlerden seçim yaptırıp otomatik stok düşürelim
            product_options = [item["Ürün Adı"] for item in st.session_state.inventory_db]
            selected_product = st.selectbox("Satışı Yapılan Ürün (Stoktan Düşülecek)", ["Ürün Seçiniz (Opsiyonel)"] + product_options)
            sale_qty = st.number_input("Satış / Düşülecek Adet", min_value=1, value=1)
            
            t_method = st.selectbox("Ödeme Yöntemi", ["Nakit", "Kredi Kartı", "Havale / EFT", "Açık Hesap"])
            t_amount = st.number_input("Toplam Tutar (₺)", min_value=0.0, step=100.0, value=1500.0)
            t_desc = st.text_area("İşlem Açıklaması / Not", "Satış detayı...")
            
            if st.form_submit_button("Satışı Tamamla & Kasaya İşle"):
                # 1. Kasa işlemine kaydet
                st.session_state.transactions_db.append({
                    "Tür": t_type,
                    "Kategori": t_cat,
                    "Ödeme Yöntemi": t_method,
                    "Tutar (₺)": t_amount,
                    "Açıklama": f"{selected_product} ({sale_qty} Adet) - {t_desc}"
                })
                
                # 2. Eğer bir ürün seçildiyse ilgili depodaki stoktan otomatik düş
                stock_updated = False
                if selected_product != "Ürün Seçiniz (Opsiyonel)":
                    for item in st.session_state.inventory_db:
                        if item["Ürün Adı"] == selected_product:
                            if item["Adet"] >= sale_qty:
                                item["Adet"] -= sale_qty
                                stock_updated = True
                            else:
                                st.warning("Uyarı: Depodaki stok adedi düşülecek miktardan az!")
                
                st.success("🎉 Satış başarıyla kasaya işlendi ve stoktan otomatik düşüldü!")
                st.rerun()
                
    with col_table:
        st.subheader("📊 Kasa İşlem Hareketleri")
        df_trans = pd.DataFrame(st.session_state.transactions_db)
        st.dataframe(df_trans, use_container_width=True)
        
        st.markdown("### 📦 Güncel Depo Stok Durumu (Canlı Takip)")
        df_inv_live = pd.DataFrame(st.session_state.inventory_db)
        st.dataframe(df_inv_live, use_container_width=True)

elif menu == "🔒 SMS & Güvenlik (OTP)":
    st.title("🔒 SMS OTP Doğrulama Merkezi")
    st.write("Kritik yönetim işlemleriniz ve kasa transferleriniz için 2FA SMS doğrulama simülasyonu:")
    
    st.info("Kayıtlı Yönetici Telefonu: **05401400071**")
    
    if st.button("📲 Telefonuma SMS OTP Kodu Gönder"):
        st.session_state.otp_code = str(random.randint(100000, 999999))
        st.session_state.otp_verified = False
        st.success(f"SMS başarıyla iletildi! Simüle Edilen OTP Kodunuz: **{st.session_state.otp_code}**")
        
    if st.session_state.otp_code:
        with st.form("otp_verify_form"):
            entered_code = st.text_input("6 Haneli SMS Kodunu Girin", max_chars=6)
            verify_submit = st.form_submit_button("Kodu Doğrula")
            
            if verify_submit:
                if entered_code == st.session_state.otp_code:
                    st.session_state.otp_verified = True
                    st.success("🎉 OTP Doğrulaması Başarılı! Kritik işlem yetkisi onaylandı.")
                else:
                    st.error("Hatalı kod! Lütfen tekrar deneyin.")
                    
    if st.session_state.otp_verified:
        st.markdown("<span style='color: #00FF00; font-weight: bold;'>✔ Bu oturum için SMS Güvenlik Kilidi Açık</span>", unsafe_allow_html=True)
