import sqlite3
import hashlib   # 👈 ต้องมี


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


# 1. เชื่อมต่อ (หรือสร้างไฟล์ถ้าไม่มี)
conn = sqlite3.connect("library.db")
c = conn.cursor()
# 2. สร้างตาราง books ถ้ายังไม่มี
c.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT DEFAULT 'available'
)
""")


c.execute("""
CREATE TABLE IF NOT EXISTS members (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    member_code  TEXT NOT NULL UNIQUE,        -- รหัสสมาชิก เช่น M001
    name         TEXT NOT NULL,              -- ชื่อ - สกุล
    gender       TEXT,                       -- เพศ (หญิง/ชาย/อื่น ๆ)
    email        TEXT UNIQUE,                -- อีเมล (ไม่จำเป็น แต่ถ้ามีให้ไม่ซ้ำ)
    phone        TEXT,                       -- เบอร์โทร
    is_active    INTEGER DEFAULT 1,          -- สถานะการใช้งาน 1=ใช้งาน, 0=ยกเลิก
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);
""")


# -------------------------
# users (NEW)   เพิ่มส่วนนี้ 
# -------------------------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin','staff')),
    is_active INTEGER NOT NULL DEFAULT 1
)
""")

# -------------------------
# borrow system (NEW)
# -------------------------
c.execute("""
CREATE TABLE IF NOT EXISTS borrow_tx (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  member_id INTEGER NOT NULL,
  staff_user_id INTEGER NOT NULL,
  borrow_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  default_due_date TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  note TEXT,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (staff_user_id) REFERENCES users(id)
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS borrow_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tx_id INTEGER NOT NULL,
  book_id INTEGER NOT NULL,
  due_date TEXT,
  return_date TEXT,
  status TEXT NOT NULL DEFAULT 'borrowed',
  return_staff_user_id INTEGER,
  FOREIGN KEY (tx_id) REFERENCES borrow_tx(id),
  FOREIGN KEY (book_id) REFERENCES books(id),
  FOREIGN KEY (return_staff_user_id) REFERENCES users(id)
)
""")

c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_tx ON borrow_items(tx_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_book ON borrow_items(book_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_status ON borrow_items(status)")

# seed admin (ถ้ายังไม่มี user เลย)  เพิ่มส่วนนี้ 
c.execute("SELECT COUNT(*) FROM users")
(count,) = c.fetchone()
if count == 0:
    c.execute(
        "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
        ("admin", hash_password("1234"), "admin", 1)
    )
# 3. บันทึกการเปลี่ยนแปลง  ของเดิม ไม่ต้องเปลี่ยนแปลง
conn.commit()
# 4. ปิดการเชื่อมต่อ
conn.close()
