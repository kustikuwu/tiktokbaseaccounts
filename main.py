
import sys, os, sqlite3, json, threading, time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit,
    QComboBox, QFileDialog, QTextEdit, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QTimer
from bot import run_bot

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Manager")
        self.setMinimumSize(1000, 700)
        self.db_path = "db.sqlite3"
        self.interval = 10
        self.max_threads = 3

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_accounts_tab(), "Аккаунты")
        self.tabs.addTab(self.create_commands_tab(), "Команды")
        self.tabs.addTab(self.create_stats_tab(), "Статистика")
        self.tabs.addTab(self.create_settings_tab(), "⚙️ Настройки")
        self.tabs.addTab(self.create_logs_tab(), "📄 Логи")

        self.setCentralWidget(self.tabs)
        self.refresh_timers()

    def create_accounts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.accounts_table = QTableWidget()
        layout.addWidget(QLabel("Список аккаунтов:"))
        layout.addWidget(self.accounts_table)

        add_btn = QPushButton("➕ Добавить аккаунт")
        add_btn.clicked.connect(self.add_account_dialog)
        layout.addWidget(add_btn)

        self.load_accounts()
        tab.setLayout(layout)
        return tab

    def create_commands_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.commands_table = QTableWidget()
        layout.addWidget(QLabel("Список команд:"))
        layout.addWidget(self.commands_table)

        form_layout = QHBoxLayout()
        self.account_input = QLineEdit()
        self.url_input = QLineEdit()
        self.command_box = QComboBox()
        self.command_box.addItems(["like", "follow", "view"])
        add_button = QPushButton("Добавить команду")
        add_button.clicked.connect(self.add_command)
        run_button = QPushButton("🚀 Запустить бота")
        run_button.clicked.connect(self.run_bot_threaded)

        form_layout.addWidget(QLabel("ID аккаунта:"))
        form_layout.addWidget(self.account_input)
        form_layout.addWidget(QLabel("URL:"))
        form_layout.addWidget(self.url_input)
        form_layout.addWidget(QLabel("Команда:"))
        form_layout.addWidget(self.command_box)
        form_layout.addWidget(add_button)
        form_layout.addWidget(run_button)

        layout.addLayout(form_layout)
        layout.addWidget(self.commands_table)
        self.load_commands()
        tab.setLayout(layout)
        return tab

    def create_stats_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.stats_label = QLabel("Загрузка статистики...")
        layout.addWidget(self.stats_label)
        tab.setLayout(layout)
        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.interval_box = QSpinBox()
        self.interval_box.setValue(self.interval)
        self.interval_box.setSuffix(" сек.")
        self.interval_box.setMinimum(1)

        self.thread_box = QSpinBox()
        self.thread_box.setValue(self.max_threads)
        self.thread_box.setMinimum(1)
        self.thread_box.setMaximum(10)

        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.clicked.connect(self.save_settings)

        layout.addWidget(QLabel("Интервал автообновления:"))
        layout.addWidget(self.interval_box)
        layout.addWidget(QLabel("Максимум потоков:"))
        layout.addWidget(self.thread_box)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        return tab

    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Вывод логов:"))
        layout.addWidget(self.log_output)
        tab.setLayout(layout)
        return tab

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")

    def load_accounts(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("SELECT id, name, session_path, proxy FROM accounts")
            rows = c.fetchall()
            self.accounts_table.setRowCount(len(rows))
            self.accounts_table.setColumnCount(4)
            self.accounts_table.setHorizontalHeaderLabels(["ID", "Имя", "Сессия", "Прокси"])
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.accounts_table.setItem(i, j, QTableWidgetItem(str(val)))
        except Exception as e:
            self.log(f"Ошибка загрузки аккаунтов: {e}")
        finally:
            conn.close()

    def load_commands(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, account_id, command, target_url, status FROM commands ORDER BY id DESC LIMIT 20")
        rows = c.fetchall()
        conn.close()

        self.commands_table.setRowCount(len(rows))
        self.commands_table.setColumnCount(5)
        self.commands_table.setHorizontalHeaderLabels(["ID", "ID аккаунта", "Команда", "URL", "Статус"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.commands_table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_command(self):
        acc_id = self.account_input.text().strip()
        url = self.url_input.text().strip()
        command = self.command_box.currentText()
        if acc_id and url:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO commands (account_id, command, target_url) VALUES (?, ?, ?)", (acc_id, command, url))
            conn.commit()
            conn.close()
            self.load_commands()
            self.account_input.clear()
            self.url_input.clear()
            self.log(f"Добавлена команда {command} для аккаунта {acc_id}")

    def update_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT status, COUNT(*) FROM commands GROUP BY status")
        data = dict(c.fetchall())
        conn.close()
        self.stats_label.setText(f"✅ Выполнено: {data.get('done',0)} | ⏳ В ожидании: {data.get('pending',0)} | ❌ Ошибок: {data.get('failed',0)}")

    def refresh_timers(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_accounts)
        self.timer.timeout.connect(self.load_commands)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(self.interval * 1000)

    def run_bot_threaded(self):
        def runner():
            self.log("▶️ Запуск бота...")
            run_bot()
            self.log("✅ Бот завершил выполнение.")
        threading.Thread(target=runner, daemon=True).start()

    def add_account_dialog(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выбери .json файл сессии", "", "JSON Files (*.json)")
        if file:
            name, ok = QLineEdit.getText(self, "Имя аккаунта", "Введите имя аккаунта:")
            if not ok or not name:
                return
            proxy, ok2 = QLineEdit.getText(self, "Прокси (необязательно)", "http://user:pass@ip:port")
            proxy = proxy if ok2 else ""
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO accounts (name, session_path, proxy) VALUES (?, ?, ?)", (name, file, proxy))
            conn.commit()
            conn.close()
            self.load_accounts()
            self.log(f"Добавлен аккаунт {name}")

    def save_settings(self):
        self.interval = self.interval_box.value()
        self.max_threads = self.thread_box.value()
        self.timer.setInterval(self.interval * 1000)
        self.log(f"Настройки обновлены: интервал {self.interval}с, потоки {self.max_threads}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
