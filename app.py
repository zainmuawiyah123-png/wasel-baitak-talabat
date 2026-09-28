import sqlite3
import streamlit as str_app
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
            location TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            name TEXT PRIMARY KEY, 
            category TEXT, 
            phone TEXT, 
            location TEXT,
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
            store_name TEXT,
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
            vehicle_type TEXT,
            status TEXT DEFAULT 'متوفر'
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM stores")
    if c.fetchone()[0] == 0:
        default_stores = [
            ("سوبرماركت طبازه", "Groceries / بقالة", "0791111111", "الكرك - المرج", "15-25 mins", 1.25, "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=300"),
            ("مطعم الرمسي", "Food / مطاعم", "0795555555", "الكرك – شارع جامعة مؤته", "20-30 mins", 1.50, "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300"),
            ("مطعم ليالي الكرك", "Food / مشاوي", "0796666666", "الكرك - المرج", "25-40 mins", 2.00, "https://images.unsplash.com/photo-1544025162-d76694265947?w=300"),
            ("محمص الشعب", "Sweets /محامص", "0798888888", "الكرك - الثنيه", "10-20 mins", 1.00, "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300")
        ]
        c.executemany("INSERT OR IGNORE INTO stores (name, category, phone, location, delivery_time, delivery_fee, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)", default_stores)
        
        default_products = [
            ("سوبرماركت طبازه", "تموينات", "سكر الأسرة الناعم (5 كغ)", "سكر أبيض نقي", 3.75, "كيس", "https://images.unsplash.com/photo-1581441363689-1f3c3c342617?w=300", 0),
            ("سوبرماركت طبازه", "دخان", "سجائر ونستون بلو (Winston Blue)", "سجائر وينستون", 2.60, "باكيت", "", 1),
            ("مطعم الرمسي", "وجبات", "وجبة مندي لحم خروف", "أرز مندي مع لحم خروف طازج ولبن", 7.50, "وجبة", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300", 0),
            ("مطعم ليالي الكرك", "مشاوي", "مشاوي مشكلة عائلية (كيلو)", "كيلو، كباب، وشيش طاووق مع المخللات", 18.00, "كيلو", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=300", 0),
            ("محمص الشعب", "قهوة ومكسرات", "بن تركي وسط محمش طازج (250 غم)", "قهوة ممتازة بالهيل", 3.50, "كيس", "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300", 0)
        ]
        c.executemany("INSERT INTO products (store_name, category, item_name, description, price, unit_type, image_url, age_restricted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", default_products)
        
        default_drivers = [
            ("معاذ المدادحة", "0799999999", "سياره", "متوفر"),
            ("عمر الكركي", "0798887766", "سيارة هبريد", "متوفر")
        ]
        c.executemany("INSERT INTO drivers (name, phone, vehicle_type, status) VALUES (?, ?, ?, ?)", default_drivers)
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

str_app.sidebar.title("🧡 بوابة الكرك للطلبات")
str_app.sidebar.markdown("---")

portal_options = [
    "👤 تسجيل البيانات الشخصية",
    "🏠 الرئيسية (Talabat Home)",
    "🛒 تصفح المتاجر والسلة والدفع",
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
    str_app.markdown("<h2 style='color: #ff5a00;'>👤 تسجيل بيانات العميل / الزبون</h2>", unsafe_allow_html=True)
    r_name = str_app.text_input("الاسم الكامل:", value=str_app.session_state.customer_name)
    r_phone = str_app.text_input("رقم الهاتف:", value=str_app.session_state.customer_phone)
    r_address = str_app.text_area("العنوان بالتفصيل:", value=str_app.session_state.customer_address)
    
    col_btn1, col_btn2 = str_app.columns([1, 1])
    with col_btn1:
        save_clicked = str_app.button("حفظ وحفظه في النظام 🚀")
    with col_btn2:
        go_home_clicked = str_app.button("🏠 الانتقال إلى الرئيسية والبدء بالتسوق")
        
    if save_clicked or go_home_clicked:
        if r_name.strip() and r_phone.strip():
            c.execute("INSERT OR REPLACE INTO customers (phone, name, address, location) VALUES (?, ?, ?, ?)", 
                      (r_phone, r_name, r_address, "31.2842, 35.7048"))
            conn.commit()
            str_app.session_state.customer_name = r_name
            str_app.session_state.customer_phone = r_phone
            str_app.session_state.customer_address = r_address
            str_app.success("✅ تم حفظ بياناتك بنجاح!")
            
            str_app.session_state.current_portal = "🏠 الرئيسية (Talabat Home)"
            str_app.rerun()
        else:
            str_app.error("يرجى إدخال الاسم ورقم الهاتف.")

elif portal == "🏠 الرئيسية (Talabat Home)":
    str_app.markdown("<h1 style='color: #ff5a00; text-align: center; margin-bottom: 20px;'>بوابة الكرك للطلبات</h1>", unsafe_allow_html=True)
    col_loc, col_prof = str_app.columns([4, 1])
    with col_loc:
        str_app.markdown(f"<h4 style='color: #ff5a00; margin-top: 0;'>📍 {str_app.session_state.customer_address}</h4>", unsafe_allow_html=True)
    with col_prof:
        if str_app.button("👤 تعديل بياناتي"):
            str_app.session_state.current_portal = "👤 تسجيل البيانات الشخصية"
            str_app.rerun()

    c.execute("SELECT DISTINCT category FROM stores")
    cat_stores = [row[0] for row in c.fetchall()]
    categories_list = ["الكل"] + cat_stores
    
    str_app.markdown("#### 📂 أقسام المتاجر السريعة")
    # عرض الأقسام بشكل صف أفقي (Row) متجاور لسهولة الاطلاع المباشر
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
        c.execute("SELECT name, category, delivery_time, delivery_fee, image_url FROM stores")
    else:
        c.execute("SELECT name, category, delivery_time, delivery_fee, image_url FROM stores WHERE category = ?", (selected_cat,))
        
    all_stores = c.fetchall()
    
    if not all_stores:
        str_app.info("لا توجد متاجر متاحة في هذا القسم حالياً.")
    else:
        st_cols = str_app.columns(2)
        for idx, (s_name, s_cat, s_time, s_fee, s_img) in enumerate(all_stores):
            with st_cols[idx % 2]:
                str_app.markdown("<div class='store-card'>", unsafe_allow_html=True)
                if s_img and s_img.startswith("http"):
                    str_app.image(s_img, use_container_width=True)
                else:
                    str_app.markdown("<h1 style='text-align: center; font-size: 40px;'>🏪</h1>", unsafe_allow_html=True)
                str_app.markdown(f"### {s_name}")
                str_app.write(f"🏷️ {s_cat} | ⏱️ {s_time} | 🚚 {s_fee:.2f} JOD")
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
    c.execute("SELECT name, delivery_fee FROM stores")
    stores_data = c.fetchall()
    store_names = [s[0] for s in stores_data]
    store_fees_map = {s[0]: s[1] for s in stores_data}
    
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
                    
                    # خيارات الدفع المحدثة بالكامل
                    pay_method = str_app.selectbox("طريقة الدفع:", [
                        "الدفع نقداً عند الاستلام", 
                        "CliQ - samarza (بنك الاتحاد)", 
                        "CliQ - ميرال (البنك الإسلامي الأردني: 962797088219)"
                    ])
                    
                    submit_order = str_app.form_submit_button("🛒 إرسال الطلب النهائي 🚀")

                if submit_order:
                    if c_name.strip() and c_phone.strip():
                        items_desc_str = ", ".join([f"{i[2]} ({i[4]})" for i in cart_items])
                        c.execute("""
                            INSERT INTO orders (customer_name, customer_phone, customer_address, store_name, items_desc, sub_total, delivery_fee, service_fee, grand_total, payment_method, order_status, assigned_driver)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'جديد (بانتظار الإدارة)', 'لم يُعين بعد')
                        """, (c_name, c_phone, c_addr, chosen_store, items_desc_str, sub_total, current_delivery_fee, service_fee, grand_total, pay_method))
                        
                        conn.commit()
                        
                        # جلب رقم الطلب الأخير لإرساله في رسالة الواتساب
                        c.execute("SELECT last_insert_rowid()")
                        new_order_id = c.fetchone()[0]
                        
                        c.execute("DELETE FROM cart WHERE customer_phone = ?", (str_app.session_state.customer_phone,))
                        conn.commit()
                        
                        str_app.success("🎉 تم إرسال طلبك بنجاح!")
                        
                        # إرسال رسالة واتساب لميرال (962797088219) تلقائياً عند تأكيد الطلب
                        whatsapp_msg = f"طلب جديد # {new_order_id}%0aالزبون: {c_name}%0aالهاتف: {c_phone}%0aالعنوان: {c_addr}%0aالمتجر: {chosen_store}%0aالأصناف: {items_desc_str}%0aالإجمالي: {grand_total:.2f} د.أ%0aطريقة الدفع: {pay_method}"
                        miral_phone = "962797088219"
                        wa_url = f"https://api.whatsapp.com/send?phone={miral_phone}&text={whatsapp_msg}"
                        
                        str_app.markdown(f"### 📲 إرسال تفاصيل الطلب عبر الواتساب لميرال:")
                        str_app.markdown(f"<a href='{wa_url}' target='_blank' style='background-color:#25d366; color:white; padding:10px 20px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;'>📤 اضغط هنا لإرسال تفاصيل الطلب عبر الواتساب لميرال</a>", unsafe_allow_html=True)
                        
                        if str_app.button("🏠 العودة للرئيسية لإضافة طلب آخر"):
                            str_app.session_state.current_portal = "🏠 الرئيسية (Talabat Home)"
                            str_app.rerun()
            else:
                str_app.info("السلة فارغة حالياً. قم بتحديد الكمية واضغط على 'أضف إلى السلة' لكل صنف ترغب به.")

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

        tab1, tab2, tab3, tab4, tab5 = str_app.tabs(["📦 إدارة ومتابعة الطلبات", "🏪 إدارة المتاجر", "🍔 إدارة الأصناف والأسعار", "📥 الاستيراد الآلي (CSV)", "🛵 إدارة السائقين"])
        
        with tab1:
            str_app.markdown("### 🔔 الطلبات الواردة وتوجيهها وإرسالها للبائع:")
            c.execute("SELECT id, customer_name, customer_phone, customer_address, store_name, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders ORDER BY id DESC")
            orders_all = c.fetchall()
            if not orders_all:
                str_app.info("لا توجد طلبات جديدة حالياً.")
            else:
                c.execute("SELECT name, phone FROM drivers")
                drivers_data_all = c.fetchall()
                drivers_list = [d[0] for d in drivers_data_all]
                
                for ord_item in orders_all:
                    oid, ocname, ocphone, ocaddr, ostore, oitems, otot, opay, ostat, odrv = ord_item
                    with str_app.expander(f"طلب رقم #{oid} | متجر: {ostore} | الزبون: {ocname} | الحالة: [{ostat}]"):
                        str_app.write(f"📱 الهاتف: {ocphone} | العنوان: {ocaddr}")
                        str_app.write(f"🛒 الأصناف: {oitems} | الإجمالي: {otot:.2f} د.أ | الدفع: {opay}")
                        
                        # زر إرسال واتساب من الإدارة إلى البائع مباشرة مع التنبيه
                        c.execute("SELECT phone FROM stores WHERE name = ?", (ostore,))
                        st_phone_row = c.fetchone()
                        store_contact_phone = st_phone_row[0] if st_phone_row and st_phone_row[0] else "962790000000"
                        
                        seller_msg = f"طلب جديد رقم #{oid} موجه لمتجركم ({ostore})%0aالزبون: {ocname}%0aالهاتف: {ocphone}%0aالعنوان: {ocaddr}%0aالأصناف المطلوب تجهيزها: {oitems}%0aالمبلغ المطلوب تحصيله: {otot:.2f} د.أ (%0aطريقة الدفع: {opay})%0aيرجى التجهيز الفوري!"
                        seller_wa_url = f"https://api.whatsapp.com/send?phone={store_contact_phone}&text={seller_msg}"
                        
                        str_app.markdown(f"<a href='{seller_wa_url}' target='_blank' style='background-color:#25d366; color:white; padding:8px 15px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:10px;'>📤 إرسال تفاصيل الطلب للبائع عبر الواتساب</a>", unsafe_allow_html=True)
                        
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
            str_app.markdown("### 🏪 إدارة المتاجر:")
            with str_app.form("add_store_form"):
                ns_name = str_app.text_input("اسم المتجر أو المطعم:")
                ns_cat = str_app.text_input("التصنيف (مثال: مطاعم):")
                ns_phone = str_app.text_input("رقم هاتف المتجر (لإرسال الطلبات واتساب):")
                ns_loc = str_app.text_input("العنوان والمنطقة:")
                ns_time = str_app.text_input("وقت التوصيل:", value="15-25 mins")
                ns_fee = str_app.number_input("أجور التوصيل (د.أ):", value=1.50)
                ns_img = str_app.text_input("رابط صورة المتجر (اختياري):")
                
                if str_app.form_submit_button("حفظ المتجر ➕"):
                    if ns_name.strip():
                        c.execute("INSERT OR REPLACE INTO stores (name, category, phone, location, delivery_time, delivery_fee, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (ns_name, ns_cat, ns_phone, ns_loc, ns_time, ns_fee, ns_img))
                        conn.commit()
                        str_app.success(f"✅ تم حفظ المتجر '{ns_name}' بنجاح!")
                        str_app.rerun()
                    else:
                        str_app.error("يرجى إدخال اسم المتجر.")

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
                    p_age = str_app.checkbox("صنف مقيد العمر (مثل التبغ 19+) 🔒")
                    
                    if str_app.form_submit_button("إضافة الصنف 🚀"):
                        if p_name.strip():
                            c.execute("INSERT INTO products (store_name, category, item_name, description, price, unit_type, image_url, age_restricted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                      (p_store, p_cat, p_name, p_desc, p_price, p_unit, p_img, 1 if p_age else 0))
                            conn.commit()
                            str_app.success(f"✅ تمت إضافة الصنف '{p_name}' بنجاح!")
                        else:
                            str_app.error("يرجى إدخال اسم الصنف.")

        with tab4:
            str_app.markdown("### 📥 الاستيراد والتحديث الآلي للأسعار (CSV Import)")
            str_app.markdown("اختر المتجر أولاً لتحديث أصنافه وأسعارها عبر ملف الـ CSV المعرف بالأعمدة: `الاسم`، `السعر`، `الصورة`")
            
            c.execute("SELECT name FROM stores")
            csv_stores_list = [s[0] for s in c.fetchall()]
            target_csv_store = str_app.selectbox("اختر المتجر المراد تحديث أصنافه:", csv_stores_list) if csv_stores_list else None
            
            uploaded_file = str_app.file_uploader("اختر ملف الـ CSV", type=["csv"])
            if uploaded_file is not None and target_csv_store:
                try:
                    df_upload = pd.read_csv(uploaded_file)
                    col_map = {}
                    for col in df_upload.columns:
                        c_clean = str(col).strip().lower()
                        if 'اسم' in c_clean or 'name' in c_clean or 'item' in c_clean:
                            col_map['item_name'] = col
                        elif 'سعر' in c_clean or 'price' in c_clean:
                            col_map['price'] = col
                        elif 'صو' in c_clean or 'image' in c_clean or 'img' in c_clean:
                            col_map['image_url'] = col
                    
                    if 'item_name' in col_map and 'price' in col_map:
                        str_app.write("معاينة سريعة للبيانات المستوردة:", df_upload.head())
                        if str_app.button("🚀 تأكيد وتحديث قاعدة البيانات الآن"):
                            count = 0
                            for _, r in df_upload.iterrows():
                                i_name = str(r[col_map['item_name']])
                                i_price = float(r[col_map['price']])
                                i_img = str(r[col_map['image_url']]) if 'image_url' in col_map else ""
                                
                                c.execute('''
                                    INSERT OR REPLACE INTO products (store_name, category, item_name, description, price, unit_type, image_url)
                                    VALUES (?, 'عام', ?, '', ?, 'وحدة', ?)
                                ''', (target_csv_store, i_name, i_price, i_img))
                                count += 1
                            conn.commit()
                            str_app.success(f"تم تحديث واستيراد {count} صنف لمتجر '{target_csv_store}' بنجاح!")
                            str_app.rerun()
                    else:
                        str_app.error("يجب أن يحتوي ملف الـ CSV على أعمدة تدل على (اسم الصنف) و (السعر).")
                except Exception as e:
                    str_app.error(f"حدث خطأ أثناء قراءة الملف: {e}")

        with tab5:
            str_app.markdown("### 🛵 إدارة السائقين:")
            with str_app.form("add_driver_form"):
                d_name = str_app.text_input("اسم السائق الكامل:")
                d_phone = str_app.text_input("رقم الهاتف:")
                d_veh = str_app.text_input("نوع المركبة:", value="سكوتر توصيل")
                if str_app.form_submit_button("تسجيل السائق ➕"):
                    if d_name.strip():
                        c.execute("INSERT INTO drivers (name, phone, vehicle_type, status) VALUES (?, ?, ?, 'متوفر')", (d_name, d_phone, d_veh))
                        conn.commit()
                        str_app.success(f"✅ تم تسجيل السائق {d_name}!")
                        str_app.rerun()
                    else:
                        str_app.error("يرجى إدخال اسم السائق.")
    elif admin_pass != "":
        str_app.error("رمز سر الإدارة غير صحيح.")

elif portal == "🏪 بوابة المتاجر (تجهيز الطلبات)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🏪 بوابة المتاجر والمطاعم</h2>", unsafe_allow_html=True)
    store_pass = str_app.text_input("أدخل كلمة مرور المتاجر:", type="password")
    if store_pass == "5678":
        c.execute("SELECT name FROM stores")
        stores_opt = [s[0] for s in c.fetchall()]
        my_store = str_app.selectbox("اختر متجرك:", stores_opt) if stores_opt else None
        if my_store:
            c.execute("SELECT COUNT(*) FROM orders WHERE store_name = ? AND order_status LIKE '%جديد%'", (my_store,))
            if c.fetchone()[0] > 0:
                play_sound_alert("https://assets.mixkit.co/active_storage/sfx/2860/2860-preview.mp3")
                str_app.warning("🛎️ تنبيه بوجود طلب جديد موجه لمتجرك!")
            
            c.execute("SELECT id, customer_name, customer_phone, customer_address, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders WHERE store_name = ? ORDER BY id DESC", (my_store,))
            for so in c.fetchall():
                so_id, so_cn, so_cp, so_ca, so_it, so_tot, so_pay, so_st, so_drv = so
                with str_app.expander(f"طلب #{so_id} للزبون {so_cn} | الحالة: [{so_st}]"):
                    str_app.write(f"📱 الهاتف: {so_cp} | العنوان: {so_ca} | الأصناف: {so_it} | الإجمالي: {so_tot:.2f} د.أ | الدفع: {so_pay}")
                    if str_app.button(f"تجهيز الطلب #{so_id}", key=f"prep_store_{so_id}"):
                        c.execute("UPDATE orders SET order_status = 'جاري التجهيز بالمطعم/المتجر' WHERE id = ?", (so_id,))
                        conn.commit()
                        str_app.success("✅ تم تحديث الحالة!")
                        str_app.rerun()

elif portal == "🛵 بوابة السائقين (الاستلام والتوصيل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛵 بوابة السائقين</h2>", unsafe_allow_html=True)
    driver_pass = str_app.text_input("أدخل كلمة مرور السائقين:", type="password")
    if driver_pass == "9988":
        c.execute("SELECT name FROM drivers")
        d_names_list = [d[0] for d in c.fetchall()]
        if d_names_list:
            active_driver = str_app.selectbox("اختر اسمك كساائق:", d_names_list)
            c.execute("SELECT COUNT(*) FROM orders WHERE assigned_driver = ? AND order_status IN ('تم الاعتماد وبانتظار تجهيز المتجر', 'جاري التجهيز بالمطعم/المتجر')", (active_driver,))
            if c.fetchone()[0] > 0:
                play_sound_alert("https://assets.mixkit.co/active_storage/sfx/2354/2354-preview.mp3")
                str_app.warning(f"🚨 تنبيه يا كابتن {active_driver}: تم تعيين طلب جديد لك!")
            
            c.execute("SELECT id, customer_name, customer_phone, customer_address, store_name, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE order_status IN ('تم الاعتماد وبانتظار تجهيز المتجر', 'جاري التجهيز بالمطعم/المتجر', 'مع السائق في طريقه للعميل') ORDER BY id DESC")
            for dro in c.fetchall():
                dro_id, dro_cn, dro_cp, dro_ca, dro_stname, dro_it, dro_tot, dro_stat, dro_assigned = dro
                with str_app.expander(f"طلب رقم #{dro_id} من [{dro_stname}] للزبون {dro_cn} | الحالة: [{dro_stat}]"):
                    str_app.write(f"📍 العنوان: {dro_ca} | الهاتف: {dro_cp} | المبلغ: {dro_tot:.2f} د.أ")
                    col_d1, col_d2 = str_app.columns(2)
                    with col_d1:
                        if str_app.button(f"استلام الطلب والانطلاق #{dro_id}", key=f"take_ord_{dro_id}"):
                            c.execute("UPDATE orders SET order_status = 'مع السائق في طريقه للعميل', assigned_driver = ? WHERE id = ?", (active_driver, dro_id))
                            conn.commit()
                            str_app.success("✅ تم الاستلام والانطلاق!")
                            str_app.rerun()
                    with col_d2:
                        if str_app.button(f"تم التسليم بنجاح #{dro_id}", key=f"done_ord_{dro_id}"):
                            c.execute("UPDATE orders SET order_status = 'تم التسليم بنجاح', assigned_driver = ? WHERE id = ?", (active_driver, dro_id))
                            conn.commit()
                            str_app.success("🎉 تم إغلاق الطلب بنجاح!")
                            str_app.rerun()

conn.close()