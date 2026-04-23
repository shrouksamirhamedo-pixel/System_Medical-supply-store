import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام مخزن ادويه طبيه", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f0f8ff; }
    .print-receipt { background: white; padding: 20px; border: 2px solid #000; border-radius: 10px; color: black; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "warehouse_system_data_final.json"

def load_all_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # التأكد من وجود البيانات الأساسية والمناديب
            if "allowed_reps" not in data:
                data["allowed_reps"] = {
                    "كريم محمود": "01550778904",
                    "فهمي صقر": "01280687403",
                    "محمود عوض": "01289754213"
                }
    else:
        data = {
            "inventory": {}, "orders": [], 
            "settings": {"low_stock_threshold": 50, "instapay_number": ""},
            "allowed_reps": {
                "كريم محمود": "01550778904",
                "فهمي صقر": "01280687403",
                "محمود عوض": "01289754213"
            },
            "users": {
                "shroukad": {"password": "shroukhamedo710rama", "role": "admin", "blacklisted": False},
                "adamad": {"password": "710reem", "role": "admin", "blacklisted": False},
                "احمد السيد": {"password": "", "role": "employee", "emp_code": "2256", "blacklisted": False},
                "ماجد محمد": {"password": "", "role": "employee", "emp_code": "6983", "blacklisted": False},
                "السيد عبدالعال": {"password": "", "role": "employee", "emp_code": "8731", "blacklisted": False},
                "شيماء حسن": {"password": "", "role": "employee", "emp_code": "7509", "blacklisted": False},
                "يسرا علي": {"password": "", "role": "employee", "emp_code": "5033", "blacklisted": False}
            }
        }
    return data

def save_all_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_all_data()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []

# --- نظام تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🏥 نظام مخزن ادويه طبيه")
    tab_login, tab_signup, tab_rep_reg = st.tabs(["تسجيل دخول", "إنشاء حساب", "تسجيل مندوب استلام"])
    
    with tab_login:
        role = st.selectbox("الدخول كـ", ["عميل", "موظف", "أدمن", "مندوب استلام"])
        u = st.text_input("اسم المستخدم / الاسم", key="login_u")
        p = st.text_input("كلمة السر", type="password", key="login_p")
        ec = st.text_input("كود الموظف") if role == "موظف" else ""
        
        if st.button("دخول"):
            if u in data["users"]:
                user_data = data["users"][u]
                if user_data.get("blacklisted", False):
                    st.error(f"🚫 الحساب محظور. السبب: {user_data.get('blacklist_reason', 'غير محدد')}")
                elif role == "أدمن" and user_data["role"] == "admin":
                    if user_data["password"] == p:
                        st.session_state.update({"logged_in": True, "user": u, "role": "admin"})
                        st.rerun()
                    else: st.error("كلمة السر خطأ")
                elif role == "موظف" and user_data["role"] == "employee":
                    if str(user_data.get("emp_code")) == str(ec):
                        if user_data["password"] == "" or user_data["password"] == p:
                            if user_data["password"] == "": 
                                data["users"][u]["password"] = p
                                save_all_data(data)
                            st.session_state.update({"logged_in": True, "user": u, "role": "employee"})
                            st.rerun()
                        else: st.error("كلمة السر خطأ")
                    else: st.error("كود الموظف غير مطابق")
                elif role == "عميل" and user_data["role"] == "customer":
                    if user_data["password"] == p:
                        st.session_state.update({"logged_in": True, "user": u, "role": "customer"})
                        st.rerun()
                    else: st.error("كلمة السر خطأ")
                elif role == "مندوب استلام" and user_data["role"] == "delivery_rep":
                    if user_data["password"] == p:
                        st.session_state.update({"logged_in": True, "user": u, "role": "delivery_rep"})
                        st.rerun()
                    else: st.error("كلمة السر خطأ")
                else: st.error("نوع الحساب لا يطابق البيانات")
            else: st.error("المستخدم غير موجود")

    with tab_signup:
        s_role = st.selectbox("إنشاء حساب كـ", ["عميل", "موظف", "أدمن"])
        nu = st.text_input("اسم المستخدم الجديد")
        np = st.text_input("كلمة السر الجديدة", type="password")
        nec = ""
        if s_role == "موظف":
            nec = st.text_input("كود الموظف")
        
        if st.button("حفظ الحساب الجديد"):
            if nu and np:
                if s_role == "أدمن" and not nu.endswith("ad"):
                    st.error("اسم الأدمن لازم ينتهي بـ ad")
                elif nu in data["users"]: 
                    st.error("الاسم موجود بالفعل")
                else:
                    role_map = {"عميل": "customer", "موظف": "employee", "أدمن": "admin"}
                    new_user = {"password": np, "role": role_map[s_role], "blacklisted": False}
                    if s_role == "موظف": new_user["emp_code"] = nec
                    data["users"][nu] = new_user
                    save_all_data(data); st.success(f"تم إنشاء حساب {s_role} بنجاح!")
            else: st.warning("أكمل البيانات")

    with tab_rep_reg:
        st.subheader("تسجيل مندوب جديد (باستخدام بيانات الأدمن)")
        ru = st.text_input("الاسم الكامل (كما سجله الأدمن)")
        rp_phone = st.text_input("رقم الهاتف")
        rp_pass = st.text_input("تعيين كلمة سر", type="password")
        if st.button("تسجيل المندوب"):
            if ru in data["allowed_reps"] and data["allowed_reps"][ru] == rp_phone:
                data["users"][ru] = {"password": rp_pass, "role": "delivery_rep", "phone": rp_phone, "blacklisted": False}
                save_all_data(data); st.success("تم تسجيل المندوب بنجاح! يمكنك الآن تسجيل الدخول.")
            else: st.error("البيانات غير متطابقة مع سجلات الشركة")

else:
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.sidebar.button("خروج"): st.session_state.logged_in = False; st.rerun()

    # --- لوحة المندوب ---
    if st.session_state.role == "delivery_rep":
        st.header("🚚 مهام التوصيل الخاصة بك")
        my_tasks = [o for o in data["orders"] if o.get("rec_name") == st.session_state.user]
        if not my_tasks:
            st.info("لا توجد أوردرات محددة لك حالياً")
        for i, o in enumerate(my_tasks):
            with st.expander(f"أوردر العميل: {o['user']} - الحالة: {o['status']}"):
                st.table(pd.DataFrame(o['items']))
                st.write(f"📞 هاتف العميل للتواصل: {o.get('rec_phone', 'غير مسجل')}")
                new_stat = st.selectbox("تحديث حالة التوصيل", ["في الطريق", "تم الوصول"], key=f"rep_stat_{i}")
                if st.button("تحديث الحالة", key=f"rep_btn_{i}"):
                    # تحديث في الداتا الأصلية
                    for idx, order in enumerate(data["orders"]):
                        if order == o:
                            data["orders"][idx]["status"] = new_stat
                            save_all_data(data)
                            st.success("تم التحديث")
                            st.rerun()

    # --- لوحة الإدارة والموظفين ---
    elif st.session_state.role in ["admin", "employee"]:
        tabs_list = ["📊 الإحصائيات", "📦 المخزن", "📑 الطلبات", "➕ الإعدادات"]
        if st.session_state.role == "admin": tabs_list.insert(3, "🚫 القائمة السوداء")
        t = st.tabs(tabs_list)
        
        with t[0]: # الإحصائيات
            limit = data["settings"]["low_stock_threshold"]
            df = pd.DataFrame([{"الدواء": k, "الكمية": v['qty'], "الحالة": "⚠️ عجز" if v['qty'] <= limit else "✅ سليم"} for k, v in data["inventory"].items()])
            st.dataframe(df)

        with t[1]: # المخزن
            st.subheader("📦 إدارة المخزن")
            col1, col2 = st.columns(2)
            with col1:
                mn = st.text_input("اسم الدواء")
                mq = st.number_input("الكمية", min_value=0)
            with col2:
                mp = st.number_input("السعر", min_value=0)
                me = st.date_input("تاريخ الصلاحية")
                if st.button("حفظ بالمخزن"):
                    if mn:
                        data["inventory"][mn] = {"qty": mq, "price": mp, "expiry": str(me)}
                        save_all_data(data); st.success("تم الحفظ")

        with t[2]: # الطلبات
            st.subheader("📑 إدارة طلبات العملاء")
            for i, o in enumerate(data["orders"]):
                with st.expander(f"طلب من: {o['user']} - الحالة: {o['status']}"):
                    st.table(pd.DataFrame(o['items']))
                    st.info(f"💬 تعليق العميل: {o.get('comment', 'لا يوجد تعليق')}")
                    
                    c1, c2 = st.columns(2)
                    # اختيار من المناديب المسجلين
                    rep_options = list(data["allowed_reps"].keys())
                    current_rep = o.get("rec_name", "")
                    rn = c1.selectbox("اختر مندوب الاستلام", rep_options, key=f"rn{i}", 
                                      index=rep_options.index(current_rep) if current_rep in rep_options else 0)
                    rp = c2.text_input("رقم هاتف المستلم", value=data["allowed_reps"].get(rn, ""), key=f"rp{i}")
                    
                    os_val = st.selectbox("تحديث الحالة", ["انتظار", "مقبول", "في الطريق", "تم الوصول"], key=f"os{i}", 
                                         index=["انتظار", "مقبول", "في الطريق", "تم الوصول"].index(o['status']))
                    
                    if st.button("تحديث البيانات", key=f"up{i}"):
                        data["orders"][i].update({"status": os_val, "rec_name": rn, "rec_phone": rp})
                        save_all_data(data); st.success("تم تحديث الأوردر وتوجيهه للمندوب")

        if st.session_state.role == "admin":
            with t[3]: # القائمة السوداء
                st.subheader("🚫 حظر المستخدمين")
                filter_role = st.radio("نوع الحساب للحظر", ["عميل", "موظف"])
                role_key = "customer" if filter_role == "عميل" else "employee"
                
                filtered_users = [u for u, info in data["users"].items() if info['role'] == role_key]
                target = st.selectbox(f"اختر ال{filter_role}", filtered_users)
                
                reason = st.text_area("سبب الحظر", key=f"reason_{target}")
                if st.button("تغيير حالة الحظر"):
                    data["users"][target]["blacklisted"] = not data["users"][target].get("blacklisted", False)
                    data["users"][target]["blacklist_reason"] = reason
                    save_all_data(data); st.rerun()

        with t[-1]: # الإعدادات
            st.subheader("⚙️ الإعدادات")
            if st.session_state.role == "admin":
                col_emp, col_rep = st.columns(2)
                with col_emp:
                    st.markdown("### 👤 إضافة موظف")
                    new_emp_name = st.text_input("اسم الموظف")
                    new_emp_code = st.text_input("كود الموظف")
                    if st.button("تسجيل الموظف"):
                        if new_emp_name and new_emp_code:
                            data["users"][new_emp_name] = {"password": "", "role": "employee", "emp_code": str(new_emp_code), "blacklisted": False}
                            save_all_data(data); st.success("تم إضافة الموظف")
                with col_rep:
                    st.markdown("### 🚚 إضافة مندوب استلام")
                    new_rep_name = st.text_input("اسم المندوب")
                    new_rep_phone = st.text_input("رقم الهاتف المعتمد")
                    if st.button("تسجيل المندوب في السجلات"):
                        if new_rep_name and new_rep_phone:
                            data["allowed_reps"][new_rep_name] = new_rep_phone
                            save_all_data(data); st.success("تم إضافة المندوب للسجلات")
                st.divider()
                data["settings"]["low_stock_threshold"] = st.number_input("حد الإنذار", value=data["settings"]["low_stock_threshold"])
                if st.button("حفظ الإعدادات العامة"): save_all_data(data)
            else:
                st.write(f"كودك: {data['users'][st.session_state.user].get('emp_code')}")
                new_p = st.text_input("تغيير كلمة السر", type="password")
                if st.button("تحديث"):
                    data["users"][st.session_state.user]["password"] = new_p
                    save_all_data(data); st.success("تم")

    else: # لوحة العميل (تظل كما هي مع إظهار المندوب)
        t1, t2, t3 = st.tabs(["🛒 الأدوية", "🛍️ السلة", "🚚 تتبع الأوردر"])
        with t1:
            for k, v in data["inventory"].items():
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{k}** - {v['price']} ج.م")
                if c2.button("أضف", key=f"b_{k}"):
                    st.session_state.cart.append({"الصنف": k, "السعر": v['price'], "العدد": 1})
                    st.toast("تمت الإضافة")
        with t2:
            if st.session_state.cart:
                st.table(pd.DataFrame(st.session_state.cart))
                total = sum(i['السعر'] * i['العدد'] for i in st.session_state.cart)
                st.write(f"إجمالي: {total} ج.م")
                comm = st.text_area("ملاحظات")
                if st.button("تأكيد الطلب"):
                    data["orders"].append({
                        "user": st.session_state.user, "items": st.session_state.cart, 
                        "status": "انتظار", "total": total, "comment": comm, "date": str(datetime.now())
                    })
                    st.session_state.cart = []; save_all_data(data); st.success("تم الطلب")
        with t3:
            my_o = [o for o in data["orders"] if o['user'] == st.session_state.user]
            for o in my_o:
                with st.expander(f"أوردر بتاريخ {o['date'][:16]} - الحالة: {o['status']}"):
                    if o.get("rec_name"):
                        st.success(f"🚚 المندوب المستلم: {o['rec_name']} | 📞 تليفونه: {o['rec_phone']}")
                    st.table(pd.DataFrame(o['items']))