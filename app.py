import sqlite3
import streamlit as str_app
import streamlit.components.v1 as components
import pandas as pd
import urllib.parse

DB_NAME = "wasel_talabat_pro.db"

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            phone TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            lat REAL DEFAULT 31.2842,
            lon REAL DEFAULT 35.7048
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            name TEXT PRIMARY KEY, 
            category TEXT, 
            phone TEXT, 
            pin_code TEXT DEFAULT '1111',
            location TEXT,
            lat REAL,
            lon REAL,
            delivery_time TEXT,
            delivery_fee REAL,
            image_url TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT, 
            category TEXT, 
            item_name TEXT, 
            description TEXT,
            price REAL, 
            unit_type TEXT,
            image_url TEXT,
            age_restricted INTEGER DEFAULT 0
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_phone TEXT,
            store_name TEXT,
            item_name TEXT,
            price REAL,
            qty REAL,
            total REAL
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            customer_lat REAL DEFAULT 31.2842,
            customer_lon REAL DEFAULT 35.7048,
            store_name TEXT,
            store_lat REAL DEFAULT 31.2842,
            store_lon REAL DEFAULT 35.7048,
            items_desc TEXT,
            sub_total REAL DEFAULT 0.0,
            delivery_fee REAL DEFAULT 1.50,
            service_fee REAL DEFAULT 0.25,
            grand_total REAL,
            payment_method TEXT,
            order_status TEXT DEFAULT 'جديد (بانتظار الإدارة)',
            assigned_driver TEXT DEFAULT 'لم يُعين بعد'
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT, 
            pin_code TEXT DEFAULT '2222',
            vehicle_type TEXT,
            status TEXT DEFAULT 'متوفر'
        )
    """)
    
    # فحص وإضافة الأعمدة الجديدة للتوافق مع الإصدارات السابقة
    for table_name, col_def in [
        ("orders", "customer_lat REAL DEFAULT 31.2842"),
        ("orders", "customer_lon REAL DEFAULT 35.7048"),
        ("orders", "store_lat REAL DEFAULT 31.2842"),
        ("orders", "store_lon REAL DEFAULT 35.7048"),
        ("stores", "lat REAL DEFAULT 31.2842"),
        ("stores", "lon REAL DEFAULT 35.7048"),
        ("stores", "pin_code TEXT DEFAULT '1111'"),
        ("drivers", "pin_code TEXT DEFAULT '2222'"),
        ("customers", "lat REAL DEFAULT 31.2842"),
        ("customers", "lon REAL DEFAULT 35.7048")
    ]:
        try:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass
            
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM stores")
    if c.fetchone()[0] == 0:
        default_stores = [
            ("سوبرماركت طبازه", "Groceries / بقالة", "0791111111", "1111", "الكرك - المرج", 31.2855, 35.7032, "15-25 mins", 1.25, "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=300"),
            ("مطعم الرمسي", "Food / مطاعم", "0795555555", "1111", "الكرك – شارع جامعة مؤته", 31.2820, 35.7010, "20-30 mins", 1.50, "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300"),
            ("مطعم ليالي الكرك", "Food / مشاوي", "0796666666", "1111", "الكرك - المرج", 31.2860, 35.7050, "25-40 mins", 2.00, "https://images.unsplash.com/photo-1544025162-d76694265947?w=300"),
            ("محمص الشعب", "Sweets /محامص", "0798888888", "1111", "الكرك - الثنيه", 31.2900, 35.7100, "10-20 mins", 1.00, "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300")
        ]
        c.executemany("INSERT OR IGNORE INTO stores (name, category, phone, pin_code, location, lat, lon, delivery_time, delivery_fee, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", default_stores)
        
        default_products = [
            ("سوبرماركت طبازه", "تموينات", "سكر الأسرة الناعم (5 كغ)", "سكر أبيض نقي", 3.75, "كيس", "https://images.unsplash.com/photo-1581441363689-1f3c3c342617?w=300", 0),
            ("سوبرماركت طبازه", "دخان", "سجائر ونستون بلو (Winston Blue)", "سجائر وينستون", 2.60, "باكيت", "", 1),
            ("مطعم الرمسي", "وجبات", "وجبة مندي لحم خروف", "أرز مندي مع لحم خروف طازج ولبن", 7.50, "وجبة", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300", 0),
            ("مطعم ليالي الكرك", "مشاوي", "مشاوي مشكلة عائلية (كيلو)", "كيلو، كباب، وشيش طاووق مع المخللات", 18.00, "كيلو", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300", 0),
            ("محمص الشعب", "قهوة ومكسرات", "بن تركي وسط محمش طازج (250 غم)", "قهوة ممتازة بالهيل", 3.50, "كيس", "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300", 0)
        ]
        c.executemany("INSERT INTO products (store_name, category, item_name, description, price, unit_type, image_url, age_restricted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", default_products)
        
        default_drivers = [
            ("معاذ المدادحة", "0799999999", "2222", "سياره", "متوفر"),
            ("عمر الكركي", "0798887766", "2222", "سيارة هبريد", "متوفر")
        ]
        c.executemany("INSERT INTO drivers (name, phone, pin_code, vehicle_type, status) VALUES (?, ?, ?, ?, ?)", default_drivers)
        conn.commit()
         
    conn.close()

init_db()

str_app.set_page_config(page_title="بوابة الكرك للطلبات", layout="wide", page_icon="🧡")

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #ff5a00;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #e05000;
        color: white;
    }
    .product-card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .store-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
"""
str_app.markdown(hide_streamlit_style, unsafe_allow_html=True)

def play_sound_alert(sound_url="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3"):
    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="{sound_url}" type="audio/mpeg">
        </audio>
    """
    str_app.markdown(audio_html, unsafe_allow_html=True)

if "current_portal" not in str_app.session_state:
    str_app.session_state.current_portal = "👤 تسجيل البيانات الشخصية"

if "selected_category" not in str_app.session_state:
    str_app.session_state.selected_category = "الكل"

if "lat" not in str_app.session_state:
    str_app.session_state.lat = 31.2842
if "lon" not in str_app.session_state:
    str_app.session_state.lon = 35.7048

str_app.sidebar.title("🧡 بوابة الكرك للطلبات")
str_app.sidebar.markdown("---")

portal_options = [
    "👤 تسجيل البيانات الشخصية",
    "🏠 الرئيسية (Talabat Home)",
    "🛒 تصفح المتاجر والسلة والدفع",
    "🚚 تابع طلباتك ومسار الرحلة",
    "🔔 لوحة الإدارة المركزية (تحكم كامل)",
    "🏪 بوابة المتاجر (تجهيز الطلبات)",
    "🛵 بوابة السائقين (الاستلام والتوصيل)"
]

current_index = portal_options.index(str_app.session_state.current_portal) if str_app.session_state.current_portal in portal_options else 0
portal = str_app.sidebar.radio("اختر البوابة:", portal_options, index=current_index)
str_app.session_state.current_portal = portal

if "customer_name" not in str_app.session_state:
    str_app.session_state.customer_name = "بوابة الكرك للطلبات"
    str_app.session_state.customer_address = "الكرك - المرج - بالقرب من جامعة مؤتة"
    str_app.session_state.customer_phone = "0797088219"

conn = get_db_connection()
c = conn.cursor()

if portal == "👤 تسجيل البيانات الشخصية":
    str_app.markdown("<h2 style='color: #ff5a00;'>👤 تسجيل بيانات العميل وتحديد الموقع تلقائياً</h2>", unsafe_allow_html=True)
    r_name = str_app.text_input("الاسم الكامل:", value=str_app.session_state.customer_name)
    r_phone = str_app.text_input("رقم الهاتف:", value=str_app.session_state.customer_phone)
    r_address = str_app.text_area("العنوان بالتفصيل:", value=str_app.session_state.customer_address)
    
    str_app.markdown("#### 📍 تحديد الموقع الجغرافي (اللوكيشن التلقائي)")
    
    geo_html = f"""
    <div style="padding: 10px; background: #e3f2fd; border-radius: 8px; border: 1px solid #90caf9; text-align: center;">
        <p style="margin: 0 0 8px 0; font-weight: bold; color: #0d47a1;">اضغط على الزر أدناه لتحديد موقعك الحالي تلقائياً عبر GPS:</p>
        <button onclick="getLocation()" style="background-color: #1976d2; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">📍 حدد موقعي الحالي تلقائياً</button>
        <p id="geo_status" style="margin-top: 8px; font-weight: bold; color: #388e3c;"></p>
    </div>
    <script>
    function getLocation() {{
        var status = document.getElementById("geo_status");
        if (navigator.geolocation) {{
            status.innerHTML = "جاري تحديد موقعك...";
            navigator.geolocation.getCurrentPosition(function(position) {{
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                status.innerHTML = "✅ تم تحديد موقعك بنجاح! (خط العرض: " + lat.toFixed(4) + ", خط الطول: " + lon.toFixed(4) + ")";
            }}, function(error) {{
                status.innerHTML = "❌ تعذر تحديد الموقع. يرجى السماح للمتصفح بالوصول للموقع.";
            }});
        }} else {{
            status.innerHTML = "المتصفح لا يدعم خاصية تحديد الموقع.";
        }}
    }}
    </script>
    """
    components.html(geo_html, height=130)
    
    col_l1, col_l2 = str_app.columns(2)
    with col_l1:
        r_lat = str_app.number_input("خط العرض الحالي (Lat):", value=str_app.session_state.lat, format="%.6f")
    with col_l2:
        r_lon = str_app.number_input("خط الطول الحالي (Lon):", value=str_app.session_state.lon, format="%.6f")
        
    col_btn1, col_btn2 = str_app.columns([1, 1])
    with col_btn1:
        save_clicked = str_app.button("حفظ البيانات والموقع 🚀")
    with col_btn2:
        go_home_clicked = str_app.button("🏠 الانتقال إلى الرئيسية والبدء بالتسوق")
        
    if save_clicked or go_home_clicked:
        if r_name.strip() and r_phone.strip():
            c.execute("INSERT OR REPLACE INTO customers (phone, name, address, lat, lon) VALUES (?, ?, ?, ?, ?)", 
                      (r_phone, r_name, r_address, r_lat, r_lon))
            conn.commit()
            str_app.session_state.customer_name = r_name
            str_app.session_state.customer_phone = r_phone
            str_app.session_state.customer_address = r_address
            str_app.session_state.lat = r_lat
            str_app.session_state.lon = r_lon
            str_app.success("✅ تم حفظ بياناتك وموقعك الجغرافي بنجاح!")
            
            str_app.session_state.current_portal = "🏠 الرئيسية (Talabat Home)"
            str_app.rerun()
        else:
            str_app.error("يرجى إدخال الاسم ورقم الهاتف.")

elif portal == "🏠 الرئيسية (Talabat Home)":
    str_app.markdown("<h1 style='color: #ff5a00; text-align: center; margin-bottom: 20px;'>بوابة الكرك للطلبات</h1>", unsafe_allow_html=True)
    col_loc, col_prof = str_app.columns([4, 1])
    with col_loc:
        map_link = f"https://maps.google.com/?q={str_app.session_state.lat},{str_app.session_state.lon}"
        str_app.markdown(f"<h4 style='color: #ff5a00; margin-top: 0;'>📍 موقعك الحالي: {str_app.session_state.customer_address} [<a href='{map_link}' target='_blank'>عرض على الخريطة</a>]</h4>", unsafe_allow_html=True)
    with col_prof:
        if str_app.button("👤 تعديل بياناتي وموقعي"):
            str_app.session_state.current_portal = "👤 تسجيل البيانات الشخصية"
            str_app.rerun()

    c.execute("SELECT DISTINCT category FROM stores")
    cat_stores = [row[0] for row in c.fetchall()]
    categories_list = ["الكل"] + cat_stores
    
    str_app.markdown("#### 📂 أقسام المتاجر السريعة")
    cols_cat = str_app.columns(len(categories_list) if len(categories_list) > 0 else 1)
    for idx, cat_name in enumerate(categories_list):
        with cols_cat[idx % len(cols_cat)]:
            is_selected = (str_app.session_state.selected_category == cat_name)
            btn_label = f"🔥 {cat_name}" if is_selected else cat_name
            if str_app.button(btn_label, key=f"cat_row_btn_{idx}"):
                str_app.session_state.selected_category = cat_name
                str_app.rerun()
                
    str_app.markdown("---")
    
    selected_cat = str_app.session_state.selected_category
    search_q = str_app.text_input("🔍 ابحث عن صنف أو متجر...", placeholder="ابحث عن مندي، سوبرماركت، بندورة...")
    if search_q.strip():
        str_app.markdown(f"### نتائج البحث عن: `{search_q}`")
        c.execute("SELECT store_name, item_name, description, price, unit_type, image_url, age_restricted FROM products WHERE item_name LIKE ? OR description LIKE ?", (f"%{search_q.strip()}%", f"%{search_q.strip()}%"))
        results = c.fetchall()
        if results:
            for r_store, r_name, r_desc, r_price, r_unit, r_img, r_age in results:
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                rc1, rc2, rc3 = str_app.columns([1, 3, 1])
                with rc1:
                    if r_img and r_img.startswith("http"):
                        str_app.image(r_img, width=90)
                    else:
                        str_app.markdown("<h1 style='text-align: center; font-size: 40px;'>🛒</h1>", unsafe_allow_html=True)
                with rc2:
                    if r_age:
                        str_app.markdown("🔒 `19+ years (صنف مقيد العمر)`")
                    str_app.markdown(f"### {r_name}")
                    if r_desc:
                        str_app.write(r_desc)
                    str_app.markdown(f"**السعر: {r_price:.2f} د.أ** ({r_unit}) | المتجر: `{r_store}`")
                with rc3:
                    if str_app.button("اطلب الآن", key=f"srch_btn_{r_name}_{r_store}"):
                        str_app.session_state.active_store = r_store
                        str_app.session_state.current_portal = "🛒 تصفح المتاجر والسلة والدفع"
                        str_app.rerun()
                str_app.markdown("</div>", unsafe_allow_html=True)

    str_app.markdown("---")
    str_app.markdown(f"### 🛒 المتاجر والمطاعم في قسم: `{selected_cat}`")
    
    if selected_cat == "الكل":
        c.execute("SELECT name, category, location, lat, lon, delivery_time, delivery_fee, image_url FROM stores")
    else:
        c.execute("SELECT name, category, location, lat, lon, delivery_time, delivery_fee, image_url FROM stores WHERE category = ?", (selected_cat,))
        
    all_stores = c.fetchall()
    
    if not all_stores:
        str_app.info("لا توجد متاجر متاحة في هذا القسم حالياً.")
    else:
        st_cols = str_app.columns(2)
        for idx, (s_name, s_cat, s_loc, s_lat, s_lon, s_time, s_fee, s_img) in enumerate(all_stores):
            with st_cols[idx % 2]:
                str_app.markdown("<div class='store-card'>", unsafe_allow_html=True)
                if s_img and s_img.startswith("http"):
                    str_app.image(s_img, use_container_width=True)
                else:
                    str_app.markdown("<h1 style='text-align: center; font-size: 40px;'>🏪</h1>", unsafe_allow_html=True)
                str_app.markdown(f"### {s_name}")
                store_map_url = f"https://maps.google.com/?q={s_lat},{s_lon}"
                str_app.write(f"🏷️ {s_cat} | 📍 {s_loc} [<a href='{store_map_url}' target='_blank'>الخريطة</a>]")
                str_app.write(f"⏱️ {s_time} | 🚚 {s_fee:.2f} JOD")
                if str_app.button(f"تصفح متجر {s_name}", key=f"btn_store_home_{idx}_{s_name}"):
                    str_app.session_state.active_store = s_name
                    str_app.session_state.current_portal = "🛒 تصفح المتاجر والسلة والدفع"
                    str_app.rerun()
                str_app.markdown("</div>", unsafe_allow_html=True)

elif portal == "🛒 تصفح المتاجر والسلة والدفع":
    if str_app.button("🏠 العودة إلى القائمة الرئيسية لإضافة طلب آخر"):
        str_app.session_state.current_portal = "🏠 الرئيسية (Talabat Home)"
        str_app.rerun()

    str_app.markdown("<h2 style='color: #ff5a00;'>🛒 سلة الطلبات ودفع الفواتير</h2>", unsafe_allow_html=True)
    c.execute("SELECT name, delivery_fee, lat, lon FROM stores")
    stores_data = c.fetchall()
    store_names = [s[0] for s in stores_data]
    store_fees_map = {s[0]: s[1] for s in stores_data}
    store_coords_map = {s[0]: (s[2], s[3]) for s in stores_data}
    
    default_st = str_app.session_state.get("active_store", store_names[0] if store_names else "")
    chosen_store = str_app.selectbox("اختر المتجر أو المطعم للتسوق منه:", store_names, index=store_names.index(default_st) if default_st in store_names else 0)
    
    if chosen_store:
        str_app.session_state.active_store = chosen_store
        current_delivery_fee = store_fees_map.get(chosen_store, 1.50)
        c.execute("SELECT id, item_name, description, price, unit_type, image_url, age_restricted FROM products WHERE store_name = ?", (chosen_store,))
        prods = c.fetchall()
        
        if not prods:
            str_app.info(f"لا توجد أصناف مسجلة حالياً في متجر '{chosen_store}'.")
        else:
            for pid, pname, pdesc, pprice, punit, pimg, page_res in prods:
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                col_det, col_img = str_app.columns([3, 1])
                with col_det:
                    if page_res:
                        str_app.markdown("🔒 `صنف مقيد (19+)`")
                    str_app.markdown(f"### {pname}")
                    str_app.markdown(f"<h3 style='color: #ff5a00; margin: 2px 0;'>السعر: {pprice:.2f} د.أ ({punit})</h3>", unsafe_allow_html=True)
                    if pdesc:
                        str_app.write(f"📝 {pdesc}")
                    
                    qty_ord = str_app.number_input(f"حدد الكمية ({punit})", min_value=0.0, step=1.0, key=f"qty_item_box_{pid}")
                    
                    if str_app.button(f"أضف إلى السلة 🛒", key=f"add_cart_btn_{pid}"):
                        if qty_ord > 0:
                            item_total = qty_ord * pprice
                            c.execute("INSERT INTO cart (customer_phone, store_name, item_name, price, qty, total) VALUES (?, ?, ?, ?, ?, ?)",
                                      (str_app.session_state.customer_phone, chosen_store, pname, pprice, qty_ord, item_total))
                            conn.commit()
                            str_app.success(f"✅ تم إضافة {qty_ord} {punit} من '{pname}' إلى السلة بنجاح!")
                        else:
                            str_app.warning("يرجى تحديد الكمية أولاً قبل الإضافة.")
                with col_img:
                    if pimg and pimg.startswith("http"):
                        str_app.image(pimg, width=120)
                    else:
                        str_app.markdown("<h1 style='text-align: center; font-size: 50px;'>🛍️</h1>", unsafe_allow_html=True)
                str_app.markdown("</div>", unsafe_allow_html=True)
            
            str_app.markdown("---")
            str_app.markdown("### 🛒 محتويات سلة الطلبات الحالية:")
            c.execute("SELECT id, store_name, item_name, price, qty, total FROM cart WHERE customer_phone = ?", (str_app.session_state.customer_phone,))
            cart_items = c.fetchall()
            
            if cart_items:
                sub_total = 0.0
                for cid, cstore, citem, cprice, cqty, ctot in cart_items:
                    sub_total += ctot
                    col_ci1, col_ci2 = str_app.columns([4, 1])
                    with col_ci1:
                        str_app.write(f"• {citem} (متجر: {cstore}) - الكمية: {cqty} عدد × {cprice} د.أ = **{ctot:.2f} د.أ**")
                    with col_ci2:
                        if str_app.button("حذف ❌", key=f"del_cart_{cid}"):
                            c.execute("DELETE FROM cart WHERE id = ?", (cid,))
                            conn.commit()
                            str_app.rerun()
                
                service_fee = 0.25
                grand_total = sub_total + current_delivery_fee + service_fee
                str_app.markdown(f"### 💳 المجموع الإجمالي المطلوب: `{grand_total:.2f} د.أ` (يشمل التوصيل {current_delivery_fee} د.أ والخدمة {service_fee} د.أ)")
                
                with str_app.form("checkout_form_final"):
                    c_name = str_app.text_input("الاسم الكامل:", value=str_app.session_state.customer_name)
                    c_phone = str_app.text_input("رقم الهاتف:", value=str_app.session_state.customer_phone)
                    c_addr = str_app.text_input("عنوان التوصيل بالتفصيل:", value=str_app.session_state.customer_address)
                    
                    pay_method = str_app.selectbox("طريقة الدفع:", [
                        "الدفع نقداً عند الاستلام", 
                        "CliQ - samarza (بنك الاتحاد)", 
                        "CliQ - ميرال (البنك الإسلامي الأردني: 962797088219)"
                    ])
                    
                    submit_order = str_app.form_submit_button("🛒 إرسال الطلب النهائي 🚀")

                if submit_order:
                    if c_name.strip() and c_phone.strip():
                        items_desc_str = ", ".join([f"{i[2]} ({i[4]})" for i in cart_items])
                        st_lat_val, st_lon_val = store_coords_map.get(chosen_store, (31.2842, 35.7048))
                        
                        c.execute("""
                            INSERT INTO orders (customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, sub_total, delivery_fee, service_fee, grand_total, payment_method, order_status, assigned_driver)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'جديد (بانتظار الإدارة)', 'لم يُعين بعد')
                        """, (c_name, c_phone, c_addr, str_app.session_state.lat, str_app.session_state.lon, chosen_store, st_lat_val, st_lon_val, items_desc_str, sub_total, current_delivery_fee, service_fee, grand_total, pay_method))
                        
                        conn.commit()
                        
                        c.execute("SELECT last_insert_rowid()")
                        new_order_id = c.fetchone()[0]
                        
                        c.execute("DELETE FROM cart WHERE customer_phone = ?", (str_app.session_state.customer_phone,))
                        conn.commit()
                        
                        str_app.success("🎉 تم إرسال طلبك بنجاح!")
                        
                        whatsapp_msg = f"طلب جديد # {new_order_id}%0aالزبون: {c_name}%0aالهاتف: {c_phone}%0aالعنوان: {c_addr}%0a[لوكيشن الزبون]: https://maps.google.com/?q={str_app.session_state.lat},{str_app.session_state.lon}%0aالمتجر: {chosen_store}%0aالأصناف: {items_desc_str}%0aالإجمالي: {grand_total:.2f} د.أ%0aطريقة الدفع: {pay_method}"
                        miral_phone = "962797088219"
                        wa_url = f"https://api.whatsapp.com/send?phone={miral_phone}&text={whatsapp_msg}"
                        
                        str_app.markdown(f"### 📲 إرسال تفاصيل الطلب عبر الواتساب لميرال:")
                        str_app.markdown(f"<a href='{wa_url}' target='_blank' style='background-color:#25d366; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;'>📤 اضغط هنا لإرسال تفاصيل الطلب عبر الواتساب لميرال</a>", unsafe_allow_html=True)
                        
                        if str_app.button("🏠 العودة للرئيسية لإضافة طلب آخر"):
                            str_app.session_state.current_portal = "🏠 الرئيسية (Talabat Home)"
                            str_app.rerun()
            else:
                str_app.info("السلة فارغة حالياً. قم بتحديد الكمية واضغط على 'أضف إلى السلة' لكل صنف ترغب به.")

elif portal == "🚚 تابع طلباتك ومسار الرحلة":
    str_app.markdown("<h2 style='color: #ff5a00;'>🚚 تتبع طلباتك ومسار الرحلة المباشر</h2>", unsafe_allow_html=True)
    cust_phone_track = str_app.text_input("أدخل رقم هاتفك المسجل لعرض طلباتك وتتبعها:", value=str_app.session_state.customer_phone)
    
    if cust_phone_track.strip():
        c.execute("SELECT id, store_name, store_lat, store_lon, customer_lat, customer_lon, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE customer_phone = ? ORDER BY id DESC", (cust_phone_track.strip(),))
        my_orders = c.fetchall()
        
        if not my_orders:
            str_app.info("لا توجد طلبات مسجلة بهذا الرقم حالياً.")
        else:
            for mo in my_orders:
                mid, mstore, mslat, mslon, mclat, mclon, mitems, mtot, mstat, mdrv = mo
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                str_app.markdown(f"### 📦 طلب رقم #{mid} - المتجر: `{mstore}`")
                str_app.write(f"🛒 الأصناف: {mitems}")
                str_app.write(f"💰 المبلغ الإجمالي: **{mtot:.2f} د.أ** | السائق المعين: `{mdrv}`")
                str_app.markdown(f"📌 **حالة الطلب الحالية:** `{mstat}`")
                
                str_app.markdown("#### 🗺️ مسار رحلة الطلب المباشر:")
                store_map_link = f"https://maps.google.com/?q={mslat},{mslon}"
                cust_map_link = f"https://maps.google.com/?q={mclat},{mclon}"
                
                str_app.markdown(f"""
                * 🏪 **موقع المتجر (نقطة الاستلام):** [فتح موقع المتجر على الخريطة]({store_map_link})
                * 🛵 **حالة السائق:** {mdrv if mdrv != 'لم يُعين بعد' else 'جاري توقيت سائق لتوصيل طلبك'}
                * 🎯 **موقعك (نقطة التسليم):** [فتح موقعك على الخريطة]({cust_map_link})
                """)
                
                # خريطة توضيحية تفاعلية لمسار الرحلة بين المتجر والعميل
                route_map_html = f"""
                <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; border: 1px solid #a5d6a7; text-align: center;">
                    <p style="margin: 0; font-weight: bold; color: #2e7d32;">📍 مسار الرحلة الجغرافي نشط لطلبك #{mid}</p>
                    <p style="margin: 5px 0 0 0; font-size: 13px; color: #555;">من المتجر ({mstore}) ➔ إلى عنوان استلامك المحدد.</p>
                </div>
                """
                components.html(route_map_html, height=80)
                str_app.markdown("</div>", unsafe_allow_html=True)

elif portal == "🔔 لوحة الإدارة المركزية (تحكم كامل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🔔 لوحة التحكم المركزية (الإدارة)</h2>", unsafe_allow_html=True)
    admin_pass = str_app.text_input("أدخل رمز سر الإدارة:", type="password")
    
    if admin_pass == "1234":
        str_app.success("تم تسجيل الدخول لصلاحيات الإدارة بنجاح.")
        
        c.execute("SELECT COUNT(*) FROM orders WHERE order_status LIKE '%جديد%'")
        new_cnt = c.fetchone()[0]
        if new_cnt > 0:
            play_sound_alert("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3")
            str_app.warning(f"🚨 يوجد {new_cnt} طلب جديد بانتظار الاعتماد!")

        tab1, tab2, tab3, tab4, tab5 = str_app.tabs(["📦 إدارة ومتابعة الطلبات", "🏪 إدارة المتاجر والرقابة", "🍔 إدارة الأصناف والأسعار", "📥 الاستيراد الآلي (CSV)", "🛵 إدارة السائقين"])
        
        with tab1:
            str_app.markdown("### 🔔 الطلبات الواردة ومواقع الزبائن والمتاجر وتوجيهها:")
            c.execute("SELECT id, customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders ORDER BY id DESC")
            orders_all = c.fetchall()
            if not orders_all:
                str_app.info("لا توجد طلبات جديدة حالياً.")
            else:
                c.execute("SELECT name, phone FROM drivers")
                drivers_data_all = c.fetchall()
                drivers_list = [d[0] for d in drivers_data_all]
                
                for ord_item in orders_all:
                    oid, ocname, ocphone, ocaddr, oclat, oclon, ostore, oslat, oslon, oitems, otot, opay, ostat, odrv = ord_item
                    with str_app.expander(f"طلب رقم #{oid} | متجر: {ostore} | الزبون: {ocname} | الحالة: [{ostat}]"):
                        str_app.write(f"📱 الهاتف: {ocphone} | العنوان: {ocaddr}")
                        cust_map_url = f"https://maps.google.com/?q={oclat},{oclon}"
                        store_map_url = f"https://maps.google.com/?q={oslat},{oslon}"
                        str_app.markdown(f"📍 **لوكيشن الزبون:** [<a href='{cust_map_url}' target='_blank'>فتح موقع العميل على الخريطة</a>] | 🏪 **لوكيشن المتجر:** [<a href='{store_map_url}' target='_blank'>فتح موقع المتجر</a>]", unsafe_allow_html=True)
                        str_app.write(f"🛒 الأصناف: {oitems} | الإجمالي: {otot:.2f} د.أ | الدفع: {opay}")
                        
                        c.execute("SELECT phone FROM stores WHERE name = ?", (ostore,))
                        st_phone_row = c.fetchone()
                        store_contact_phone = st_phone_row[0] if st_phone_row and st_phone_row[0] else "962790000000"
                        
                        seller_msg = f"طلب جديد رقم #{oid} موجه لمتجركم ({ostore})%0aالزبون: {ocname}%0aالهاتف: {ocphone}%0aالعنوان: {ocaddr}%0a[لوكيشن الزبون]: https://maps.google.com/?q={oclat},{oclon}%0aالأصناف المطلوب تجهيزها: {oitems}%0aالمبلغ المطلوب تحصيله: {otot:.2f} د.أ (%0aطريقة الدفع: {opay})%0aيرجى التجهيز الفوري!"
                        seller_wa_url = f"https://api.whatsapp.com/send?phone={store_contact_phone}&text={seller_msg}"
                        
                        str_app.markdown(f"<a href='{seller_wa_url}' target='_blank' style='background-color:#25d366; color:white; padding:8px 15px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:10px;'>📤 إرسال تفاصيل الطلب واللوكيشن للبائع عبر الواتساب</a>", unsafe_allow_html=True)
                        
                        col_st1, col_st2 = str_app.columns(2)
                        with col_st1:
                            new_status = str_app.selectbox(f"حالة الطلب #{oid}", ["جديد (بانتظار الإدارة)", "تم الاعتماد وبانتظار تجهيز المتجر", "جاري التجهيز بالمطعم/المتجر", "مع السائق في طريقه للعميل", "تم التسليم بنجاح"], key=f"admin_st_{oid}")
                        with col_st2:
                            assigned_d = str_app.selectbox(f"تعيين سائق #{oid}", ["لم يُعين بعد"] + drivers_list, key=f"admin_drv_{oid}")
                        
                        if str_app.button(f"حفظ التحديث #{oid}", key=f"save_ord_btn_{oid}"):
                            c.execute("UPDATE orders SET order_status = ?, assigned_driver = ? WHERE id = ?", (new_status, assigned_d, oid))
                            conn.commit()
                            str_app.success(f"✅ تم تحديث الطلب #{oid}")
                            str_app.rerun()

        with tab2:
            str_app.markdown("### 🏪 إدارة المتاجر وإحداثياتها وأرقامها السرية:")
            
            with str_app.form("add_store_form"):
                str_app.markdown("#### إضافة متجر جديد أو تحديث بياناته ورقمة السري")
                ns_name = str_app.text_input("اسم المتجر أو المطعم (مفتاح أساسي للتعديل أو الإضافة):")
                ns_cat = str_app.text_input("التصنيف (مثال: مطاعم):")
                ns_phone = str_app.text_input("رقم هاتف المتجر (لإرسال الطلبات واتساب):")
                ns_pin = str_app.text_input("الرقم السري الخاص بداخل المتجر (PIN):", value="1111", type="password")
                ns_loc = str_app.text_input("العنوان والمنطقة:")
                ns_slat = str_app.number_input("خط عرض المتجر (Lat):", value=31.2842, format="%.6f")
                ns_slon = str_app.number_input("خط طول المتجر (Lon):", value=35.7048, format="%.6f")
                ns_time = str_app.text_input("وقت التوصيل:", value="15-25 mins")
                ns_fee = str_app.number_input("أجور التوصيل (د.أ):", value=1.50)
                ns_img = str_app.text_input("رابط صورة المتجر (اختياري):")
                
                if str_app.form_submit_button("حفظ أو تحديث المتجر ➕"):
                    if ns_name.strip():
                        c.execute("INSERT OR REPLACE INTO stores (name, category, phone, pin_code, location, lat, lon, delivery_time, delivery_fee, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (ns_name, ns_cat, ns_phone, ns_pin, ns_loc, ns_slat, ns_slon, ns_time, ns_fee, ns_img))
                        conn.commit()
                        str_app.success(f"✅ تم حفظ المتجر '{ns_name}' بنجاح!")
                        str_app.rerun()
                    else:
                        str_app.error("يرجى إدخال اسم المتجر.")

            str_app.markdown("---")
            str_app.markdown("### 📋 قائمة المتاجر المسجلة (تعديل أو حذف):")
            c.execute("SELECT name, category, phone, pin_code, location, lat, lon, delivery_time, delivery_fee FROM stores")
            db_stores = c.fetchall()
            
            if not db_stores:
                str_app.info("لا توجد متاجر مسجلة حالياً.")
            else:
                for st_row in db_stores:
                    st_name, st_cat, st_phone, st_pin, st_loc, st_lat, st_lon, st_time, st_fee = st_row
                    with str_app.expander(f"🏪 متجر: {st_name} ({st_cat}) | الرقم السري: {st_pin}"):
                        str_app.write(f"📱 الهاتف: {st_phone} | 📍 العنوان: {st_loc}")
                        str_app.write(f"🌐 الإحداثيات: Lat: {st_lat}, Lon: {st_lon} | ⏱️ الوقت: {st_time} | 🚚 التوصيل: {st_fee} د.أ")
                        
                        col_del_btn, col_dummy = str_app.columns([1, 4])
                        with col_del_btn:
                            if str_app.button(f"حذف المتجر ❌", key=f"del_store_{st_name}"):
                                c.execute("DELETE FROM stores WHERE name = ?", (st_name,))
                                c.execute("DELETE FROM products WHERE store_name = ?", (st_name,))
                                conn.commit()
                                str_app.success(f"🗑️ تم حذف المتجر '{st_name}' وجميع أصنافه بنجاح!")
                                str_app.rerun()

        with tab3:
            str_app.markdown("### 🍔 إضافة أو حذف الأصناف:")
            c.execute("SELECT name FROM stores")
            st_names_list = [s[0] for s in c.fetchall()]
            
            if st_names_list:
                with str_app.form("product_add_form_isolated"):
                    p_store = str_app.selectbox("اختر المتجر:", st_names_list, key="p_store_sel")
                    p_cat = str_app.text_input("قسم الصنف:", value="خضار")
                    p_name = str_app.text_input("اسم الصنف:", value="")
                    p_desc = str_app.text_area("وصف الصنف والتفاصيل:")
                    p_price = str_app.number_input("السعر (بالدينار):", min_value=0.01, value=0.75, step=0.05)
                    p_unit = str_app.text_input("وحدة القياس:", value="كيلو")
                    p_img = str_app.text_input("رابط صورة المنتج (اختياري):")
                    p_age = str_app.checkbox("صنف مقيد العمر (19+ - مثل الدخان والتبغ)")
                    
                    if str_app.form_submit_button("إضافة الصنف للمتجر 🚀"):
                        if p_name.strip():
                            c.execute("INSERT INTO products (store_name, category, item_name, description, price, unit_type, image_url, age_restricted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (p_store, p_cat, p_name, p_desc, p_price, p_unit, p_img, 1 if p_age else 0))
                            conn.commit()
                            str_app.success(f"✅ تم إضافة الصنف '{p_name}' إلى متجر '{p_store}' بنجاح!")
                            str_app.rerun()
                        else:
                            str_app.error("يرجى إدخال اسم الصنف.")
            else:
                str_app.warning("يرجى إضافة متجر أولاً قبل إضافة الأصناف.")

        with tab4:
            str_app.markdown("### 📥 الاستيراد الآلي (CSV) للأصناف والأسعار:")
            str_app.info("قم برفع ملف CSV يحتوي على الأعمدة: (اسم الصنف، السعر) بترميز UTF-8 لتجنب مشاكل الحروف العربية.")
            st_import_store = str_app.selectbox("اختر المتجر لتحديث أصنافه عبر الملف:", st_names_list if st_names_list else [""], key="import_st_box")
            csv_file_up = str_app.file_uploader("اختر ملف الـ CSV:", type=["csv"])
            
            if csv_file_up and st_import_store:
                try:
                    df_imported = pd.read_csv(csv_file_up, encoding='utf-8')
                    str_app.write("معاينة البيانات المستوردة من الملف:")
                    str_app.dataframe(df_imported.head())
                    
                    if str_app.button("تأكيد وحفظ الأصناف المستوردة بالمتجر 🚀"):
                        count_ins = 0
                        for _, row in df_imported.iterrows():
                            col_item_name = str(row.iloc[0]).strip()
                            col_price = float(row.iloc[1]) if pd.notnull(row.iloc[1]) else 0.0
                            if col_item_name and col_item_name != 'nan':
                                c.execute("INSERT INTO products (store_name, category, item_name, description, price, unit_type) VALUES (?, ?, ?, ?, ?, ?)",
                                          (st_import_store, "عام", col_item_name, "مستورد عبر CSV", col_price, "عدد"))
                                count_ins += 1
                        conn.commit()
                        str_app.success(f"✅ تم بنجاح استيراد وإضافة {count_ins} صنفاً لمتجر '{st_import_store}'!")
                except Exception as e:
                    str_app.error(f"حدث خطأ أثناء قراءة الملف تأكد من الترميز (UTF-8) وصيغة الأعمدة: {e}")

        with tab5:
            str_app.markdown("### 🛵 إدارة السائقين وأرقامهم السرية:")
            with str_app.form("driver_add_form"):
                d_name = str_app.text_input("اسم السائق:")
                d_phone = str_app.text_input("رقم هاتف السائق:")
                d_pin = str_app.text_input("الرقم السري للسائق (PIN):", value="2222", type="password")
                d_veh = str_app.text_input("نوع المركبة:", value="سيارة")
                if str_app.form_submit_button("إضافة سائق جديد ➕"):
                    if d_name.strip():
                        c.execute("INSERT INTO drivers (name, phone, pin_code, vehicle_type, status) VALUES (?, ?, ?, ?, 'متوفر')", (d_name, d_phone, d_pin, d_veh))
                        conn.commit()
                        str_app.success(f"✅ تم إضافة السائق '{d_name}' بنجاح!")
                        str_app.rerun()
            
            str_app.markdown("#### السائقون المسجلون:")
            c.execute("SELECT id, name, phone, pin_code, vehicle_type, status FROM drivers")
            all_drvs = c.fetchall()
            for did, dname, dph, dpin, dveh, dst in all_drvs:
                str_app.write(f"- السائق: **{dname}** | الهاتف: {dph} | الرقم السري: `{dpin}` | المركبة: {dveh} | الحالة: `{dst}`")

elif portal == "🏪 بوابة المتاجر (تجهيز الطلبات)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🏪 بوابة المتاجر - تجهيز الطلبات (محمية برقم سري)</h2>", unsafe_allow_html=True)
    
    c.execute("SELECT name FROM stores")
    st_names_portal = [s[0] for s in c.fetchall()]
    chosen_portal_store = str_app.selectbox("اختر متجرك:", st_names_portal if st_names_portal else [""])
    store_entered_pin = str_app.text_input("أدخل الرقم السري الخاص بالمتجر:", type="password")
    
    auth_store_ok = False
    if chosen_portal_store and store_entered_pin:
        c.execute("SELECT pin_code FROM stores WHERE name = ?", (chosen_portal_store,))
        row_pin = c.fetchone()
        if row_pin and row_pin[0] == store_entered_pin:
            auth_store_ok = True
        else:
            str_app.error("❌ الرقم السري غير صحيح يرجى التأكد من إدارة المنصة.")

    if auth_store_ok and chosen_portal_store:
        str_app.success(f"🔓 تم تسجيل الدخول بنجاح لمتجر: {chosen_portal_store}")
        
        c.execute("SELECT COUNT(*) FROM orders WHERE store_name = ? AND order_status LIKE '%جديد%'", (chosen_portal_store,))
        st_new_orders_cnt = c.fetchone()[0]
        if st_new_orders_cnt > 0:
            play_sound_alert("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3")
            str_app.warning(f"🔔 تنبيه: يوجد {st_new_orders_cnt} طلب جديد بانتظار التجهيز في متجرك!")

        c.execute("SELECT id, customer_name, customer_phone, customer_address, items_desc, grand_total, payment_method, order_status FROM orders WHERE store_name = ? ORDER BY id DESC", (chosen_portal_store,))
        store_orders = c.fetchall()
        if not store_orders:
            str_app.info(f"لا توجد طلبات موجهة حالياً لمتجر '{chosen_portal_store}'.")
        else:
            for so in store_orders:
                so_id, so_cname, so_cphone, so_caddr, so_items, so_tot, so_pay, so_stat = so
                str_app.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                str_app.markdown(f"### طلب رقم #{so_id} - الزبون: {so_cname}")
                str_app.write(f"📱 هاتف الزبون: {so_cphone} | 📍 العنوان: {so_caddr}")
                str_app.write(f"🛒 الأصناف المطلوبة: {so_items}")
                str_app.write(f"💰 المجموع: {so_tot:.2f} د.أ | الدفع: {so_pay} | الحالة الحالية: **{so_stat}**")
                
                new_st_store = str_app.selectbox(f"تحديث حالة الطلب #{so_id}", ["جديد (بانتظار الإدارة)", "تم الاعتماد وبانتظار تجهيز المتجر", "جاري التجهيز بالمطعم/المتجر", "جاهز للاستلام من السائق", "تم التسليم بنجاح"], key=f"st_portal_up_{so_id}")
                if str_app.button(f"حفظ حالة الطلب #{so_id}", key=f"st_portal_btn_{so_id}"):
                    c.execute("UPDATE orders SET order_status = ? WHERE id = ?", (new_st_store, so_id))
                    conn.commit()
                    str_app.success(f"✅ تم تحديث حالة الطلب #{so_id} بنجاح!")
                    str_app.rerun()
                str_app.markdown("</div>", unsafe_allow_html=True)

elif portal == "🛵 بوابة السائقين (الاستلام والتوصيل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛵 بوابة السائقين - مهام التوصيل (محمية برقم سري)</h2>", unsafe_allow_html=True)
    
    c.execute("SELECT name FROM drivers")
    drv_names = [d[0] for d in c.fetchall()]
    chosen_driver = str_app.selectbox("اختر اسمك كَسائق:", drv_names if drv_names else [""])
    driver_entered_pin = str_app.text_input("أدخل الرقم السري الخاص بك:", type="password")
    
    auth_driver_ok = False
    if chosen_driver and driver_entered_pin:
        c.execute("SELECT pin_code FROM drivers WHERE name = ?", (chosen_driver,))
        d_row_pin = c.fetchone()
        if d_row_pin and d_row_pin[0] == driver_entered_pin:
            auth_driver_ok = True
        else:
            str_app.error("❌ الرقم السري للسائق غير صحيح.")

    if auth_driver_ok and chosen_driver:
        str_app.success(f"🔓 أهلاً بك يا {chosen_driver}، تم تسجيل دخولك بنجاح.")
        
        c.execute("SELECT COUNT(*) FROM orders WHERE assigned_driver = ? AND order_status NOT LIKE '%تم التسليم%'", (chosen_driver,))
        drv_tasks_cnt = c.fetchone()[0]
        if drv_tasks_cnt > 0:
            play_sound_alert("https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3")
            str_app.warning(f"🔔 تنبيه: لديك {drv_tasks_cnt} مهام توصيل بانتظار التنفيذ!")

        c.execute("SELECT id, customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, payment_method, order_status FROM orders WHERE assigned_driver = ? ORDER BY id DESC", (chosen_driver,))
        driver_orders = c.fetchall()
        if not driver_orders:
            str_app.info(f"لا توجد طلبات معينة لك حالياً يا {chosen_driver}.")
        else:
            for dro in driver_orders:
                d_id, d_cname, d_cphone, d_caddr, d_clat, d_clon, d_store, d_slat, d_slon, d_items, d_tot, d_pay, d_stat = dro
                str_app.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                str_app.markdown(f"### مهمة توصيل رقم #{d_id} | المتجر: {d_store}")
                str_app.write(f"👤 الزبون: {d_cname} | 📱 الهاتف: {d_cphone} | 📍 العنوان: {d_caddr}")
                
                store_map_link = f"https://maps.google.com/?q={d_slat},{d_slon}"
                cust_map_link = f"https://maps.google.com/?q={d_clat},{d_clon}"
                str_app.markdown(f"📍 **[موقع المتجر على الخريطة]({store_map_link})** | 🎯 **[موقع العميل على الخريطة]({cust_map_link})**", unsafe_allow_html=True)
                str_app.write(f"🛒 الأصناف: {d_items} | المطلوب تحصيله: **{d_tot:.2f} د.أ** ({d_pay})")
                str_app.write(f"📌 حالة الطلب الحالية: {d_stat}")
                
                drv_new_st = str_app.selectbox(f"تحديث حالة التوصيل للطلب #{d_id}", ["مع السائق في طريقه للعميل", "تم التسليم بنجاح"], key=f"drv_st_box_{d_id}")
                if str_app.button(f"تحديث حالة الطلب #{d_id}", key=f"drv_save_btn_{d_id}"):
                    c.execute("UPDATE orders SET order_status = ? WHERE id = ?", (drv_new_st, d_id))
                    conn.commit()
                    str_app.success(f"✅ تم تحديث حالة الطلب #{d_id} بنجاح!")
                    str_app.rerun()
                str_app.markdown("</div>", unsafe_allow_html=True)

conn.close()