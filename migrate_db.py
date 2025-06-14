import sqlite3

conn = sqlite3.connect("db.sqlite3")
c = conn.cursor()
try:
    c.execute("ALTER TABLE accounts ADD COLUMN proxy TEXT")
    print("✅ Колонка 'proxy' добавлена.")
except sqlite3.OperationalError:
    print("⚠️ Колонка уже существует или ошибка.")
conn.commit()
conn.close()
