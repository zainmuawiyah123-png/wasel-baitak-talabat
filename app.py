import sqlite3
import streamlit as str_app
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
            ("محمص الشعب", "Sweets / محامص", "0798888888", "الكرك - الثنيه", "10-20 mins", 1.00, " https://www.instagram.com/alshaeb.roasters_jordan/ ")
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

str_app.set_page_config(page_title="بوابة الكرك للطلبات المتقدمة", layout="wide", page_icon="🧡")

str_app.markdown("""
    <style>
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
    .talabat-cat-card {
        background-color: #ff5a00;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 10px;
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
""", unsafe_allow_html=True)

str_app.sidebar.title("🧡 بوابة الكرك للطلبات")
str_app.sidebar.markdown("---")

portal = str_app.sidebar.radio("القائمة الرئيسية:", [
    "👤 تسجيل البيانات الشخصية",
    "🏠 الرئيسية (Talabat Home)", 
    "🛒 تصفح المتاجر والسلة والدفع",
    "🔔 لوحة الإدارة المركزية (تحكم كامل)",
    "🏪 بوابة المتاجر (تجهيز الطلبات)",
    "🛵 بوابة السائقين (الاستلام والتوصيل)"
])

if "customer_name" not in str_app.session_state:
    str_app.session_state.customer_name = "بوابة الكرك للطلبات"
    str_app.session_state.customer_address = "الكرك - المرج - بالقرب من جامعة مؤتة"
    str_app.session_state.customer_phone = "0797088219"

conn = get_db_connection()
c = conn.cursor()

if portal == "👤 تسجيل البيانات الشخصية":
    str_app.markdown("<h2 style='color: #ff5a00;'>👤 تسجيل بيانات العميل / الزبون</h2>", unsafe_allow_html=True)
    str_app.write("قم بتحديث بياناتك ليسهل على السائق والمتاجر الوصول إليك بدقة في الكرك.")
    
    r_name = str_app.text_input("الاسم الكامل:", value=str_app.session_state.customer_name)
    r_phone = str_app.text_input("رقم الهاتف:", value=str_app.session_state.customer_phone)
    r_address = str_app.text_area("العنوان بالتفصيل:", value=str_app.session_state.customer_address)
    
    if str_app.button("حفظ وحفظه في النظام 🚀"):
        if r_name.strip() and r_phone.strip():
            c.execute("INSERT OR REPLACE INTO customers (phone, name, address, location) VALUES (?, ?, ?, ?)", 
                      (r_phone, r_name, r_address, "31.2842, 35.7048"))
            conn.commit()
            str_app.session_state.customer_name = r_name
            str_app.session_state.customer_phone = r_phone
            str_app.session_state.customer_address = r_address
            str_app.success("✅ تم حفظ بياناتك بنجاح! انتقل الآن إلى 'الرئيسية' أو 'تصفح المتاجر'.")
        else:
            str_app.error("يرجى إدخال الاسم ورقم الهاتف.")

elif portal == "🏠 الرئيسية (Talabat Home)":
    # عنوان رئيسي بخط كبير في أعلى الصفحة
    str_app.markdown("<h1 style='color: #ff5a00; text-align: center; margin-bottom: 20px;'>بوابة الكرك للطلبات</h1>", unsafe_allow_html=True)

    col_loc, col_prof = str_app.columns([4, 1])
    with col_loc:
        str_app.markdown("<p style='color: gray; margin-bottom: 0; font-size: 13px;'>Deliver to / التوصيل إلى:</p>", unsafe_allow_html=True)
        str_app.markdown(f"<h4 style='color: #ff5a00; margin-top: 0;'>📍 {str_app.session_state.customer_address} ▾</h4>", unsafe_allow_html=True)
    with col_prof:
        str_app.markdown(f"👤 **{str_app.session_state.customer_name}**")

    search_q = str_app.text_input("🔍 Search stores & products...", placeholder="ابحث عن مطعم، مندي، سوبرماركت، دخان، قهوة...")
    
    if search_q.strip():
        str_app.markdown(f"### نتائج البحث عن: `{search_q}`")
        c.execute("SELECT store_name, item_name, description, price, unit_type, image_url, age_restricted FROM products WHERE item_name LIKE ? OR description LIKE ?", (f"%{search_q.strip()}%", f"%{search_q.strip()}%"))
        results = c.fetchall()
        if results:
            for r_store, r_name, r_desc, r_price, r_unit, r_img, r_age in results:
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                rc1, rc2, rc3 = str_app.columns([1, 3, 1])
                with rc1:
                    if r_img:
                        str_app.image(r_img, width=90)
                    else:
                        str_app.markdown("<h1 style='text-align: center; font-size: 40px; margin: 0;'>🛍️</h1>", unsafe_allow_html=True)
                with rc2:
                    if r_age:
                        str_app.markdown("🔒 `19+ years (صنف مقيد العمر)`")
                    str_app.markdown(f"### {r_name}")
                    str_app.write(r_desc)
                    str_app.markdown(f"**JOD {r_price:.2f}** ({r_unit}) | المتجر: `{r_store}`")
                with rc3:
                    if str_app.button("اطلب الآن", key=f"srch_btn_{r_name}"):
                        str_app.session_state.active_store = r_store
                        str_app.success(f"تم الانتقال إلى متجر {r_store}")
                str_app.markdown("</div>", unsafe_allow_html=True)
        else:
            str_app.info("لم يتم العثور على نتائج.")
        str_app.markdown("---")

    str_app.markdown("### الأقسام الرئيسية (Categories)")
    cat_cols = str_app.columns(4)
    categories_data = [
        ("🍔", "Food", "مطاعم ووجبات"),
        ("🚀", "Talabat Mart", "مارت وسريع"),
        ("🛒", "Groceries", "خضار وفواكه"),
        ("🥩", "Stores", "لحوم طازجة بلدي"),
        ("🍰", "Sweets", "كنافه وحلويات"),
        ("💊", "Wellness", "صيدلية وومستلزمات تجميل"),
        ("🛍️", "Pickup", "استلام ذاتي"),
        ("❤️", "Donate", "تبرعات وخيرية")
    ]
    
    for idx, (icon, title_en, title_ar) in enumerate(categories_data):
        with cat_cols[idx % 4]:
            str_app.markdown(f"""
                <div class='talabat-cat-card'>
                    <span style='font-size: 26px;'>{icon}</span>
                    <h4 style='margin: 4px 0 2px 0; color: white; font-size: 14px;'>{title_en}</h4>
                    <p style='color: #f0f0f0; font-size: 11px; margin: 0;'>{title_ar}</p>
                </div>
            """, unsafe_allow_html=True)

    str_app.markdown("---")
    str_app.markdown("### المتاجر والمطاعم المتاحة في الكرك 🛒")
    c.execute("SELECT name, category, delivery_time, delivery_fee, image_url FROM stores")
    all_stores = c.fetchall()
    
    st_cols = str_app.columns(2)
    for idx, (s_name, s_cat, s_time, s_fee, s_img) in enumerate(all_stores):
        with st_cols[idx % 2]:
            str_app.markdown("<div class='store-card'>", unsafe_allow_html=True)
            if s_img:
                str_app.image(s_img, use_container_width=True)
            str_app.markdown(f"### {s_name}")
            str_app.write(f"🏷️ {s_cat}")
            str_app.write(f"⏱️ {s_time} | 🚚 التوصيل: {s_fee:.2f} JOD")
            if str_app.button(f"تصفح متجر {s_name}", key=f"btn_store_home_{idx}"):
                str_app.session_state.active_store = s_name
                str_app.success(f"تم اختيار متجر {s_name}! انتقل إلى قسم 'تصفح المتاجر والسلة'.")
            str_app.markdown("</div>", unsafe_allow_html=True)

elif portal == "🛒 تصفح المتاجر والسلة والدفع":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛒 سلة الطلبات ودفع الفواتير</h2>", unsafe_allow_html=True)
    
    c.execute("SELECT name, delivery_fee FROM stores")
    stores_data = c.fetchall()
    store_names = [s[0] for s in stores_data]
    store_fees_map = {s[0]: s[1] for s in stores_data}
    
    default_st = str_app.session_state.get("active_store", store_names[0] if store_names else "")
    chosen_store = str_app.selectbox("اختر المتجر أو المطعم:", store_names, index=store_names.index(default_st) if default_st in store_names else 0)
    
    if chosen_store:
        str_app.session_state.active_store = chosen_store
        current_delivery_fee = store_fees_map.get(chosen_store, 1.50)
        
        c.execute("SELECT id, item_name, description, price, unit_type, image_url, age_restricted FROM products WHERE store_name = ?", (chosen_store,))
        prods = c.fetchall()
        
        if not prods:
            str_app.info("لا توجد منتجات مسجلة لهذا المتجر حالياً.")
        else:
            str_app.markdown(f"### أصناف متجر `{chosen_store}`:")
            cart_basket = []
            
            for pid, pname, pdesc, pprice, punit, pimg, page_res in prods:
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                col_det, col_img = str_app.columns([3, 1])
                
                with col_det:
                    if page_res:
                        str_app.markdown("🔒 `صنف مقيد (19+)`")
                    str_app.markdown(f"### {pname}")
                    str_app.markdown(f"<h4 style='color: #2c3e50; margin: 2px 0;'>JOD {pprice:.2f}</h4>", unsafe_allow_html=True)
                    str_app.write(pdesc)
                    
                    qty_ord = str_app.number_input(f"الكمية ({punit})", min_value=0.0, step=1.0, key=f"qty_item_{pid}")
                    if qty_ord > 0:
                        cart_basket.append({"name": pname, "price": pprice, "qty": qty_ord, "total": qty_ord * pprice})
                
                with col_img:
                    if pimg:
                        str_app.image(pimg, width=120)
                    else:
                        str_app.markdown("<h1 style='text-align: center; font-size: 45px;'>🛍️</h1>", unsafe_allow_html=True)
                str_app.markdown("</div>", unsafe_allow_html=True)
            
            if cart_basket:
                str_app.markdown("---")
                str_app.markdown("### 🧺 ملخص السلة النهائية والتوصيل:")
                sub_total = sum(i["total"] for i in cart_basket)
                service_fee = 0.25
                grand_total = sub_total + current_delivery_fee + service_fee
                
                for item in cart_basket:
                    str_app.write(f"- {item['name']} × {item['qty']} = **{item['total']:.2f} د.أ**")
                
                str_app.markdown(f"مجموع المشتريات: `{sub_total:.2f} د.أ`")
                str_app.markdown(f"أجور النقل والتوصيل: `{current_delivery_fee:.2f} د.أ`")
                str_app.markdown(f"رسوم الخدمة: `{service_fee:.2f} د.أ`")
                str_app.markdown(f"### 💳 المجموع الإجمالي المطلوب: `{grand_total:.2f} د.أ`")
                
                str_app.markdown("---")
                str_app.markdown("#### بيانات التوصيل والدفع الفوري:")
                with str_app.form("checkout_form_final"):
                    c_name = str_app.text_input("الاسم الكامل:", value=str_app.session_state.customer_name)
                    c_phone = str_app.text_input("رقم الهاتف:", value=str_app.session_state.customer_phone)
                    c_addr = str_app.text_input("عنوان التوصيل بالتفصيل:", value=str_app.session_state.customer_address)
                    
                    pay_method = str_app.selectbox("اختر طريقة الدفع الفوري أو النقدي:", [
                        "الدفع نقداً عند الاستلام (Cash on Delivery)",
                        "CliQ - تحويل فوري (رقم الحساب: 0797088219 - البنك الإسلامي الأردني)",
                        "بنك الاتحاد (samarza - تحويل مالي فوري)"
                    ])
                    
                    submit_order = str_app.form_submit_button("🛒 إرسال الطلب الآن إلى الإدارة والمتجر 🚀")
                    if submit_order:
                        if c_name.strip() and c_phone.strip():
                            items_desc_str = ", ".join([f"{i['name']} ({i['qty']})" for i in cart_basket])
                            
                            c.execute("""
                                INSERT INTO orders (customer_name, customer_phone, customer_address, store_name, items_desc, sub_total, delivery_fee, service_fee, grand_total, payment_method, order_status, assigned_driver)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'جديد (بانتظار الإدارة)', 'لم يُعين بعد')
                            """, (c_name, c_phone, c_addr, chosen_store, items_desc_str, sub_total, current_delivery_fee, service_fee, grand_total, pay_method))
                            conn.commit()
                            
                            str_app.success("🎉 تم إرسال طلبك بنجاح للإدارة والمتاجر والسائقين!")
                            
                            wa_msg = f"🔔 *طلب جديد عبر بوابة الكرك*\n👤 العميل: {c_name}\n📱 الهاتف: {c_phone}\n📍 العنوان: {c_addr}\n🏪 المتجر: {chosen_store}\n📦 المنتجات: {items_desc_str}\n💰 الإجمالي: {grand_total:.2f} د.أ\n💳 طريقة الدفع: {pay_method}"
                            enc_w = urllib.parse.quote(wa_msg)
                            str_app.markdown(f"<a href='https://wa.me/962797088219?text={enc_w}' target='_blank'><button style='background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:6px; font-weight:bold;'>إرسال نسخة الطلب للإدارة عبر واتساب 💬</button></a>", unsafe_allow_html=True)
                        else:
                            str_app.error("الرجاء إدخال الاسم ورقم الهاتف.")

elif portal == "🔔 لوحة الإدارة المركزية (تحكم كامل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🔔 لوحة التحكم المركزية (الإدارة)</h2>", unsafe_allow_html=True)
    admin_pass = str_app.text_input("أدخل رمز سر الإدارة:", type="password")
    
    if admin_pass == "1234":
        str_app.success("تم تسجيل الدخول لصلاحيات الإدارة بنجاح.")
        
        tab1, tab2, tab3, tab4 = str_app.tabs(["📦 إدارة ومتابعة الطلبات", "🏪 إضافة وتعديل المتاجر", "🍔 إضافة أصناف وأسعار", "🛵 إدارة السائقين"])
        
        with tab1:
            str_app.markdown("### 🔔 الطلبات الواردة وتوجيهها:")
            c.execute("SELECT id, customer_name, customer_phone, customer_address, store_name, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders ORDER BY id DESC")
            orders_all = c.fetchall()
            
            if not orders_all:
                str_app.info("لا توجد طلبات جديدة حالياً.")
            else:
                c.execute("SELECT name FROM drivers")
                drivers_list = [d[0] for d in c.fetchall()]
                
                for ord_item in orders_all:
                    oid, ocname, ocphone, ocaddr, ostore, oitems, otot, opay, ostat, odrv = ord_item
                    with str_app.expander(f"طلب رقم #{oid} | متجر: {ostore} | الزبون: {ocname} | الحالة: [{ostat}]"):
                        str_app.write(f"📱 هاتف الزبون: {ocphone} | العنوان: {ocaddr}")
                        str_app.write(f"🛒 الأصناف: {oitems}")
                        str_app.write(f"💰 المجموع الإجمالي: {otot:.2f} د.أ | الدفع: {opay}")
                        str_app.write(f"🛵 السائق الحالي: `{odrv}`")
                        
                        col_st1, col_st2 = str_app.columns(2)
                        with col_st1:
                            new_status = str_app.selectbox(f"تحديث حالة الطلب #{oid}", [
                                "جديد (بانتظار الإدارة)", 
                                "تم الاعتماد وبانتظار تجهيز المتجر", 
                                "جاري التجهيز بالمطعم/المتجر", 
                                "مع السائق في طريقه للعميل", 
                                "تم التسليم بنجاح"
                            ], key=f"admin_st_{oid}")
                        with col_st2:
                            assigned_d = str_app.selectbox(f"تعيين سائق للطلب #{oid}", ["لم يُعين بعد"] + drivers_list, key=f"admin_drv_{oid}")
                        
                        if str_app.button(f"حفظ تحديثات الطلب #{oid}", key=f"save_ord_btn_{oid}"):
                            c.execute("UPDATE orders SET order_status = ?, assigned_driver = ? WHERE id = ?", (new_status, assigned_d, oid))
                            conn.commit()
                            str_app.success(f"✅ تم تحديث الطلب #{oid} وإرسال التنبيه للمتجر والسائق!")
                            str_app.rerun()

        with tab2:
            str_app.markdown("### 🏪 إضافة متجر أو مطعم جديد:")
            with str_app.form("add_store_form"):
                ns_name = str_app.text_input("اسم المتجر أو المطعم الجديد:")
                ns_cat = str_app.text_input("التصنيف (مثال: مطاعم، سوبرماركت، لحوم):")
                ns_phone = str_app.text_input("رقم هاتف المتجر:")
                ns_loc = str_app.text_input("العنوان والمنطقة في الكرك (مثال: المرج):")
                ns_time = str_app.text_input("وقت التوصيل التقريبي (مثال: 15-25 mins):")
                ns_fee = str_app.number_input("أجور التوصيل الافتراضية (د.أ):", value=1.50)
                ns_img = str_app.text_input("رابط صورة المتجر (Image URL):")
                
                if str_app.form_submit_button("إضافة المتجر للنظام ➕"):
                    if ns_name.strip():
                        c.execute("INSERT OR REPLACE INTO stores (name, category, phone, location, delivery_time, delivery_fee, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (ns_name, ns_cat, ns_phone, ns_loc, ns_time, ns_fee, ns_img))
                        conn.commit()
                        str_app.success(f"✅ تمت إضافة المتجر '{ns_name}' بنجاح!")
                        str_app.rerun()
                    else:
                        str_app.error("يرجى إدخال اسم المتجر على الأقل.")

        with tab3:
            str_app.markdown("### 🍔 إضافة منتج أو صنف وأسعاره لأي متجر:")
            c.execute("SELECT name FROM stores")
            st_names_list = [s[0] for s in c.fetchall()]
            
            if st_names_list:
                with str_app.form("add_prod_form"):
                    p_store = str_app.selectbox("اختر المتجر التابع له المنتج:", st_names_list)
                    p_cat = str_app.text_input("قسم الصنف (مثال: وجبات رئيسية، دخان، تموينات):")
                    p_name = str_app.text_input("اسم الصنف (مثال: مندي لحم، كباب، سكر):")
                    p_desc = str_app.text_area("وصف الصنف والتفاصيل:")
                    p_price = str_app.number_input("السعر (بالدينار الأردني):", min_value=0.10, value=2.50)
                    p_unit = str_app.text_input("وحدة القياس (مثال: وجبة، كيلو، كيس، باكيت):", value="وجبة")
                    p_img = str_app.text_input("رابط صورة المنتج (اختياري):")
                    p_age = str_app.checkbox("صنف مقيد العمر (مثل التبغ والدخان 19+) 🔒")
                    
                    if str_app.form_submit_button("إضافة الصنف وتحديث السعر 🚀"):
                        if p_name.strip():
                            c.execute("INSERT INTO products (store_name, category, item_name, description, price, unit_type, image_url, age_restricted) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (p_store, p_cat, p_name, p_desc, p_price, p_unit, p_img, 1 if p_age else 0))
                            conn.commit()
                            str_app.success(f"✅ تم إضافة الصنف '{p_name}' إلى متجر {p_store} بنجاح!")
                            str_app.rerun()
                        else:
                            str_app.error("يرجى إدخال اسم الصنف.")
            else:
                str_app.warning("الرجاء إضافة متاجر أولاً قبل إضافة المنتجات.")

        with tab4:
            str_app.markdown("### 🛵 إضافة سائق جديد للنظام:")
            with str_app.form("add_driver_form"):
                d_name = str_app.text_input("اسم السائق الكامل:")
                d_phone = str_app.text_input("رقم هاتف السائق:")
                d_veh = str_app.text_input("نوع المركبة (سكوتر، سيارة):", value="سكوتر توصيل")
                
                if str_app.form_submit_button("تسجيل السائق ➕"):
                    if d_name.strip():
                        c.execute("INSERT INTO drivers (name, phone, vehicle_type, status) VALUES (?, ?, ?, 'متوفر')", (d_name, d_phone, d_veh))
                        conn.commit()
                        str_app.success(f"✅ تم تسجيل السائق {d_name} بنجاح!")
                        str_app.rerun()
                    else:
                        str_app.error("يرجى إدخال اسم السائق.")
                        
    elif admin_pass != "":
        str_app.error("رمز سر الإدارة غير صحيح.")

elif portal == "🏪 بوابة المتاجر (تجهيز الطلبات)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🏪 بوابة المتاجر والمطاعم (تجهيز الطلبات)</h2>", unsafe_allow_html=True)
    store_pass = str_app.text_input("أدخل كلمة مرور المتاجر:", type="password")
    
    if store_pass == "5678":
        c.execute("SELECT name FROM stores")
        stores_opt = [s[0] for s in c.fetchall()]
        my_store = str_app.selectbox("اختر متجرك لإدارة طلباته:", stores_opt) if stores_opt else None
        
        if my_store:
            str_app.markdown(f"### الطلبات الموجهة إلى متجرك: `{my_store}`")
            c.execute("SELECT id, customer_name, customer_phone, customer_address, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders WHERE store_name = ? ORDER BY id DESC", (my_store,))
            store_ords = c.fetchall()
            
            if not store_ords:
                str_app.info("لا توجد طلبات جديدة حالياً في متجرك.")
            else:
                for so in store_ords:
                    so_id, so_cn, so_cp, so_ca, so_it, so_tot, so_pay, so_st, so_drv = so
                    with str_app.expander(f"طلب رقم #{so_id} للزبون {so_cn} | الحالة: [{so_st}]"):
                        str_app.write(f"📱 الهاتف: {so_cp} | العنوان: {so_ca}")
                        str_app.write(f"🛒 الأصناف المطلوبة: {so_it}")
                        str_app.write(f"💰 المجموع: {so_tot:.2f} د.أ | طريقة الدفع: {so_pay}")
                        str_app.write(f"🛵 السائق المعين: `{so_drv}`")
                        
                        if str_app.button(f"تجهيز الطلب وبدء التحضير #{so_id}", key=f"prep_store_{so_id}"):
                            c.execute("UPDATE orders SET order_status = 'جاري التجهيز بالمطعم/المتجر' WHERE id = ?", (so_id,))
                            conn.commit()
                            str_app.success("✅ تم تحديث حالة الطلب إلى 'جاري التجهيز' وإشعار السائق والإدارة!")
                            str_app.rerun()
    elif store_pass != "":
        str_app.error("كلمة مرور المتاجر خاطئة.")

elif portal == "🛵 بوابة السائقين (الاستلام والتوصيل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛵 بوابة السائقين والكابتن</h2>", unsafe_allow_html=True)
    driver_pass = str_app.text_input("أدخل كلمة مرور السائقين:", type="password")
    
    if driver_pass == "9988":
        c.execute("SELECT name FROM drivers")
        d_names_list = [d[0] for d in c.fetchall()]
        
        if d_names_list:
            active_driver = str_app.selectbox("اختر اسمك كساائق:", d_names_list)
            str_app.success(f"أهلاً بك يا كابتن {active_driver}! إليك الطلبات الجاهزة للاستلام والتوصيل:")
            
            c.execute("SELECT id, customer_name, customer_phone, customer_address, store_name, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE order_status IN ('تم الاعتماد وبانتظار تجهيز المتجر', 'جاري التجهيز بالمطعم/المتجر', 'مع السائق في طريقه للعميل') ORDER BY id DESC")
            driver_orders = c.fetchall()
            
            if not driver_orders:
                str_app.info("لا توجد طلبات جاهزة حالياً.")
            else:
                for dro in driver_orders:
                    dro_id, dro_cn, dro_cp, dro_ca, dro_stname, dro_it, dro_tot, dro_stat, dro_assigned = dro
                    with str_app.expander(f"طلب رقم #{dro_id} من [{dro_stname}] إلى العميل {dro_cn} | الحالة: [{dro_stat}]"):
                        str_app.write(f"📍 عنوان التوصيل: {dro_ca} | هاتف الزبون: {dro_cp}")
                        str_app.write(f"🛒 الأصناف: {dro_it} | المبلغ المطلوب تحصيله: {dro_tot:.2f} د.أ")
                        str_app.write(f"🛵 السائق المعين: `{dro_assigned}`")
                        
                        col_d1, col_d2 = str_app.columns(2)
                        with col_d1:
                            if str_app.button(f"استلام الطلب والانطلاق #{dro_id}", key=f"take_ord_{dro_id}"):
                                c.execute("UPDATE orders SET order_status = 'مع السائق في طريقه للعميل', assigned_driver = ? WHERE id = ?", (active_driver, dro_id))
                                conn.commit()
                                str_app.success("✅ تم استلام الطلب بنجاح وأصبح بحوزتك لتوصيله للزبون!")
                                str_app.rerun()
                        with col_d2:
                            if str_app.button(f"تم تسليم الطلب للزبون بنجاح #{dro_id}", key=f"done_ord_{dro_id}"):
                                c.execute("UPDATE orders SET order_status = 'تم التسليم بنجاح', assigned_driver = ? WHERE id = ?", (active_driver, dro_id))
                                conn.commit()
                                str_app.success("🎉 ممتاز! تم إغلاق الطلب بنجاح وتسجيله كمكتمل.")
                                str_app.rerun()
        else:
            str_app.warning("لم تقم بإضافة سائقين من لوحة الإدارة بعد.")
    elif driver_pass != "":
        str_app.error("كلمة مرور السائقين غير صحيحة.")

conn.close()
