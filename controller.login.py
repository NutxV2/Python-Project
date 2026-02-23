import hashlib
import model

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


def login(username: str, password: str):
    """Login (มีการเช็ค active)"""
    errors = []
    if not username.strip():
        errors.append("กรุณากรอก **ชื่อผู้ใช้**")
    if not password.strip():
        errors.append("กรุณากรอก **รหัสผ่าน**")
    if errors:
        return False, errors, None


    u = model.get_user_auth_row(username)
    if not u:
        return False, ["⚠ ไม่พบบัญชีผู้ใช้นี้ในระบบ"], None


    if u["is_active"] != 1:
        return False, ["⚠ บัญชีนี้ถูกปิดใช้งาน กรุณาติดต่อผู้ดูแลระบบ"], None


    if _hash_password(password) != u["password_hash"]:
        return False, ["⚠ รหัสผ่านไม่ถูกต้อง"], None


    user_info = {"id": u["id"], "username": u["username"], "role": u["role"]}
    return True, ["✅ เข้าสู่ระบบสำเร็จ"], user_info


# -------- Admin actions --------
def create_user(username: str, password: str, role: str, is_active: bool = True):
    errors = []
    if not username.strip():
        errors.append("กรุณากรอก **ชื่อผู้ใช้**")
    if len(username.strip()) < 3:
        errors.append("ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร")
    if not password.strip():
        errors.append("กรุณากรอก **รหัสผ่าน**")
    if len(password.strip()) < 4:
        errors.append("รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร")
    if role not in ("admin", "staff"):
        errors.append("role ต้องเป็น admin หรือ staff")


    if username.strip() and model.is_username_exists(username.strip()):
        errors.append(f"ชื่อผู้ใช้ **{username.strip()}** มีอยู่แล้ว")


    if errors:
        return False, errors


    model.add_user(
        username=username.strip(),
        password_hash=_hash_password(password),
        role=role,
        is_active=1 if is_active else 0
    )
    return True, [f"✅ เพิ่มผู้ใช้ '{username.strip()}' เรียบร้อยแล้ว"]


def set_user_role(user_id: int, new_role: str, current_username: str):
    # กันลดสิทธิ์ตัวเองแบบง่าย ๆ
    if new_role not in ("admin", "staff"):
        return False, ["role ต้องเป็น admin หรือ staff"]


    users_df = model.get_all_users()
    me = users_df[users_df["username"] == current_username]
    if not me.empty and int(me.iloc[0]["id"]) == int(user_id) and new_role != "admin":
        return False, ["ไม่อนุญาตให้ลดสิทธิ์ของผู้ดูแลระบบที่กำลังล็อกอินอยู่"]


    model.update_user_role(int(user_id), new_role)
    return True, ["✅ เปลี่ยน role เรียบร้อยแล้ว"]


def set_user_active(user_id: int, is_active: bool, current_username: str):
    # กันปิดตัวเอง
    users_df = model.get_all_users()
    me = users_df[users_df["username"] == current_username]
    if not me.empty and int(me.iloc[0]["id"]) == int(user_id) and (not is_active):
        return False, ["ไม่อนุญาตให้ปิดใช้งานบัญชีที่กำลังล็อกอินอยู่"]


    model.update_user_active(int(user_id), 1 if is_active else 0)
    return True, ["✅ เปลี่ยนสถานะผู้ใช้เรียบร้อยแล้ว"]


