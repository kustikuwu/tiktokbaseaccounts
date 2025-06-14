
import os
import sqlite3

SESSIONS_DIR = "sessions"
DB_PATH = "db.sqlite3"

def load_sessions():
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    if not files:
        print("❌ В папке 'sessions/' нет session-файлов.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for file in files:
        session_path = os.path.join(SESSIONS_DIR, file)
        print(f"\nНайден файл сессии: {file}")
        name = input("Введите имя аккаунта (или нажмите Enter, чтобы пропустить): ").strip()
        if not name:
            print("Пропущено.")
            continue

        c.execute("INSERT INTO accounts (name, session_path) VALUES (?, ?)", (name, session_path))
        print(f"✅ Аккаунт '{name}' добавлен.")

    conn.commit()
    conn.close()
    print("\n✅ Загрузка завершена.")

if __name__ == "__main__":
    load_sessions()
