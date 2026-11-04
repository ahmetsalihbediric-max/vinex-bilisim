import random
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Vinex Bilişim - Yönetim Paneli",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gold & Siyah Lüks Tasarım CSS
st.markdown("""
    <style>
    .stApp { background-color: #0B0B0B; color: #E0E0E0; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #AA7C11 100%);
        color: #000000; font-weight: bold; border: none; border-radius: 6px; padding: 0.5rem 1rem;
    }
    .stButton>button:hover { background: linear-gradient(135deg, #E6C555, #C49216); color: #000; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
""", unsafe_allow_html=True)

# --- SUPABASE BAĞLANTISI ---
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.warning("⚠️ Supabase API bilgileri bulunamadı. Lütfen Streamlit Secrets alanını kontrol edin.")
        return None
    return create_client(url, key)

supabase = init_supabase()

# --- OTURUM YÖNETİMİ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_key" not in st.session_state:
    st.session_state.user_key = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🛡️ VINEX BİLİŞİM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #D4AF37;'>Supabase PostgreSQL Entegre ERP Yönetim Paneli</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Kullanıcı Girişi")
            u_input = st.text_input("Kullanıcı Adı (Telefon)", value="05401400071")
            p_input = st.text_input("Şifre", type="password", value="admin123")
            submit = st.form_submit_button("Güvenli Giriş Yap")
            
            if submit:
                if supabase:
                    res = supabase.table("users").select("*").eq("phone", u_input).eq("password", p_input).execute()
                    if res.data:
                        user_data = res.data[0]
                        if user_data.get("status") != "Aktif":
                            st.error("Bu hesap pasif durumdadır.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user_key = u_input
                            st.session_state.user_name = user_data["name"]
                            st.session_state.user_role = user_data["role"]
                            st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                            st.rerun()
                    else:
                        st.error("Hatalı kullanıcı adı veya şifre!")
                else:
                    # Yedek / Simülasyon Girişi
                    if u_input == "05401400071" and p_input == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.user_key = u_input
                        st.session_state.user_name = "Ahmet Salih Bedir"
                        st.session_state.user_role = "Genel Yönetici"
                        st.rerun()
    st.stop()

# --- ANA UYGULAMA PANELİ ---
st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
st.sidebar.markdown(f"<span style='color: #D4AF37;'>Rol: {st.session_state.user_role}</span>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigasyon", [
    "📊 Genel Bakış", 
    "⚡ Hızlı Satış (POS)",
    "📦 Depo & Ürün Yönetimi", 
    "🤝 Cari Hesaplar",
    "💰 Ön Muhasebe & Kasa", 
    "🔑 Şifre & Profil"
])

# Veri Çekme Yardımcı Fonksiyonları
def fetch_inventory():
    if supabase:
        res = supabase.table("inventory").select("*").execute()
        return res.data
    return []

def fetch_transactions():
    if supabase:
        res = supabase.table("transactions").select("*").order("created_at", desc=True).execute()
        return res.data
    return []

# --- 1. GENEL BAKIŞ ---
if menu == "📊 Genel Bakış":
    st.title("📊 Vinex Bilişim - Yönetim Paneli")
    st.markdown("---")
    
    inv_data = fetch_inventory()
    trx_data = fetch_transactions()
    
    total_income = sum([t["amount"] for t in trx_data if "Gelir" in t["type"]]) if trx_data else 0.0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Canlı Ciro", f"₺{total_income:,.2f}")
    col2.metric("Stok Çeşidi", f"{len(inv_data)} Kalem")
    col3.metric("Kasa İşlem Kaydı", f"{len(trx_data)} Adet")
    col4.metric("Veritabanı Durumu", "Supabase Bağlı" if supabase else "Çevrimdışı")

# --- 2. HIZLI SATIŞ (POS) ---
elif menu == "⚡ Hızlı Satış (POS)":
    st.title("⚡ Hızlı Satış & Kasa POS Ekranı")
    st.markdown("---")
    
    inv_data = fetch_inventory()
    if not inv_data:
        st.warning("POS ekranında satış yapabilmek için veritabanında kayıtlı ürün olmalıdır.")
    else:
        with st.form("pos_form_db"):
            prod_options = [f"{item['product_name']} (Stok: {item['qty']} | ₺{item['unit_price']})" for item in inv_data]
            sel_prod = st.selectbox("Ürün Seçin", prod_options)
            sale_qty = st.number_input("Satış Adedi", min_value=1, value=1)
            pay_method = st.selectbox("Ödeme Yöntemi", ["Nakit", "Kredi Kartı", "Havale / EFT"])
            cust_name = st.text_input("Müşteri / Cari Adı", "Perakende Müşteri")
            
            if st.form_submit_button("💳 Satışı Tamamla ve Veritabanına İşle"):
                sel_idx = prod_options.index(sel_prod)
                target = inv_data[sel_idx]
                
                if target["qty"] >= sale_qty:
                    total_amount = float(target["unit_price"]) * sale_qty
                    new_qty = target["qty"] - sale_qty
                    
                    if supabase:
                        # 1. Stok Miktarını Güncelle
                        supabase.table("inventory").update({"qty": new_qty}).eq("id", target["id"]).execute()
                        
                        # 2. Kasaya Gelir Kaydı Ekle
                        supabase.table("transactions").insert({
                            "type": "Gelir (Satış)",
                            "category": "POS Satışı",
                            "payment_method": pay_method,
                            "amount": total_amount,
                            "description": f"Cari: {cust_name} | {target['product_name']} ({sale_qty} Adet)"
                        }).execute()
                        
                        st.success(f"🎉 Satış Başarılı! ₺{total_amount:,.2f} kasaya işlendi ve PostgreSQL veritabanında güncellendi.")
                        st.rerun()
                else:
                    st.error("Depoda yeterli stok bulunmuyor!")

# --- 3. DEPO & ÜRÜN YÖNETİMİ ---
elif menu == "📦 Depo & Ürün Yönetimi":
    st.title("📦 Depo & Envanter Yönetimi (Supabase Live)")
    st.markdown("---")
    
    tab_list, tab_add = st.tabs(["📋 Canlı Envanter Listesi", "➕ Yeni Ürün Kaydet"])
    
    with tab_list:
        inv = fetch_inventory()
        if inv:
            st.dataframe(pd.DataFrame(inv), use_container_width=True)
        else:
            st.info("Henüz ürün kaydı bulunmuyor.")
            
    with tab_add:
        with st.form("add_prod_db"):
            p_bc = st.text_input("Barkod", f"VNX-{random.randint(1000,9999)}")
            p_name = st.text_input("Ürün Adı *")
            p_dep = st.selectbox("Depo", ["Ankara Merkez", "Çankaya Şube", "Ulus Tedarik"])
            p_cat = st.text_input("Kategori", "Teknoloji")
            p_qty = st.number_input("Stok Adedi", min_value=1, value=10)
            p_price = st.number_input("Birim Fiyat (₺)", min_value=0.0, value=500.0)
            
            if st.form_submit_button("Ürünü Supabase'e Kaydet"):
                if p_name and supabase:
                    supabase.table("inventory").insert({
                        "barcode": p_bc,
                        "product_name": p_name,
                        "depot": p_dep,
                        "category": p_cat,
                        "qty": p_qty,
                        "unit_price": p_price
                    }).execute()
                    st.success(f"'{p_name}' kalıcı veritabanına eklendi!")
                    st.rerun()

# --- 4. CARİ HESAPLAR ---
elif menu == "🤝 Cari Hesaplar":
    st.title("🤝 Cari Hesap Yönetimi")
    st.markdown("---")
    if supabase:
        c_res = supabase.table("currents").select("*").execute()
        if c_res.data:
            st.dataframe(pd.DataFrame(c_res.data), use_container_width=True)
        else:
            st.info("Kayıtlı cari bulunmuyor.")

# --- 5. ÖN MUHASEBE & KASA ---
elif menu == "💰 Ön Muhasebe & Kasa":
    st.title("💰 Kasa İşlem Hareketleri")
    st.markdown("---")
    trx = fetch_transactions()
    if trx:
        st.dataframe(pd.DataFrame(trx), use_container_width=True)
    else:
        st.info("Kasa hareketi bulunmuyor.")

# --- 6. ŞİFRE & PROFİL ---
elif menu == "🔑 Şifre & Profil":
    st.title("🔑 Şifre Yönetimi")
    st.markdown("---")
    with st.form("pw_db_form"):
        curr_p = st.text_input("Mevcut Şifre", type="password")
        new_p = st.text_input("Yeni Şifre", type="password")
        if st.form_submit_button("Şifremi Güncelle"):
            if supabase and new_p:
                supabase.table("users").update({"password": new_p}).eq("phone", st.session_state.user_key).execute()
                st.success("Şifreniz Supabase üzerinde kalıcı olarak güncellendi!")
