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
if "user_key" not in st.session_state:
    st.session_state.user_key = None
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
    st.session_state.inventory_db = []

# Bellek İçi Finansal İşlemler Listesi
if "transactions_db" not in st.session_state:
    st.session_state.transactions_db = []

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ VINEX BİLİŞİM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D4AF37;'>Kurumsal Depo & Ön Muhasebe Yönetim Sistemi</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Kullanıcı Girişi")
            username_input = st.text_input("Kullanıcı Adı (Telefon veya E-posta)", value="05401400071")
            password_input = st.text_input("Şifre", type="password", value="admin123")
            submit = st.form_submit_button("Güvenli Giriş Yap")
            
            if submit:
                user_info = st.session_state.users_db.get(username_input)
                if user_info and user_info["password"] == password_input:
                    if user_info["status"] != "Aktif":
                        st.error("Bu hesap pasif durumdadır. Yöneticinizle iletişime geçin.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_key = username_input
                        st.session_state.user = user_info["name"]
                        st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                        st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    st.stop()

# --- ANA UYGULAMA PANELİ ---
current_user_data = st.session_state.users_db.get(st.session_state.user_key, {})
st.sidebar.markdown(f"### 👤 {st.session_state.user}")
st.sidebar.markdown(f"<span style='color: #D4AF37;'>Rol: {current_user_data.get('role', 'Kullanıcı')}</span>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasyon", [
    "📊 Genel Bakış", 
    "📦 Gelişmiş Depo & Stok Yönetimi", 
    "💰 Ön Muhasebe & Kasa İşlemleri", 
    "👥 Personel & Yetki Yönetimi", 
    "🔑 Şifre & Profil Ayarları",
    "🔒 SMS & Güvenlik (OTP)"
])

# --- 1. GENEL BAKIŞ ---
if menu == "📊 Genel Bakış":
    st.title("📊 Vinex Bilişim - Yönetim Paneli")
    st.markdown("---")
    
    # Kritik stok kontrolü
    critical_items = [item for item in st.session_state.inventory_db if item["Adet"] <= item["Kritik Sınır"]]
    if critical_items:
        st.warning(f"⚠️ **Dikkat:** Toplam {len(critical_items)} kalem ürün kritik stok sınırında veya tükenmek üzere!")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kayıtlı Ürün Çeşidi", f"{len(st.session_state.inventory_db)} Kalem")
    col2.metric("Kasa İşlem Kaydı", f"{len(st.session_state.transactions_db)} Adet")
    col3.metric("Kayıtlı Personel", f"{len(st.session_state.users_db)} Kişi")
    col4.metric("Kritik Stok Uyarı", f"{len(critical_items)} Ürün", delta_color="inverse")

# --- 2. GELİŞMİŞ DEPO & STOK YÖNETİMİ ---
elif menu == "📦 Gelişmiş Depo & Stok Yönetimi":
    st.title("📦 Gelişmiş Envanter & Stok Yönetimi")
    st.markdown("---")
    
    tab_list, tab_add = st.tabs(["🔍 Envanter Arama & Filtreleme", "➕ Yeni Ürün Ekle"])
    
    with tab_list:
        if not st.session_state.inventory_db:
            st.info("Henüz sisteme eklenmiş bir ürün bulunmuyor. 'Yeni Ürün Ekle' sekmesinden ürün ekleyebilirsiniz.")
        else:
            col_search, col_f_depot, col_f_cat = st.columns([2, 1, 1])
            with col_search:
                search_query = st.text_input("🔎 Ürün Adı, Barkod veya Açıklamada Ara", "")
            with col_f_depot:
                all_depots = list(set([item["Depo"] for item in st.session_state.inventory_db]))
                filter_depot = st.selectbox("Depo Filtresi", ["Tüm Depolar"] + all_depots)
            with col_f_cat:
                all_cats = list(set([item["Kategori"] for item in st.session_state.inventory_db]))
                filter_cat = st.selectbox("Kategori Filtresi", ["Tüm Kategoriler"] + all_cats)
            
            # Filtreleme Mantığı
            filtered_inv = st.session_state.inventory_db
            if search_query:
                filtered_inv = [
                    item for item in filtered_inv 
                    if search_query.lower() in item["Ürün Adı"].lower() 
                    or search_query.lower() in item["Barkod"].lower()
                    or search_query.lower() in item["Açıklama"].lower()
                ]
            if filter_depot != "Tüm Depolar":
                filtered_inv = [item for item in filtered_inv if item["Depo"] == filter_depot]
            if filter_cat != "Tüm Kategoriler":
                filtered_inv = [item for item in filtered_inv if item["Kategori"] == filter_cat]
                
            st.dataframe(pd.DataFrame(filtered_inv), use_container_width=True)
            
    with tab_add:
        st.subheader("➕ Sıfırdan Yeni Ürün Kaydı")
        with st.form("add_new_custom_product"):
            col_a, col_b = st.columns(2)
            with col_a:
                p_barcode = st.text_input("Barkod Numarası", f"VNX-{random.randint(1000, 9999)}")
                p_name = st.text_input("Ürün / Model Adı *")
                p_depot = st.selectbox("Depo Lokasyonu", ["Ankara Merkez", "Çankaya Şube", "Ulus Tedarik"])
                p_cat = st.text_input("Kategori", "Teknoloji / Aksesuar")
            with col_b:
                p_qty = st.number_input("Stok Adedi", min_value=1, value=10)
                p_crit = st.number_input("Kritik Uyarı Sınırı", min_value=1, value=2)
                p_price = st.number_input("Birim Satış Fiyatı (₺)", min_value=0.0, step=10.0, value=100.0)
                p_desc = st.text_area("Açıklama / Notlar", "")
                
            if st.form_submit_button("Ürünü Envantere Kaydet"):
                if p_name:
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
                    st.success(f"'{p_name}' başarıyla depoya eklendi!")
                    st.rerun()
                else:
                    st.error("Lütfen Ürün Adı alanını doldurun!")

# --- 3. ÖN MUHASEBE & KASA İŞLEMLERİ ---
elif menu == "💰 Ön Muhasebe & Kasa İşlemleri":
    st.title("💰 Ön Muhasebe & Kasa Yönetimi")
    st.markdown("---")
    
    tab_trans_list, tab_trans_add = st.tabs(["📊 Kasa Hareketleri & Filtreleme", "➕ Yeni Kasa / Satış Kaydı"])
    
    with tab_trans_list:
        if not st.session_state.transactions_db:
            st.info("Henüz kaydedilmiş bir kasa hareketi bulunmuyor.")
        else:
            col_f_type, col_f_pay = st.columns(2)
            with col_f_type:
                f_type = st.selectbox("İşlem Türü Filtresi", ["Tüm İşlemler", "Gelir (Satış)", "Gider (Maliyet)"])
            with col_f_pay:
                f_pay = st.selectbox("Ödeme Yöntemi Filtresi", ["Tüm Yöntemler", "Nakit", "Kredi Kartı", "Havale / EFT", "Açık Hesap"])
                
            filtered_trans = st.session_state.transactions_db
            if f_type != "Tüm İşlemler":
                filtered_trans = [t for t in filtered_trans if t["Tür"] == f_type]
            if f_pay != "Tüm Yöntemler":
                filtered_trans = [t for t in filtered_trans if t["Ödeme Yöntemi"] == f_pay]
                
            st.dataframe(pd.DataFrame(filtered_trans), use_container_width=True)
            
    with tab_trans_add:
        st.subheader("➕ Gelir / Gider İşlemi Kaydet")
        with st.form("add_transaction_form"):
            t_type = st.selectbox("İşlem Türü", ["Gelir (Satış)", "Gider (Maliyet)"])
            t_cat = st.selectbox("İşlem Kategorisi", [
                "Cihaz Satışı", "Özel Koleksiyon (Tesbih/Epoksi)", "Aksesuar Satışı", 
                "Kira & Fatura", "Lojistik / Kargo", "Maaş & Personel", "Diğer Harcamalar"
            ])
            
            product_options = [item["Ürün Adı"] for item in st.session_state.inventory_db]
            selected_product = st.selectbox("Satışı Yapılan Ürün (Stoktan Otomatik Düşer)", ["Ürün Seçiniz (Opsiyonel)"] + product_options)
            sale_qty = st.number_input("Satış / Düşülecek Adet", min_value=1, value=1)
            
            t_method = st.selectbox("Ödeme Yöntemi", ["Nakit", "Kredi Kartı", "Havale / EFT", "Açık Hesap"])
            t_amount = st.number_input("Toplam Tutar (₺)", min_value=0.0, step=50.0, value=500.0)
            t_desc = st.text_area("İşlem Açıklaması", "")
            
            if st.form_submit_button("Kasaya İşle"):
                st.session_state.transactions_db.append({
                    "Tür": t_type,
                    "Kategori": t_cat,
                    "Ödeme Yöntemi": t_method,
                    "Tutar (₺)": t_amount,
                    "Açıklama": f"{selected_product} ({sale_qty} Adet) - {t_desc}" if selected_product != "Ürün Seçiniz (Opsiyonel)" else t_desc
                })
                
                if selected_product != "Ürün Seçiniz (Opsiyonel)":
                    for item in st.session_state.inventory_db:
                        if item["Ürün Adı"] == selected_product:
                            if item["Adet"] >= sale_qty:
                                item["Adet"] -= sale_qty
                            else:
                                st.warning("Uyarı: Depodaki stok adedi düşülecek miktardan az!")
                
                st.success("İşlem kasaya kaydedildi!")
                st.rerun()

# --- 4. PERSONEL & YETKİ YÖNETİMİ ---
elif menu == "👥 Personel & Yetki Yönetimi":
    st.title("👥 Personel & Kullanıcı Yönetimi")
    st.markdown("---")
    
    col_u_list, col_u_add = st.columns([3, 2])
    
    with col_u_list:
        st.subheader("Sistemdeki Yetkili Kullanıcılar")
        user_table_data = [
            {
                "Telefon / Kullanıcı": k,
                "Ad Soyad": v["name"],
                "Departman": v["department"],
                "Rol": v["role"],
                "Durum": v["status"]
            }
            for k, v in st.session_state.users_db.items()
        ]
        st.dataframe(pd.DataFrame(user_table_data), use_container_width=True)
        
    with col_u_add:
        st.subheader("➕ Yeni Personel Tanımla")
        with st.form("create_user_form"):
            u_phone = st.text_input("Telefon Numarası (Giriş Adı) *")
            u_name = st.text_input("Ad Soyad *")
            u_email = st.text_input("E-posta")
            u_dept = st.selectbox("Departman", ["Yönetim", "Depo & Lojistik", "Ön Muhasebe", "Satış & Mağaza"])
            u_role = st.selectbox("Yetki Rolü", ["Yönetici", "Depo Sorumlusu", "Muhasebe Yetkilisi", "Satış Danışmanı"])
            u_pass = st.text_input("Başlangıç Şifresi *", type="password")
            
            if st.form_submit_button("Personeli Kaydet"):
                if u_phone and u_name and u_pass:
                    st.session_state.users_db[u_phone] = {
                        "password": u_pass,
                        "role": u_role,
                        "department": u_dept,
                        "email": u_email,
                        "name": u_name,
                        "status": "Aktif"
                    }
                    st.success(f"'{u_name}' sisteme eklendi!")
                    st.rerun()
                else:
                    st.error("Lütfen zorunlu (*) alanları doldurun!")

# --- 5. ŞİFRE & PROFİL AYARLARI ---
elif menu == "🔑 Şifre & Profil Ayarları":
    st.title("🔑 Şifre & Profil Yönetim Merkezi")
    st.markdown("---")
    
    col_my_pass, col_admin_pass = st.columns(2)
    
    with col_my_pass:
        st.subheader("👤 Kendi Şifrenizi Değiştirin")
        with st.form("change_my_password_form"):
            current_pass = st.text_input("Mevcut Şifreniz", type="password")
            new_pass = st.text_input("Yeni Şifreniz", type="password")
            confirm_pass = st.text_input("Yeni Şifreniz (Tekrar)", type="password")
            
            if st.form_submit_button("Şifremi Güncelle"):
                user_record = st.session_state.users_db.get(st.session_state.user_key)
                if user_record and user_record["password"] == current_pass:
                    if new_pass and new_pass == confirm_pass:
                        user_record["password"] = new_pass
                        st.success("🎉 Şifreniz başarıyla güncellendi!")
                    else:
                        st.error("Yeni şifreler eşleşmiyor veya boş!")
                else:
                    st.error("Mevcut şifrenizi hatalı girdiniz!")
                    
    with col_admin_pass:
        if current_user_data.get("role") == "Genel Yönetici":
            st.subheader("🛡️ Başka Bir Kullanıcının Şifresini Sıfırla")
            with st.form("reset_user_password_form"):
                target_user = st.selectbox("Kullanıcı Seçin", list(st.session_state.users_db.keys()))
                target_new_pass = st.text_input("Atanacak Yeni Şifre", type="password")
                
                if st.form_submit_button("Kullanıcı Şifresini Güncelle"):
                    if target_new_pass:
                        st.session_state.users_db[target_user]["password"] = target_new_pass
                        st.success(f"'{target_user}' kullanıcısının şifresi güncellendi!")
                    else:
                        st.error("Lütfen geçerli bir yeni şifre girin!")

# --- 6. SMS & GÜVENLİK (OTP) ---
elif menu == "🔒 SMS & Güvenlik (OTP)":
    st.title("🔒 SMS OTP Doğrulama Merkezi")
    st.info("Kayıtlı Yönetici Telefonu: **05401400071**")
    
    if st.button("📲 Telefonuma SMS OTP Kodu Gönder"):
        st.session_state.otp_code = str(random.randint(100000, 999999))
        st.session_state.otp_verified = False
        st.success(f"SMS iletildi! OTP Kodunuz: **{st.session_state.otp_code}**")
        
    if st.session_state.otp_code:
        with st.form("otp_verify_form"):
            entered_code = st.text_input("6 Haneli Kodu Girin", max_chars=6)
            if st.form_submit_button("Doğrula"):
                if entered_code == st.session_state.otp_code:
                    st.session_state.otp_verified = True
                    st.success("🎉 OTP Doğrulaması Başarılı!")
                else:
                    st.error("Hatalı kod!")
                    
