import streamlit as st
import model
import controller

# =========================
# View helpers (reset form)
# =========================

def reset_member_form():
    st.session_state["member_code"] = ""
    st.session_state["member_name"] = ""
    st.session_state["gender"] = "ไม่ระบุ"
    st.session_state["member_email"] = ""
    st.session_state["member_phone"] = ""


def on_save_member():
    code = st.session_state.get("member_code", "")
    name = st.session_state.get("member_name", "")
    gender = st.session_state.get("gender", "ไม่ระบุ")
    email = st.session_state.get("member_email", "")
    phone = st.session_state.get("member_phone", "")

    ok, msgs = controller.create_member(code, name, gender, email, phone)
    if not ok:
        for m in msgs:
            st.error(m)
    else:
        for m in msgs:
            st.success(m)
        reset_member_form()


# =========================
# UI
# =========================
def render_member():
    # -------- Member: Create --------
    st.subheader("เพิ่มข้อมูลสมาชิกใหม่")
    st.text_input("รหัสสมาชิก", key="member_code")
    st.text_input("ชื่อสมาชิก", key="member_name")
    st.selectbox("เพศ", ["ไม่ระบุ", "ชาย", "หญิง"], key="gender")
    st.text_input("อีเมล", key="member_email")
    st.text_input("เบอร์โทรศัพท์", key="member_phone")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.button("บันทึกข้อมูลสมาชิก", on_click=on_save_member)
    with col2:
        st.button("ล้างฟอร์ม", on_click=reset_member_form)

    # -------- Member: Read --------
    st.subheader("👤 รายการสมาชิกทั้งหมดในระบบ")
    members_df = model.fetch_members()
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลสมาชิกในระบบ")
    else:
        st.dataframe(members_df, use_container_width=True)

    # -------- Member: Delete --------
    st.subheader("🗑 ลบข้อมูลสมาชิก")
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลสมาชิกในระบบ")
    else:
        for _, row in members_df.iterrows():
            c1, c2, c3 = st.columns([4, 3, 1])
            with c1:
                st.write(f"👤 **{row['name']}** ({row['member_code']})")
            with c2:
                st.write(f"{row['email']} | {row['phone']}")
            with c3:
                if st.button("ลบ", key=f"delete_member_{row['id']}"):
                    controller.remove_member(int(row["id"]))
                    st.success("ลบข้อมูลสมาชิกเรียบร้อยแล้ว")
                    st.rerun()

    # -------- Member: Update --------
    st.subheader("✏️ แก้ไขข้อมูลสมาชิก")
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลให้แก้ไข")
    else:
        search_name = st.text_input("ค้นหาชื่อสมาชิก", key="search_member_name")

        if search_name.strip():
            filtered_df = members_df[
                members_df["name"].str.contains(search_name.strip(), case=False)
            ]
        else:
            filtered_df = members_df

        if filtered_df.empty:
            st.warning("ไม่พบสมาชิกตามคำค้นหา")
        else:
            options = [
                f"{row['id']} - {row['name']}"
                for _, row in filtered_df.iterrows()
            ]
            selected = st.selectbox("เลือกสมาชิกที่จะแก้ไข", options)

            member_id = int(selected.split(" - ")[0])
            row = members_df[members_df["id"] == member_id].iloc[0]

            with st.form("edit_member_form"):
                new_code = st.text_input("รหัสสมาชิก", value=row["member_code"])
                new_name = st.text_input("ชื่อสมาชิก", value=row["name"])
                new_gender = st.selectbox(
                    "เพศ", ["ไม่ระบุ", "ชาย", "หญิง"],
                    index=["ไม่ระบุ", "ชาย", "หญิง"].index(row["gender"])
                )
                new_email = st.text_input("อีเมล", value=row["email"])
                new_phone = st.text_input("เบอร์โทรศัพท์", value=row["phone"])
                save = st.form_submit_button("บันทึกการแก้ไข")

            if save:
                ok, msgs = controller.edit_member(
                    member_id, new_code, new_name, new_gender, new_email, new_phone
                )
                if not ok:
                    for m in msgs:
                        st.error(m)
                else:
                    for m in msgs:
                        st.success(m)
                    st.rerun()