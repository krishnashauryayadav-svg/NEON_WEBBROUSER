import sys
import os
import threading
import time
import json
from datetime import datetime
import cv2
import pyautogui
import numpy as np

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWebEngineWidgets import *

class CyberBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber Net Premium Browser")
        self.setGeometry(100, 100, 1300, 850)
        
        # Core Configurations
        self.history_enabled = True
        self.history_data = []
        self.bookmarks_file = "bookmarks.json"
        self.bookmarks_data = self.load_bookmarks()
        self.is_recording = False
        self.recording_thread = None

        # 🪐 HOME.HTML KO PYTHON KE ANDAR HI GHUSA DIYA 🪐
        self.custom_home_html = """
        <!DOCTYPE html>
        <html>
        <head>
          <link rel="stylesheet" href="https://cloudflare.com">
          <style>
            body { margin: 0; padding: 0; background: #060913; overflow: hidden; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }
            canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }
            .panel { position: relative; z-index: 2; background: rgba(13, 21, 39, 0.85); border: 1px solid #00f0ff; padding: 40px; border-radius: 12px; text-align: center; box-shadow: 0 0 30px rgba(0, 240, 255, 0.2); backdrop-filter: blur(5px); width: 450px; }
            h1 { color: #00f0ff; margin: 0 0 5px 0; font-size: 2.5rem; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }
            p { color: #8fa0bc; font-size: 0.9rem; margin-bottom: 25px; }
            .search-box { display: flex; align-items: center; background: #060913; border: 1px solid #16223f; border-radius: 30px; padding: 10px 20px; }
            .search-box:focus-within { border-color: #00f0ff; box-shadow: 0 0 12px rgba(0, 240, 255, 0.3); }
            .search-box i { color: #00f0ff; margin-right: 12px; font-size: 1.1rem; }
            .search-box input { background: none; border: none; color: #fff; width: 100%; outline: none; font-size: 1rem; }
          </style>
        </head>
        <body>
          <canvas id="cyberCanvas"></canvas>
          <div class="panel">
            <h1>CYBER NET</h1>
            <p>Secure Node Protocol Active</p>
            <div class="search-box">
              <i class="fas fa-search"></i>
              <input type="text" id="center-search" placeholder="Search or type URL...">
            </div>
          </div>
          <script>
            const canvas = document.getElementById('cyberCanvas'); const ctx = canvas.getContext('2d');
            function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
            window.onresize = resize; resize();
            const characters = "010101001101XYZ####"; const fontSize = 14; const columns = canvas.width / fontSize; const drops = Array(Math.floor(columns)).fill(1);
            function draw() {
              ctx.fillStyle = 'rgba(6, 9, 19, 0.08)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
              ctx.fillStyle = '#00f0ff'; ctx.font = fontSize + 'px monospace';
              for (let i = 0; i < drops.length; i++) {
                const text = characters.charAt(Math.floor(Math.random() * characters.length)); ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0; drops[i]++;
              }
            }
            setInterval(draw, 33);
            document.getElementById('center-search').addEventListener('keydown', (e) => {
              if (e.key === 'Enter') {
                let val = e.target.value.trim(); if(!val) return;
                if (!val.startsWith('http://') && !val.startsWith('https://')) {
                  val = val.includes('.') ? 'https://' + val : 'https://google.com/search?q=' + encodeURIComponent(val);
                }
                window.location.href = val;
              }
            });
          </script>
        </body>
        </html>
        """

        # 🎨 Cyber Neon UI Stylesheet 🎨
        self.setStyleSheet("""
            QMainWindow { background-color: #04060a; }
            QTabWidget::pane { border: none; }
            QTabBar { background: #020306; qproperty-drawBase: 0; }
            QTabBar::tab {
                background: #0d121f; color: #788fa1; padding: 12px 20px; 
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                min-width: 120px; max-width: 180px; 
                border: 1px solid #1a233a; border-bottom: none; margin-right: 4px;
                font-family: 'Segoe UI'; font-size: 11px; font-weight: bold;
            }
            QTabBar::tab:selected { background: #090d16; color: #00f0ff; border: 1px solid #00f0ff; border-bottom: 2px solid #090d16; }
            QToolBar { background-color: #090d16; border-bottom: 2px solid #00f0ff; padding: 10px; spacing: 12px; }
            QLineEdit { background-color: #030509; color: #00f0ff; border: 1px solid #1a233a; border-radius: 18px; padding: 8px 18px; font-size: 13px; font-family: 'Consolas', monospace; }
            QLineEdit:focus { border: 1px solid #00f0ff; background-color: #05080f; }
            QPushButton { background: #0d121f; border: 1px solid #1a233a; color: #00f0ff; font-size: 13px; border-radius: 8px; padding: 6px 14px; font-weight: bold; }
            QPushButton:hover { color: #04060a; background: #00f0ff; border-color: #ffffff; }
        """)

        # Tabs Layout
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)

        # Toolbar
        self.nav_bar = QToolBar()
        self.addToolBar(self.nav_bar)

        # Logo Label
        self.logo_label = QLabel(" 🌐 CYBER_NET v4.0 ")
        self.logo_label.setStyleSheet("color: #04060a; background-color: #00f0ff; font-weight: bold; font-family: 'Segoe UI'; font-size: 12px; padding: 5px 10px; border-radius: 6px; margin-right: 5px;")
        self.nav_bar.addWidget(self.logo_label)

        # Control Buttons
        self.back_btn = QPushButton("◀")
        self.back_btn.clicked.connect(self.navigate_back)
        self.nav_bar.addWidget(self.back_btn)

        self.forward_btn = QPushButton("▶")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.nav_bar.addWidget(self.forward_btn)

        self.reload_btn = QPushButton("⟳")
        self.reload_btn.clicked.connect(self.reload_page)
        self.nav_bar.addWidget(self.reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter address or type query...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.addWidget(self.url_bar)

        self.bmark_btn = QPushButton("⭐")
        self.bmark_btn.clicked.connect(self.add_current_to_bookmarks)
        self.nav_bar.addWidget(self.bmark_btn)

        self.add_tab_btn = QPushButton("＋ Naya Tab")
        self.add_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.nav_bar.addWidget(self.add_tab_btn)

        self.menu_btn = QPushButton("⋮ MENU")
        self.menu_btn.clicked.connect(self.show_three_dots_menu)
        self.nav_bar.addWidget(self.menu_btn)

        # Launch First Tab
        self.add_new_tab()

    # --- Bookmarks Core ---
    def load_bookmarks(self):
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, "r") as f: return json.load(f)
            except: return []
        return []

    def save_bookmarks(self):
        with open(self.bookmarks_file, "w") as f: json.dump(self.bookmarks_data, f, indent=4)

    def add_current_to_bookmarks(self):
        browser = self.tabs.currentWidget()
        if browser:
            url = browser.url().toString()
            title = self.tabs.tabText(self.tabs.currentIndex()).replace("...", "")
            if "data:text/html" in url: return
            if any(b['url'] == url for b in self.bookmarks_data): return
            self.bookmarks_data.append({"title": title, "url": url})
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmarks", "Node linked successfully!")

    # --- Tab Handling Engine ---
    def add_new_tab(self):
        browser = QWebEngineView()
        # Direct string html data load karega bina external file ke
        browser.setHtml(self.custom_home_html)
        i = self.tabs.addTab(browser, "Cyber Net")
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.update_tab_title(i, browser))

    def update_tab_title(self, index, browser):
        title = browser.page().title()
        if "data:text/html" in browser.url().toString() or not title:
            self.tabs.setTabText(index, "Cyber Net")
        else:
            self.tabs.setTabText(index, title[:12] + "...")

    def close_current_tab(self, i):
        if self.tabs.count() < 2: return
        self.tabs.removeTab(i)

    def tab_changed(self, i):
        browser = self.tabs.widget(i)
        if browser:
            url_str = browser.url().toString()
            self.url_bar.setText("" if "data:text/html" in url_str else url_str)

    def update_url(self, qurl, browser=None):
        if browser != self.tabs.currentWidget(): return
        url_str = qurl.toString()
        self.url_bar.setText("" if "data:text/html" in url_str else url_str)
        if self.history_enabled and "data:text/html" not in url_str and "://google.com" not in url_str:
            self.history_data.append({"url": url_str, "time": datetime.now().strftime("%I:%M:%S %p")})

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text: return
        if text.startswith("data:text/html"): text = ""
        if text.startswith("http://") or text.startswith("https://"):
            qurl = QUrl(text)
        else:
            qurl = QUrl(f"https://google.com/search?q={text}")
        self.tabs.currentWidget().setUrl(qurl)

    def navigate_back(self): self.tabs.currentWidget().back()
    def navigate_forward(self): self.tabs.currentWidget().forward()
    def reload_page(self): self.tabs.currentWidget().reload()

    # --- Menu Features ---
    def show_three_dots_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #090d16; color: #00f0ff; border: 1px solid #00f0ff; padding: 6px; font-family: 'Segoe UI'; font-weight: bold; } QMenu::item { padding: 10px 30px; } QMenu::item:selected { background-color: #00f0ff; color: #090d16; }")
        view_history_act = menu.addAction("📜 View Saved History")
        view_bookmarks_act = menu.addAction("🔖 Access Saved Bookmarks")
        screenshot_act = menu.addAction("📸 Take Screenshot")
        rec_text = "🛑 Stop Recording" if self.is_recording else "🎥 Start Screen Recorder"
        recorder_act = menu.addAction(rec_text)
        action = menu.exec(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height())))
        
        if action == view_history_act: self.open_history_dialog()
        elif action == view_bookmarks_act: self.open_bookmarks_dialog()
        elif action == screenshot_act: self.take_browser_screenshot()
        elif action == recorder_act: self.toggle_screen_recorder()

    def open_bookmarks_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cyber Bookmarks Node Manager")
        dialog.setGeometry(150, 150, 550, 400)
        dialog.setStyleSheet("QDialog { background-color: #090d16; color: white; }")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setStyleSheet("QListWidget { background-color: #030509; border: 1px solid #1a233a; color: #00f0ff; padding: 8px; }")
        if not self.bookmarks_data: list_widget.addItem("Bookmarks vault empty.")
        else:
            for b in self.bookmarks_data: list_widget.addItem(f"{b['title']} -> ({b['url']})")
        def on_bookmark_clicked(item):
            text_str = item.text()
            if "->" in text_str:
                self.tabs.currentWidget().setUrl(QUrl(text_str.split("->")[-1].strip().strip("()")))
                dialog.accept()
        list_widget.itemDoubleClicked.connect(on_bookmark_clicked)
        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.exec()

    def open_history_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cyber History Database")
        dialog.setGeometry(150, 150, 500, 400)
        dialog.setStyleSheet("QDialog { background-color: #090d16; color: white; }")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setStyleSheet("QListWidget { background-color: #030509; border: 1px solid #1a233a; color: #c9d1d9; padding: 10px; }")
        if not self.history_data: list_widget.addItem("No logs recorded.")
        else:
            for item in reversed(self.history_data): list_widget.addItem(f"[{item['time']}] -> {item['url']}")
        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.exec()

    def take_browser_screenshot(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.winId())
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        s_dir = os.path.join(desktop, "Cyber_Screenshots")
        if not os.path.exists(s_dir): os.makedirs(s_dir)
        screenshot.save(os.path.join(s_dir, f"Snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"), "png")
        QMessageBox.information(self, "Snapshot", "Screenshot compiled on Desktop inside 'Cyber_Screenshots'!")

    def toggle_screen_recorder(self):
        if not self.is_recording:
            self.is_recording = True
            QMessageBox.information(self, "Recorder", "Recording STARTED!")
            self.recording_thread = threading.Thread(target=self.record_screen_worker)
            self.recording_thread.start()
        else:
            self.is_recording = False
            QMessageBox.information(self, "Recorder", "Recording STOPPED!")

    def record_screen_worker(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        video_path = os.path.join(desktop, f"Cyber_Record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*"XVID"), 10.0, pyautogui.size())
        while self.is_recording:
            frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
            out.write(frame)
            time.sleep(0.1)
        out.release()

app = QApplication(sys.argv)
window = CyberBrowser()
window.show()
sys.exit(app.exec())
