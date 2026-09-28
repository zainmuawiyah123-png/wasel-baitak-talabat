import streamlit as str_app
import os

# محاولة استيراد مكتبات قاعدة البيانات والدعم
try:
    import sqlite3
except ImportError:
    sqlite3 = None

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

# إعداد واجهة الصفحة
str_app.set_page_config(
    page_title="بوابة الكرك للطلبات - Wasel Talabat Pro",
    page_icon="🛒",
    layout="wide"
)

# تخصيص التصميم والأنماط (CSS)
str_app.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #ff5a00;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .product-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# إعداد قاعدة البيانات (يدعم SQLite أو PostgreSQL عبر DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")

def init_db():
    if HAS_SQLALCHEMY and DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stores (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE,
                    category TEXT,
                    phone TEXT,
                    location TEXT,
                    delivery_fee REAL,
                    pin_code TEXT
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS drivers (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE,
                    phone TEXT,
                    vehicle_type TEXT,
                    status TEXT,
                    pin_code TEXT
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_name TEXT,
                    customer_phone TEXT,
                    customer_address TEXT,
                    customer_lat REAL,
                    customer_lon REAL,
                    store_name TEXT,
                    store_lat REAL,
                    store_lon REAL,
                    items_desc TEXT,
                    grand_total REAL,
                    payment_method TEXT,
                    order_status TEXT,
                    assigned_driver TEXT
                )
            """))
    else:
        if sqlite3:
            conn = sqlite3.connect("wasel_talabat_pro.db", check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    category TEXT,
                    phone TEXT,
                    location TEXT,
                    delivery_fee REAL,
                    pin_code TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    phone TEXT,
                    vehicle_type TEXT,
                    status TEXT,
                    pin_code TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT,
                    customer_phone TEXT,
                    customer_address TEXT,
                    customer_lat REAL,
                    customer_lon REAL,
                    store_name TEXT,
                    store_lat REAL,
                    store_lon REAL,
                    items_desc TEXT,
                    grand_total REAL,
                    payment_method TEXT,
                    order_status TEXT,
                    assigned_driver TEXT
                )
            """)
            conn.commit()
            conn.close()

init_db()

def db_query(query, params=None, fetch=True, commit=False):
    if HAS_SQLALCHEMY and DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        with engine.begin() as conn:
            res = conn.execute(text(query), params or {})
            if fetch:
                return res.fetchall()
            return None
    else:
        if sqlite3:
            conn = sqlite3.connect("wasel_talabat_pro.db", check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if commit:
                conn.commit()
                res = None
            else:
                res = cursor.fetchall()
            conn.close()
            return res
        return []

# إدخال بيانات أولية افتراضية للمتاجر والسائقين إذا كانت الجداول فارغة
def seed_initial_data():
    stores_check = db_query("SELECT COUNT(*) FROM stores")
    if stores_check and stores_check[0][0] == 0:
        default_stores = [
            ("مطعم المنسف الكركي الأصيل", "مأكولات شعبية", "0790001111", "الكرك - الثنية", 1.5, "1111"),
            ("حلويات الكرك العريقة", "حلويات", "0780002222", "الكرك - المرج", 1.0, "1111"),
            ("سوبرماركت البركة", "بقالة ومواد غذائية", "0770003333", "الكرك - الثنية", 0.75, "1111")
        ]
        for s in default_stores:
            if HAS_SQLALCHEMY and DATABASE_URL:
                db_query("INSERT INTO stores (name, category, phone, location, delivery_fee, pin_code) VALUES (:n, :c, :p, :l, :d, :pin)",
                         {"n": s[0], "c": s[1], "p": s[2], "l": s[3], "d": s[4], "pin": s[5]}, fetch=False, commit=True)
            else:
                db_query("INSERT INTO stores (name, category, phone, location, delivery_fee, pin_code) VALUES (?, ?, ?, ?, ?, ?)", s, fetch=False, commit=True)

    drivers_check = db_query("SELECT COUNT(*) FROM drivers")
    if drivers_check and drivers_check[0][0] == 0:
        default_drivers = [
            ("أحمد المجالي", "0791112233", "دراجة نارية", "متوفر", "2222"),
            ("عمر الحمايدة", "0782223344", "سيارة صغيرة", "متوفر", "2222")
        ]
        for d in default_drivers:
            if HAS_SQLALCHEMY and DATABASE_URL:
                db_query("INSERT INTO drivers (name, phone, vehicle_type, status, pin_code) VALUES (:n, :p, :v, :s, :pin)",
                         {"n": d[0], "p": d[1], "v": d[2], "s": d[3], "pin": d[4]}, fetch=False, commit=True)
            else:
                db_query("INSERT INTO drivers (name, phone, vehicle_type, status, pin_code) VALUES (?, ?, ?, ?, ?)", d, fetch=False, commit=True)

seed_initial_data()

def play_sound_alert():
    str_app.markdown('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mp3"></audio>', unsafe_allow_html=True)

# رأس التطبيق
str_app.markdown("<h1 class='main-header'>🛒 بوابة الكرك للطلبات (Wasel Talabat Pro)</h1>", unsafe_allow_html=True)
str_app.markdown("<p style='text-align: center; color: #555;'>منصتك المحلية المتكاملة لتوصيل الطلبات في محافظة الكرك 🇯🇴</p>", unsafe_allow_html=True)

# الشريط الجانبي للتنقل بين الأقسام
portal = str_app.sidebar.radio("اختر البوابة أو القسم:", [
    "🛍️ تصفح المتاجر وطلب الأكل",
    "📦 تتبع طلباتي الحالية",
    "🔔 لوحة الإدارة المركزية (تحكم كامل)",
    "🏪 بوابة المتاجر (تجهيز الطلبات)",
    "🛵 بوابة السائقين (الاستلام والتوصيل)"
])

# 1. قسم تصفح المتاجر وطلب الأكل
if portal == "🛍️ تصفح المتاجر وطلب الأكل":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛍️ المتاجر المتاحة في الكرك</h2>", unsafe_allow_html=True)
    
    stores_data = db_query("SELECT name, category, phone, location, delivery_fee FROM stores")
    
    if not stores_data:
        str_app.info("لا توجد متاجر مضافة حالياً.")
    else:
        selected_store = str_app.selectbox("اختر المتجر أو المطعم لطلب المنتجات:", [s[0] for s in stores_data])
        
        store_info = [s for s in stores_data if s[0] == selected_store][0]
        str_app.write(f"🏷️ **التصنيف:** {store_info[1]} | 📍 **الموقع:** {store_info[3]} | 🛵 **رسوم التوصيل:** {store_info[4]} د.أ")
        
        str_app.markdown("---")
        str_app.markdown("### 📝 تفاصيل الطلب وبيانات التوصيل")
        
        with str_app.form("order_form"):
            c_name = str_app.text_input("الاسم الكامل:")
            c_phone = str_app.text_input("رقم الهاتف (للتواصل والتتبع):")
            c_address = str_app.text_area("عنوان التوصيل بالتفصيل (مثال: الثنية، قرب جامعة مؤتة):")
            
            # إحداثيات افتراضية لمدينتي الكرك ومؤتة
            c_lat = str_app.number_input("خط العرض (Latitude) للعميل:", value=31.1852)
            c_lon = str_app.number_input("خط الطول (Longitude) للعميل:", value=35.7048)
            
            items_desc = str_app.text_area("الأصناف المطلوبة (اكتب ما تحتاجه بالتفصيل):")
            est_price = str_app.number_input("التكلفة التقديرية للأصناف (بالدينار الأردني):", min_value=0.5, value=5.0)
            
            payment_method = str_app.selectbox("طريقة الدفع:", ["الدفع النقدي عند الاستلام (Cash)", "زين كاش (Zain Cash)"])
            
            submit_order = str_app.form_submit_button("🚀 إرسال الطلب الآن")
            
            if submit_order:
                if not c_name or not c_phone or not items_desc:
                    str_app.error("❌ يرجى تعبئة الحقول الأساسية (الاسم، الهاتف، والأصناف المطلوبة).")
                else:
                    grand_total = est_price + store_info[4]
                    initial_status = "جديد (بانتظار الإدارة)"
                    default_driver = "لم يُعين بعد"
                    
                    # إحداثيات افتراضية للمتجر
                    s_lat, s_lon = 31.1800, 35.7000
                    
                    if HAS_SQLALCHEMY and DATABASE_URL:
                        db_query("""
                            INSERT INTO orders (customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, payment_method, order_status, assigned_driver)
                            VALUES (:cn, :cp, :ca, :clat, :clon, :sn, :slat, :slon, :idesc, :gtot, :pm, :st, :dr)
                        """, {
                            "cn": c_name, "cp": c_phone, "ca": c_address, "clat": c_lat, "clon": c_lon,
                            "sn": selected_store, "slat": s_lat, "slon": s_lon, "idesc": items_desc,
                            "gtot": grand_total, "pm": payment_method, "st": initial_status, "dr": default_driver
                        }, fetch=False, commit=True)
                    else:
                        db_query("""
                            INSERT INTO orders (customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, payment_method, order_status, assigned_driver)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (c_name, c_phone, c_address, c_lat, c_lon, selected_store, s_lat, s_lon, items_desc, grand_total, payment_method, initial_status, default_driver), fetch=False, commit=True)
                    
                    str_app.success("🎉 تم إرسال طلبك بنجاح! يمكنك تتبع حالة الطلب من قسم 'تتبع طلباتي الحالية'.")
                    play_sound_alert()

# 2. قسم تتبع الطلبات الحالية للعميل
elif portal == "📦 تتبع طلباتي الحالية":
    str_app.markdown("<h2 style='color: #ff5a00;'>📦 تتبع طلباتك النشطة</h2>", unsafe_allow_html=True)
    cust_phone_track = str_app.text_input("أدخل رقم هاتفك للبحث عن طلباتك:")
    
    if cust_phone_track:
        if HAS_SQLALCHEMY and DATABASE_URL:
            my_orders = db_query("SELECT id, store_name, store_lat, store_lon, customer_lat, customer_lon, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE customer_phone = :phone", {"phone": cust_phone_track.strip()})
        else:
            my_orders = db_query("SELECT id, store_name, store_lat, store_lon, customer_lat, customer_lon, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE customer_phone = ?", (cust_phone_track.strip(),))
        
        if not my_orders:
            str_app.info("لا توجد طلبات مسجلة لهذا الرقم حالياً.")
        else:
            for oid, ost_name, ost_lat, ost_lon, oc_lat, oc_lon, odesc, otot, ostatus, odriver in my_orders:
                str_app.markdown("<div class='product-card'>", unsafe_allow_html=True)
                str_app.markdown(f"### 📦 الطلب رقم #{oid} - المتجر: `{ost_name}`")
                str_app.write(f"📝 **الأصناف:** {odesc}")
                str_app.write(f"💰 **المجموع الإجمالي:** {otot:.2f} د.أ")
                str_app.write(f"🚚 **السائق المعين:** {odriver}")
                
                if "جديد" in ostatus:
                    str_app.warning(f"حالة الطلب: {ostatus}")
                elif "جارٍ" in ostatus or "التوصيل" in ostatus or "قيد التجهيز" in ostatus:
                    str_app.info(f"حالة الطلب: {ostatus}")
                else:
                    str_app.success(f"حالة الطلب: {ostatus}")
                
                store_map = f"https://maps.google.com/?q={ost_lat},{ost_lon}"
                cust_map = f"https://maps.google.com/?q={oc_lat},{oc_lon}"
                str_app.markdown(f"📍 **موقع المتجر:** [<a href='{store_map}' target='_blank'>فتح على الخريطة</a>] | 📍 **موقع التوصيل الخاص بك:** [<a href='{cust_map}' target='_blank'>فتح على الخريطة</a>]", unsafe_allow_html=True)
                str_app.markdown("</div>", unsafe_allow_html=True)

# 3. لوحة الإدارة المركزية
elif portal == "🔔 لوحة الإدارة المركزية (تحكم كامل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🔔 لوحة الإدارة المركزية</h2>", unsafe_allow_html=True)
    admin_pin = str_app.text_input("أدخل رمز المرور الإداري:", type="password")
    
    if admin_pin == "1234":
        str_app.success("✅ تم تسجيل الدخول بنجاح إلى لوحة الإدارة.")
        play_sound_alert()
        
        tab1, tab2, tab3 = str_app.tabs(["📦 إدارة الطلبات", "🏪 إدارة المتاجر", "🛵 إدارة السائقين"])
        
        with tab1:
            str_app.markdown("### كافة الطلبات الواردة")
            all_ords = db_query("SELECT id, customer_name, customer_phone, store_name, items_desc, grand_total, payment_method, order_status, assigned_driver FROM orders ORDER BY id DESC")
            if not all_ords:
                str_app.info("لا توجد طلبات حتى الآن.")
            else:
                for ord_item in all_ords:
                    oid, cname, cphone, sname, idesc, gtot, pmethod, ostatus, adriver = ord_item
                    with str_app.expander(f"الطلب #{oid} - الزبون: {cname} ({sname}) - الحالة: {ostatus}"):
                        str_app.write(f"📞 هاتف الزبون: {cphone}")
                        str_app.write(f"🛒 الأصناف: {idesc}")
                        str_app.write(f"💳 الإجمالي: {gtot:.2f} د.أ | طريقة الدفع: {pmethod}")
                        
                        drivers_res = db_query("SELECT name FROM drivers WHERE status = 'متوفر'")
                        avail_drivers = [d[0] for d in drivers_res]
                        avail_drivers_list = ["لم يُعين بعد"] + avail_drivers
                        
                        try:
                            default_drv_index = avail_drivers_list.index(adriver)
                        except ValueError:
                            default_drv_index = 0
                            
                        chosen_drv = str_app.selectbox(f"تعيين سائق للطلب #{oid}", avail_drivers_list, index=default_drv_index, key=f"drv_sel_{oid}")
                        
                        status_options = [
                            "جديد (بانتظار الإدارة)",
                            "قيد التجهيز في المتجر",
                            "تم الاستلام من قبل السائق وجارٍ التوصيل",
                            "تم التوصيل بنجاح",
                            "ملغي"
                        ]
                        try:
                            default_st_index = status_options.index(ostatus)
                        except ValueError:
                            default_st_index = 0
                            
                        new_status = str_app.selectbox(f"تحديث حالة الطلب #{oid}", status_options, index=default_st_index, key=f"st_sel_{oid}")
                        
                        if str_app.button(f"حفظ التعديلات للطلب #{oid}", key=f"save_ord_{oid}"):
                            if HAS_SQLALCHEMY and DATABASE_URL:
                                db_query("UPDATE orders SET order_status = :st, assigned_driver = :dr WHERE id = :id", {"st": new_status, "dr": chosen_drv, "id": oid}, fetch=False, commit=True)
                            else:
                                db_query("UPDATE orders SET order_status = ?, assigned_driver = ? WHERE id = ?", (new_status, chosen_drv, oid), fetch=False, commit=True)
                            str_app.success(f"✅ تم تحديث الطلب #{oid} بنجاح!")
                            str_app.rerun()
                            
        with tab2:
            str_app.markdown("### إدارة المتاجر والمطاعم")
            stores_list_admin = db_query("SELECT name, category, phone, location, delivery_fee FROM stores")
            for st_row in stores_list_admin:
                str_app.write(f"- 🏪 **{st_row[0]}** ({st_row[1]}) - الهاتف: {st_row[2]} - الموقع: {st_row[3]} - رسوم التوصيل: {st_row[4]} د.أ")
                
        with tab3:
            str_app.markdown("### إدارة السائقين")
            drivers_list_admin = db_query("SELECT id, name, phone, vehicle_type, status FROM drivers")
            for dr_row in drivers_list_admin:
                str_app.write(f"- 🛵 **{dr_row[1]}** - هاتف: {dr_row[2]} - المركبة: {dr_row[3]} - الحالة: {dr_row[4]}")
                
    elif admin_pin:
        str_app.error("❌ رمز المرور الإداري غير صحيح (رمز الافتراضي للإدارة هو 1234).")

# 4. بوابة المتاجر
elif portal == "🏪 بوابة المتاجر (تجهيز الطلبات)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🏪 بوابة المتاجر والمطاعم</h2>", unsafe_allow_html=True)
    stores_res = db_query("SELECT name, pin_code FROM stores")
    store_dict = {s[0]: s[1] for s in stores_res}
    
    if store_dict:
        selected_store_portal = str_app.selectbox("اختر المتجر الخاص بك:", list(store_dict.keys()))
        entered_pin = str_app.text_input("أدخل رمز PIN الخاص بالمتجر:", type="password")
        
        if entered_pin and selected_store_portal:
            if entered_pin == store_dict.get(selected_store_portal, "1111"):
                str_app.success(f"✅ أهلاً بك في لوحة تحكم متجر {selected_store_portal}")
                
                if HAS_SQLALCHEMY and DATABASE_URL:
                    store_orders = db_query("SELECT id, customer_name, customer_phone, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE store_name = :st ORDER BY id DESC", {"st": selected_store_portal})
                else:
                    store_orders = db_query("SELECT id, customer_name, customer_phone, items_desc, grand_total, order_status, assigned_driver FROM orders WHERE store_name = ? ORDER BY id DESC", (selected_store_portal,))
                    
                if not store_orders:
                    str_app.info("لا توجد طلبات واردة لهذا المتجر حالياً.")
                else:
                    for so in store_orders:
                        so_id, so_cname, so_cphone, so_idesc, so_gtot, so_status, so_drv = so
                        with str_app.expander(f"طلب رقم #{so_id} للزبون {so_cname} - الحالة: {so_status}"):
                            str_app.write(f"📞 الهاتف: {so_cphone}")
                            str_app.write(f"🛒 الأصناف المطلوبة: {so_idesc}")
                            str_app.write(f"💵 المجموع: {so_gtot:.2f} د.أ | السائق: {so_drv}")
                            
                            next_st = str_app.selectbox(f"تحديث حالة الطلب #{so_id}", [
                                "قيد التجهيز في المتجر",
                                "جاهز للاستلام من قبل السائق"
                            ], key=f"store_st_{so_id}")
                            
                            if str_app.button(f"تحديث حالة الطلب #{so_id} للمتجر", key=f"btn_store_upd_{so_id}"):
                                if HAS_SQLALCHEMY and DATABASE_URL:
                                    db_query("UPDATE orders SET order_status = :st WHERE id = :id", {"st": next_st, "id": so_id}, fetch=False, commit=True)
                                else:
                                    db_query("UPDATE orders SET order_status = ? WHERE id = ?", (next_st, so_id), fetch=False, commit=True)
                                str_app.success("✅ تم التحديث بنجاح!")
                                str_app.rerun()
            else:
                str_app.error("❌ رمز PIN غير صحيح.")

# 5. بوابة السائقين
elif portal == "🛵 بوابة السائقين (الاستلام والتوصيل)":
    str_app.markdown("<h2 style='color: #ff5a00;'>🛵 بوابة السائقين</h2>", unsafe_allow_html=True)
    drivers_res = db_query("SELECT name, pin_code FROM drivers")
    driver_dict = {d[0]: d[1] for d in drivers_res}
    
    if driver_dict:
        chosen_driver_name = str_app.selectbox("اختر اسم السائق:", list(driver_dict.keys()))
        driver_pin = str_app.text_input("أدخل رمز PIN الخاص بالسائق:", type="password")
        
        if driver_pin and chosen_driver_name:
            if driver_pin == driver_dict.get(chosen_driver_name, "2222"):
                str_app.success(f"✅ أهلاً بك كابتن {chosen_driver_name}")
                
                if HAS_SQLALCHEMY and DATABASE_URL:
                    assigned_orders = db_query("SELECT id, customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, order_status FROM orders WHERE assigned_driver = :dr ORDER BY id DESC", {"dr": chosen_driver_name})
                else:
                    assigned_orders = db_query("SELECT id, customer_name, customer_phone, customer_address, customer_lat, customer_lon, store_name, store_lat, store_lon, items_desc, grand_total, order_status FROM orders WHERE assigned_driver = ? ORDER BY id DESC", (chosen_driver_name,))
                    
                if not assigned_orders:
                    str_app.info("لا توجد طلبات مسندة إليك حالياً.")
                else:
                    for ao in assigned_orders:
                        ao_id, ao_cname, ao_cphone, ao_caddr, ao_clat, ao_clon, ao_sname, ao_slat, ao_slon, ao_idesc, ao_gtot, ao_status = ao
                        with str_app.expander(f"طلب توصيل رقم #{ao_id} من {ao_sname} للزبون {ao_cname}"):
                            str_app.write(f"📞 هاتف الزبون: {ao_cphone} | العنوان: {ao_caddr}")
                            str_app.write(f"🛒 الأصناف: {ao_idesc}")
                            str_app.write(f"💵 التحصيل المطلوب: {ao_gtot:.2f} د.أ")
                            
                            s_map = f"https://maps.google.com/?q={ao_slat},{ao_slon}"
                            c_map = f"https://maps.google.com/?q={ao_clat},{ao_clon}"
                            str_app.markdown(f"📍 **موقع المتجر (الاستلام):** [<a href='{s_map}' target='_blank'>خريطة المتجر</a>] | 📍 **موقع الزبون (التوصيل):** [<a href='{c_map}' target='_blank'>خريطة الزبون</a>]", unsafe_allow_html=True)
                            
                            drv_update_status = str_app.selectbox(f"تحديث حالة الطلب #{ao_id}", [
                                "تم الاستلام من قبل السائق وجارٍ التوصيل",
                                "تم التوصيل بنجاح"
                            ], key=f"drv_st_{ao_id}")
                            
                            if str_app.button(f"تحديث الحالة للسائق #{ao_id}", key=f"btn_drv_upd_{ao_id}"):
                                if HAS_SQLALCHEMY and DATABASE_URL:
                                    db_query("UPDATE orders SET order_status = :st WHERE id = :id", {"st": drv_update_status, "id": ao_id}, fetch=False, commit=True)
                                else:
                                    db_query("UPDATE orders SET order_status = ? WHERE id = ?", (drv_update_status, ao_id), fetch=False, commit=True)
                                str_app.success("✅ تم تحديث حالة الطلب بنجاح!")
                                str_app.rerun()
            else:
                str_app.error("❌ رمز PIN السائق غير صحيح.")