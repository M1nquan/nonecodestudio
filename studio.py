import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from PyQt6.QtCore import (
    Qt, QProcess, QProcessEnvironment, QDir, QUrl, QSettings,
    QPropertyAnimation, QEasingCurve, QSize, QPoint, QThread, pyqtSignal
)
from PyQt6.QtGui import (
    QAction, QDesktopServices, QIcon, QKeySequence, QShortcut,
    QTextCharFormat, QTextCursor, QFileSystemModel
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QTreeView, QTextEdit, QFileDialog, QMessageBox, QLabel, QToolBar,
    QToolButton, QFrame, QMenu, QLineEdit, QComboBox, QInputDialog,
    QAbstractItemView, QSizePolicy, QProgressDialog, QApplication
)

import theme
from theme import ORG, APP_NAME, BROWSE, CREDIT, VERSION, T
from workers import venv_python, venv_root_of, find_venvs
from editor import CodeEditor
from widgets import Overlay, Toast
from dialogs import CloneDialog, VenvDialog


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url, target_path):
        super().__init__()
        self.url = url
        self.target_path = target_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "NoneCodeStudio-AutoUpdater"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = resp.info().get("Content-Length")
                total_size = int(total_size) if total_size else 0
                downloaded = 0
                block_size = 1024 * 64

                with open(self.target_path, "wb") as f:
                    while True:
                        if self._is_cancelled:
                            return
                        chunk = resp.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.progress.emit(percent)
            self.finished.emit(self.target_path)
        except Exception as e:
            self.failed.emit(str(e))


class NoneCodeStudio(QMainWindow):
    TERM_OPEN_H = 240
    TERM_CLOSED_H = 32

    # CẤU HÌNH GITHUB REPOSITORY ĐỂ CHECK CẬP NHẬT
    GITHUB_OWNER = "M1nquan"
    GITHUB_REPO = "nonecodestudio"

    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORG, APP_NAME)
        ws = self.settings.value("workspace", QDir.homePath())
        self.workspace = ws if isinstance(ws, str) and os.path.isdir(ws) else QDir.homePath()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        saved_theme = self.settings.value("theme", "Deep Obsidian")
        if saved_theme in theme.THEMES:
            theme.set_theme(saved_theme)

        self.setWindowTitle(f"{APP_NAME} — {VERSION}")
        self.setWindowIcon(QIcon(theme.make_logo(48)))
        self.resize(1380, 840)
        geo = self.settings.value("geometry")
        if geo:
            self.restoreGeometry(geo)

        self._term_anim = None
        self._find_anim = None
        self._term_open = True
        self._on_done = None
        self._last_find = ""

        self.setStyleSheet(theme.build_style())
        self.create_layout()
        self.overlay = Overlay(self)
        self.create_toolbar_and_menu()

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)
        self.process.errorOccurred.connect(self.on_process_error)

        self.set_workspace(self.workspace)
        self.new_file()

    def create_layout(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = QWidget()
        self.title_bar.setObjectName("customTitleBar")
        self.title_bar.setFixedHeight(32)
        tb_layout = QHBoxLayout(self.title_bar)
        tb_layout.setContentsMargins(10, 0, 0, 0)
        tb_layout.setSpacing(8)

        self.title_icon = QLabel()
        self.title_icon.setPixmap(theme.make_logo(16))
        
        self.title_lbl = QLabel(f"{APP_NAME} — {VERSION}")
        self.title_lbl.setStyleSheet(f"color: {T['MUTED']}; font-size: 8.5pt; font-weight: 600;")

        tb_layout.addWidget(self.title_icon)
        tb_layout.addWidget(self.title_lbl)
        tb_layout.addStretch()

        btn_min = QToolButton()
        btn_min.setObjectName("windowBtn")
        btn_min.setText("—")
        btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_min.clicked.connect(self.showMinimized)

        self.btn_max = QToolButton()
        self.btn_max.setObjectName("windowBtn")
        btn_max_text = "❐" if self.isMaximized() else "□"
        self.btn_max.setText(btn_max_text)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self.toggle_maximize)

        btn_close = QToolButton()
        btn_close.setObjectName("windowCloseBtn")
        btn_close.setText("✕")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.close)

        tb_layout.addWidget(btn_min)
        tb_layout.addWidget(self.btn_max)
        tb_layout.addWidget(btn_close)
        root.addWidget(self.title_bar)

        self._drag_pos = None
        self.title_bar.mousePressEvent = self.title_mouse_press
        self.title_bar.mouseMoveEvent = self.title_mouse_move
        self.title_bar.mouseDoubleClickEvent = lambda e: self.toggle_maximize()

        # 2. Main Body Splitter
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.split = QSplitter(Qt.Orientation.Horizontal)
        self.split.setChildrenCollapsible(False)
        self.split.setHandleWidth(1)
        body_layout.addWidget(self.split)
        root.addWidget(body_widget, 1)

        # Explorer Panel
        side = QFrame()
        side.setObjectName("sidebar")
        side.setMinimumWidth(210)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)

        lbl_sec = QLabel("EXPLORER")
        lbl_sec.setObjectName("sidebarTitle")
        sl.addWidget(lbl_sec)

        self.lbl_ws = QLabel()
        self.lbl_ws.setObjectName("wsName")
        sl.addWidget(self.lbl_ws)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(12)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for col in (1, 2, 3):
            self.tree_view.hideColumn(col)
        self.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.tree_menu)
        sl.addWidget(self.tree_view, 1)

        self.split.addWidget(side)

        # Editor Workspace
        main = QWidget()
        ml = QVBoxLayout(main)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setDocumentMode(False)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        btn_plus = QToolButton()
        btn_plus.setObjectName("tabPlusBtn")
        btn_plus.setIcon(theme.vicon("plus", T["MUTED"], 12))
        btn_plus.setToolTip("File mới (Ctrl+N)")
        btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_plus.clicked.connect(self.new_file)
        self.tab_widget.setCornerWidget(btn_plus, Qt.Corner.TopRightCorner)
        ml.addWidget(self.tab_widget, 1)

        # Find Bar
        self.find_bar = QFrame()
        self.find_bar.setObjectName("findBar")
        self.find_bar.setMaximumHeight(0)
        fb = QHBoxLayout(self.find_bar)
        fb.setContentsMargins(8, 4, 8, 4)
        fb.setSpacing(6)
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Tìm trong file… (Enter để tìm tiếp)")
        self.find_edit.returnPressed.connect(lambda: self.find(True))
        self.find_edit.textEdited.connect(lambda _t: setattr(self, "_last_find", ""))
        btn_prev = QToolButton()
        btn_prev.setIcon(theme.vicon("chev_up", T["MUTED"], 12))
        btn_prev.clicked.connect(lambda: self.find(False))
        btn_next = QToolButton()
        btn_next.setIcon(theme.vicon("chev_down", T["MUTED"], 12))
        btn_next.clicked.connect(lambda: self.find(True))
        btn_x = QToolButton()
        btn_x.setIcon(theme.vicon("close", T["MUTED"], 12))
        btn_x.clicked.connect(self.hide_find)
        fb.addWidget(self.find_edit, 1)
        fb.addWidget(btn_prev)
        fb.addWidget(btn_next)
        fb.addWidget(btn_x)
        self.find_bar.hide()
        esc = QShortcut(QKeySequence("Escape"), self.find_bar)
        esc.activated.connect(self.hide_find)
        ml.addWidget(self.find_bar)

        # Terminal Panel
        self.term_panel = QFrame()
        self.term_panel.setObjectName("termPanel")
        self.term_panel.setMinimumHeight(0)
        self.term_panel.setMaximumHeight(self.TERM_OPEN_H)
        tl = QVBoxLayout(self.term_panel)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)

        th = QWidget()
        th.setObjectName("cardHeader")
        th.setFixedHeight(self.TERM_CLOSED_H)
        thl = QHBoxLayout(th)
        thl.setContentsMargins(14, 0, 8, 0)
        thl.setSpacing(8)
        lbl_term = QLabel("TERMINAL")
        lbl_term.setObjectName("termTitle")
        thl.addWidget(lbl_term)

        self.lbl_term_info = QLabel()
        self.lbl_term_info.setStyleSheet(f"color: {T['MUTED']}; font-size: 8pt;")
        thl.addWidget(self.lbl_term_info)
        thl.addStretch()

        btn_clear = QToolButton()
        btn_clear.setText("Clear")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_terminal)
        self.btn_toggle = QToolButton()
        self.btn_toggle.setIcon(theme.vicon("chev_down", T["MUTED"], 12))
        self.btn_toggle.setToolTip("Thu gọn / Mở Terminal (Ctrl+`)")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_terminal)
        thl.addWidget(btn_clear)
        thl.addWidget(self.btn_toggle)

        self.term_body = QWidget()
        tb = QVBoxLayout(self.term_body)
        tb.setContentsMargins(0, 0, 0, 0)
        tb.setSpacing(0)
        self.terminal_output = QTextEdit()
        self.terminal_output.setObjectName("termOut")
        self.terminal_output.setReadOnly(True)
        self.stdin_edit = QLineEdit()
        self.stdin_edit.setObjectName("termIn")
        self.stdin_edit.setPlaceholderText("stdin › Nhập dữ liệu rồi nhấn Enter...")
        self.stdin_edit.returnPressed.connect(self.send_stdin)
        tb.addWidget(self.terminal_output, 1)
        tb.addWidget(self.stdin_edit)

        tl.addWidget(th)
        tl.addWidget(self.term_body, 1)
        ml.addWidget(self.term_panel)

        self.split.addWidget(main)
        self.split.setSizes([220, 1160])

        # Status Bar
        sb = self.statusBar()
        sb.setSizeGripEnabled(False)
        self.lbl_status = QLabel("Ready")
        self.lbl_run = QLabel("")
        self.lbl_interp = QLabel()
        self.lbl_interp.setObjectName("statusPill")
        self.lbl_lang = QLabel("Plain Text")
        self.lbl_pos = QLabel("Ln 1, Col 1")
        self.lbl_enc = QLabel("UTF-8")
        sb.addWidget(self.lbl_status, 1)
        sb.addWidget(self.lbl_run)
        sb.addPermanentWidget(self.lbl_interp)
        sb.addPermanentWidget(self.lbl_lang)
        sb.addPermanentWidget(self.lbl_pos)
        sb.addPermanentWidget(self.lbl_enc)

    def title_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def title_mouse_move(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            if self.isMaximized():
                self.showNormal()
                self.btn_max.setText("□")
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_max.setText("□")
        else:
            self.showMaximized()
            self.btn_max.setText("❐")

    def switch_theme(self, name):
        if name in theme.THEMES:
            theme.set_theme(name)
            self.settings.setValue("theme", name)
            self.setStyleSheet(theme.build_style())
            self.title_icon.setPixmap(theme.make_logo(16))
            self.title_lbl.setStyleSheet(f"color: {theme.T['MUTED']}; font-size: 8.5pt; font-weight: 600;")
            for i in range(self.tab_widget.count()):
                w = self.tab_widget.widget(i)
                if isinstance(w, CodeEditor):
                    w._setup_ui()
                    w.apply_lexer()
            self.toast(f"Theme: {name}", theme.T["OK"])

    def _act(self, text, shortcut, slot, icon_kind=None, icon_color=None):
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        if icon_kind:
            a.setIcon(theme.vicon(icon_kind, icon_color or T["MUTED"], 13))
        a.triggered.connect(slot)
        self.addAction(a)
        return a

    def _tool_btn(self, action, primary=False, danger=False):
        b = QToolButton()
        b.setDefaultAction(action)
        b.setIconSize(QSize(13, 13))
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        if primary:
            b.setObjectName("primary")
        elif danger:
            b.setObjectName("danger")
        return b

    def check_github_update(self):
        """Kiểm tra bản cập nhật: Ưu tiên GitHub API, tự động Fallback qua Web Redirect nếu bị 403."""
        import json
        import urllib.error
        import urllib.request
        from theme import VERSION

        api_url = f"https://api.github.com/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/releases/latest"
        latest_tag = ""
        changelog = "Bản phát hành mới nhất từ GitHub."
        download_url = None
        is_exe = True

        # 1. Thử dùng GitHub REST API trước để lấy Changelog và Assets
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latest_tag = data.get("tag_name", "").strip()
                changelog = data.get("body", changelog)
                
                # Tìm file .exe trong danh sách assets
                for asset in data.get("assets", []):
                    name = asset.get("name", "").lower()
                    if name.endswith(".exe"):
                        download_url = asset.get("browser_download_url")
                        break
        except urllib.error.HTTPError as e:
            # 2. Nếu bị chặn 403 hoặc lỗi API, kích hoạt Fallback qua URL Redirect
            if e.code in (403, 429):
                try:
                    web_url = f"https://github.com/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/releases/latest"
                    web_req = urllib.request.Request(
                        web_url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
                    )
                    with urllib.request.urlopen(web_req, timeout=6) as web_resp:
                        final_url = web_resp.geturl()
                    
                    if not (final_url.endswith("/releases") or final_url.endswith("/releases/")):
                        latest_tag = final_url.rstrip("/").split("/")[-1]
                except Exception:
                    self.toast("Không thể lấy dữ liệu cập nhật", theme.T["ERR"])
                    return
            elif e.code == 404:
                self.toast("Chưa có bản Release nào trên GitHub", theme.T["WARN"])
                return
            else:
                self.toast(f"Lỗi kiểm tra cập nhật ({e.code})", theme.T["ERR"])
                return
        except Exception:
            self.toast("Không thể kết nối tới GitHub", theme.T["ERR"])
            return

        if not latest_tag:
            self.toast("Không tìm thấy thông tin bản cập nhật", theme.T["WARN"])
            return

        # Tự động gán link download file exe nếu chưa lấy được từ Assets API
        if not download_url:
            download_url = f"https://github.com/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/releases/download/{latest_tag}/nonecodestudio.exe"

        # Hiển thị thông báo xác nhận cập nhật cho người dùng
        res = self.blurred(
            QMessageBox.question,
            self,
            "Có bản cập nhật mới",
            f"Bản phát hành: {latest_tag}\n(Phiên bản hiện tại: {VERSION})\n\n"
            f"Mô tả:\n{changelog}\n\n"
            f"Bạn có muốn tự động tải 'nonecodestudio.exe' và cập nhật ngay không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if res == QMessageBox.StandardButton.Yes:
            self.start_auto_update(download_url, is_exe=True)
    def start_auto_update(self, download_url, is_exe):
        """Tải bản mới về thư mục tạm và tự động ghi đè file hiện tại."""
        temp_dir = tempfile.gettempdir()
        file_ext = ".exe" if is_exe else ".zip"
        temp_file = os.path.join(temp_dir, f"update_{os.getpid()}{file_ext}")

        # Hộp thoại hiển thị tiến trình tải
        progress_dlg = QProgressDialog("Đang tải bản cập nhật mới...", "Hủy", 0, 100, self)
        progress_dlg.setWindowTitle("Cập nhật ứng dụng")
        progress_dlg.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dlg.setAutoClose(True)
        progress_dlg.show()

        worker = DownloadWorker(download_url, temp_file)

        def on_progress(percent):
            progress_dlg.setValue(percent)

        def on_finished(downloaded_path):
            progress_dlg.close()
            self.apply_update_and_restart(downloaded_path, is_exe)

        def on_failed(err_msg):
            progress_dlg.close()
            self.toast(f"Tải thất bại: {err_msg}", theme.T["ERR"])

        progress_dlg.canceled.connect(worker.cancel)
        worker.progress.connect(on_progress)
        worker.finished.connect(on_finished)
        worker.failed.connect(on_failed)
        worker.start()
        self._updater_thread = worker

    def apply_update_and_restart(self, downloaded_file, is_exe):
        """Khởi tạo script batch để đợi app tắt rồi thay thế file và khởi động lại."""
        current_exe = os.path.abspath(sys.argv[0])
        # Nếu đang chạy bằng file python thuần (chưa đóng gói exe)
        if not current_exe.lower().endswith(".exe"):
            current_exe = os.path.abspath(sys.executable)

        target_dir = os.path.dirname(current_exe)
        current_pid = os.getpid()

        # Tạo file batch tạm thời để thay thế file sau khi app đóng
        bat_file = os.path.join(tempfile.gettempdir(), f"update_runner_{current_pid}.bat")

        if is_exe:
            # Ghi đè file exe
            bat_content = f"""@echo off
chcp 65001 >nul
echo Dang cap nhat... Cho ung dung dong hoan toan.
:wait_loop
tasklist /fi "PID eq {current_pid}" | find ":" >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
move /y "{downloaded_file}" "{current_exe}" >nul
start "" "{current_exe}"
del "%~f0"
exit
"""
        else:
            # Giải nén đè nếu là file .zip
            bat_content = f"""@echo off
chcp 65001 >nul
echo Dang giai nen ban cap nhat...
:wait_loop
tasklist /fi "PID eq {current_pid}" | find ":" >nul
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)
powershell -Command "Expand-Archive -Path '{downloaded_file}' -DestinationPath '{target_dir}' -Force"
del "{downloaded_file}" >nul
start "" "{current_exe}"
del "%~f0"
exit
"""

        with open(bat_file, "w", encoding="utf-8") as f:
            f.write(bat_content)

        # Chạy script ngầm
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(["cmd.exe", "/c", bat_file], shell=True, creationflags=creationflags)

        # Thoát ứng dụng hiện tại để tiến trình batch thực hiện nhiệm vụ
        QApplication.quit()

    def create_toolbar_and_menu(self):
        self.act_new = self._act("New", "Ctrl+N", self.new_file, "plus")
        self.act_open = self._act("Open…", "Ctrl+O", self.open_file_dialog, "folder")
        self.act_open_folder = self._act("Folder…", "Ctrl+Shift+O", self.open_folder_dialog, "folder")
        self.act_clone = self._act("Clone…", "Ctrl+Shift+G", self.clone_github, "git")
        self.act_save = self._act("Save", "Ctrl+S", self.save_file, "save")
        self.act_close = self._act("Close Tab", "Ctrl+W",
                                   lambda: self.close_tab(self.tab_widget.currentIndex()))
        self.act_find = self._act("Find…", "Ctrl+F", self.show_find, "search")
        self.act_run = self._act("Run", "F5", self.run_current_file, "play", T["PRIMARY_FG"])
        self.act_live_html = self._act("HTML Preview", "Ctrl+B", self.open_html_preview, "globe")
        self.act_stop = self._act("Stop", "Shift+F5", self.stop_process, "stop", T["ERR"])
        self.act_stop.setEnabled(False)
        self.act_term = self._act("Terminal", "Ctrl+`", self.toggle_terminal)
        self.act_venv = self._act("Env Manager…", "Ctrl+Shift+V", self.open_venv_dialog, "box")
        self.act_req = self._act("Install requirements.txt", "", self.install_selected_requirements)
        
        # Nút kiểm tra và tự cập nhật
        self.act_check_update = self._act("Check for Updates…", "", self.check_github_update)
        self.act_about = self._act("About", "", self.show_about)

        mb = self.menuBar()
        m_file = mb.addMenu("File")
        for a in (self.act_new, self.act_open, self.act_open_folder, self.act_clone):
            m_file.addAction(a)
        m_file.addSeparator()
        m_file.addAction(self.act_save)
        m_file.addAction(self.act_close)

        m_edit = mb.addMenu("Edit")
        m_edit.addAction(self.act_find)

        m_run = mb.addMenu("Run")
        m_run.addAction(self.act_run)
        m_run.addAction(self.act_live_html)
        m_run.addAction(self.act_stop)

        m_theme = mb.addMenu("Theme")
        for th_name in theme.THEMES:
            m_theme.addAction(th_name, lambda n=th_name: self.switch_theme(n))

        m_py = mb.addMenu("Runtime")
        m_py.addAction(self.act_venv)
        m_py.addAction(self.act_req)

        m_view = mb.addMenu("View")
        m_view.addAction(self.act_term)

        m_help = mb.addMenu("Help")
        m_help.addAction(self.act_check_update)
        m_help.addAction(self.act_about)

        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addWidget(self._tool_btn(self.act_open_folder))
        tb.addWidget(self._tool_btn(self.act_clone))
        tb.addWidget(self._tool_btn(self.act_save))
        tb.addSeparator()

        self.cmb_py = QComboBox()
        self.cmb_py.setObjectName("runtimePill")
        self.cmb_py.setToolTip("Chọn Python Environment")
        self.cmb_py.activated.connect(self.on_interpreter_activated)
        tb.addWidget(self.cmb_py)
        tb.addWidget(self._tool_btn(self.act_venv))
        tb.addSeparator()

        self.cmb_theme = QComboBox()
        self.cmb_theme.setObjectName("themeSelector")
        self.cmb_theme.setToolTip("Đổi màu giao diện (UI/UX Theme)")
        for th_name in theme.THEMES:
            self.cmb_theme.addItem(th_name)
        self.cmb_theme.setCurrentText(theme.CURRENT_THEME_NAME)
        self.cmb_theme.currentTextChanged.connect(self.switch_theme)
        tb.addWidget(self.cmb_theme)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        tb.addWidget(self._tool_btn(self.act_live_html))
        tb.addWidget(self._tool_btn(self.act_run, primary=True))
        tb.addWidget(self._tool_btn(self.act_stop, danger=True))

    def open_html_preview(self):
        ed = self.current_editor()
        if not ed:
            return
        if not self.save_editor(ed) or not ed.filepath:
            return
        ext = os.path.splitext(ed.filepath)[1].lower()
        if ext in (".html", ".htm"):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(ed.filepath)))
            self.toast("Previewing HTML in Browser", theme.T["OK"])
        else:
            self.toast("Not an HTML file", theme.T["WARN"])

    def start_intro(self):
        pix = self.safe_capture_blurred()
        self.overlay.start_intro(pix)

    def safe_capture_blurred(self):
        was_visible = self.overlay.isVisible()
        if was_visible:
            self.overlay.hide()
        pix = self.grab()
        if was_visible:
            self.overlay.show()
        return theme.gaussian_blur(pix, 12)

    def blurred(self, fn, *args, **kwargs):
        pix = self.safe_capture_blurred()
        self.overlay.show_backdrop(pix)
        try:
            return fn(*args, **kwargs)
        finally:
            self.overlay.fade_out(200)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "overlay"):
            self.overlay.setGeometry(self.rect())

    def toast(self, text, color=None):
        Toast(self, text, color or theme.T["ACCENT"])

    def set_workspace(self, folder):
        self.workspace = folder
        self.tree_view.setRootIndex(self.file_model.index(folder))
        self.lbl_ws.setText(os.path.basename(folder.rstrip("/\\")) or folder)
        self.lbl_ws.setToolTip(folder)
        self.settings.setValue("workspace", folder)
        self.refresh_interpreters()

    def open_folder_dialog(self):
        folder = self.blurred(QFileDialog.getExistingDirectory, self, "Mở thư mục", self.workspace)
        if folder:
            self.set_workspace(folder)
            self.toast("Workspace mounted", theme.T["OK"])

    def open_file_dialog(self):
        path, _ = self.blurred(QFileDialog.getOpenFileName, self, "Open File", self.workspace, "All Files (*.*)")
        if path:
            self.load_file(path)

    def on_file_double_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.load_file(path)

    def tree_menu(self, pos):
        idx = self.tree_view.indexAt(pos)
        path = self.file_model.filePath(idx) if idx.isValid() else self.workspace
        is_dir = os.path.isdir(path)
        menu = QMenu(self)
        if is_dir:
            menu.addAction("New File…", lambda: self.fs_new(path, False))
            menu.addAction("New Folder…", lambda: self.fs_new(path, True))
        else:
            menu.addAction("Open", lambda: self.load_file(path))
            if path.lower().endswith((".html", ".htm")):
                menu.addAction("Preview in Browser", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(path)))
        if idx.isValid():
            menu.addSeparator()
            menu.addAction("Rename…", lambda: self.fs_rename(path))
            menu.addAction("Delete", lambda: self.fs_delete(path))
        menu.addSeparator()
        target = path if is_dir else os.path.dirname(path)
        menu.addAction("Reveal in Explorer",
                       lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(target)))
        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def fs_new(self, folder, is_dir):
        title = "New Folder" if is_dir else "New File"
        name, ok = self.blurred(QInputDialog.getText, self, title, "Name:")
        name = name.strip() if ok else ""
        if not name:
            return
        target = os.path.join(folder, name)
        try:
            if is_dir:
                os.makedirs(target)
            else:
                with open(target, "x", encoding="utf-8"):
                    pass
        except OSError as e:
            self.toast(f"Error: {e}", theme.T["ERR"])
            return
        if not is_dir:
            self.load_file(target)

    def fs_rename(self, path):
        base = os.path.basename(path)
        name, ok = self.blurred(QInputDialog.getText, self, "Rename", "New name:",
                                QLineEdit.EchoMode.Normal, base)
        name = name.strip() if ok else ""
        if not name or name == base:
            return
        new = os.path.join(os.path.dirname(path), name)
        try:
            os.rename(path, new)
        except OSError as e:
            self.toast(f"Error: {e}", theme.T["ERR"])
            return
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if ed.filepath and os.path.abspath(ed.filepath) == os.path.abspath(path):
                ed.set_filepath(new)
                self._refresh_tab_title(ed)

    def fs_delete(self, path):
        res = self.blurred(
            QMessageBox.question, self, "Delete",
            f"Delete permanently:\n{path}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if res != QMessageBox.StandardButton.Yes:
            return
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError as e:
            self.toast(f"Error: {e}", theme.T["ERR"])
            return
        self._close_tabs_under(path)

    def _close_tabs_under(self, path):
        target = os.path.abspath(path)
        for i in range(self.tab_widget.count() - 1, -1, -1):
            ed = self.tab_widget.widget(i)
            if ed.filepath and os.path.abspath(ed.filepath).startswith(target):
                self.tab_widget.removeTab(i)
                ed.deleteLater()
        if self.tab_widget.count() == 0:
            self.new_file()

    def clone_github(self):
        dlg = CloneDialog(self, self.workspace)
        self.blurred(dlg.exec)
        path = dlg.result_path
        dlg.deleteLater()
        if path:
            self.set_workspace(path)
            self.toast("Repository cloned", theme.T["OK"])

    def custom_pythons(self):
        val = self.settings.value("custom_pythons", [])
        if isinstance(val, str):
            val = [val]
        return [p for p in (val or []) if isinstance(p, str)]

    def interpreters(self):
        items = [("Python (System)", sys.executable)]
        for name, py in find_venvs(self.workspace):
            items.append((f"venv: {name}", py))
        known = {p for _, p in items}
        for py in self.custom_pythons():
            if os.path.isfile(py) and py not in known:
                items.append((f"Custom: {os.path.basename(py)}", py))
                known.add(py)
        return items

    def refresh_interpreters(self, select=None):
        current = select or self.cmb_py.currentData() or self.settings.value("interpreter", sys.executable)
        self.cmb_py.blockSignals(True)
        self.cmb_py.clear()
        for label, path in self.interpreters():
            self.cmb_py.addItem(label, path)
        self.cmb_py.addItem("Browse…", BROWSE)
        idx = self.cmb_py.findData(current)
        self.cmb_py.setCurrentIndex(idx if idx >= 0 else 0)
        self.cmb_py.blockSignals(False)
        self.settings.setValue("interpreter", self.cmb_py.currentData())
        self.update_interp_label()

    def on_interpreter_activated(self, index):
        if self.cmb_py.itemData(index) == BROWSE:
            path, _ = self.blurred(QFileDialog.getOpenFileName, self, "Select Python", "",
                                   "Python (python*.exe python*);;All (*.*)")
            if path:
                customs = self.custom_pythons()
                if path not in customs:
                    customs.append(path)
                    self.settings.setValue("custom_pythons", customs)
                self.refresh_interpreters(select=path)
            else:
                self.refresh_interpreters()
            return
        self.settings.setValue("interpreter", self.cmb_py.currentData())
        self.update_interp_label()

    def update_interp_label(self):
        py = self.cmb_py.currentData()
        root = venv_root_of(py)
        if root:
            self.lbl_interp.setText(f"venv: {os.path.basename(root)}")
        else:
            self.lbl_interp.setText("Python: System")
        self.lbl_interp.setToolTip(py or "")
        self.lbl_term_info.setText(py or "")

    def open_venv_dialog(self):
        dlg = VenvDialog(self)
        self.blurred(dlg.exec)
        dlg.deleteLater()

    def prompt_create_venv(self):
        if not self._require_workspace():
            return
        name, ok = self.blurred(QInputDialog.getText, self, "Create venv", "Name:",
                                QLineEdit.EchoMode.Normal, ".venv")
        if ok and name.strip():
            self.create_venv(name.strip())

    def create_venv(self, name):
        if not self._require_workspace():
            return
        venv_dir = os.path.join(self.workspace, name)
        if os.path.exists(venv_dir):
            self.toast("Folder already exists", theme.T["WARN"])
            return
        py_new = venv_python(venv_dir)
        self.start_task(
            sys.executable, ["-m", "venv", venv_dir], self.workspace,
            f"Create venv '{name}'",
            on_done=lambda ok: self.refresh_interpreters(select=py_new) if ok else None,
            python=None,
        )

    def install_selected_requirements(self):
        self.install_requirements(self.cmb_py.currentData())

    def install_requirements(self, python):
        if not self._require_workspace() or not python:
            return
        req = os.path.join(self.workspace, "requirements.txt")
        if not os.path.isfile(req):
            self.toast("No requirements.txt found", theme.T["WARN"])
            return
        self.start_task(python, ["-m", "pip", "install", "-r", req], self.workspace,
                        "pip install -r requirements.txt", python=python)

    def delete_venv(self, python):
        root = venv_root_of(python)
        if not root:
            self.toast("Not a venv directory", theme.T["WARN"])
            return False
        res = self.blurred(
            QMessageBox.question, self, "Delete venv",
            f"Delete venv directory?\n{root}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if res != QMessageBox.StandardButton.Yes:
            return False
        try:
            shutil.rmtree(root)
        except OSError as e:
            self.toast(f"Error: {e}", theme.T["ERR"])
            return False
        self.toast("Venv deleted", theme.T["WARN"])
        return True

    def _require_workspace(self):
        if not os.path.isdir(self.workspace):
            self.toast("Invalid workspace", theme.T["WARN"])
            return False
        return True

    def current_editor(self):
        return self.tab_widget.currentWidget()

    def add_editor(self, editor, title):
        idx = self.tab_widget.addTab(editor, title)
        self.tab_widget.setCurrentIndex(idx)
        editor.cursorPositionChanged.connect(self.update_status)
        editor.modificationChanged.connect(lambda _m, ed=editor: self._refresh_tab_title(ed))
        self._refresh_tab_title(editor)
        self.update_status()

    def _refresh_tab_title(self, editor):
        idx = self.tab_widget.indexOf(editor)
        if idx < 0:
            return
        name = os.path.basename(editor.filepath) if editor.filepath else "Untitled"
        if editor.isModified():
            name = "• " + name
        self.tab_widget.setTabText(idx, name)
        self.tab_widget.setTabToolTip(idx, editor.filepath or "Unsaved")

    def on_tab_changed(self, _index):
        self._last_find = ""
        self.update_status()

    def update_status(self, *_):
        ed = self.current_editor()
        if not ed:
            return
        line, col = ed.getCursorPosition()
        self.lbl_pos.setText(f"Ln {line + 1}, Col {col + 1}")
        self.lbl_lang.setText(ed.language_name())
        self.lbl_status.setText(ed.filepath or "Untitled")

    def new_file(self):
        self.add_editor(CodeEditor(parent=self), "Untitled")

    def load_file(self, filepath):
        target = os.path.abspath(filepath)
        for i in range(self.tab_widget.count()):
            ed = self.tab_widget.widget(i)
            if ed.filepath and os.path.abspath(ed.filepath) == target:
                self.tab_widget.setCurrentIndex(i)
                return
        self.add_editor(CodeEditor(filepath=filepath, parent=self), os.path.basename(filepath))

    def open_file_dialog(self):
        path, _ = self.blurred(QFileDialog.getOpenFileName, self, "Open File", self.workspace, "All Files (*.*)")
        if path:
            self.load_file(path)

    def close_tab(self, index):
        if index < 0:
            return
        ed = self.tab_widget.widget(index)
        if ed.isModified():
            res = self.blurred(
                QMessageBox.question, self, "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if res == QMessageBox.StandardButton.Cancel:
                return
            if res == QMessageBox.StandardButton.Save and not self.save_editor(ed):
                return
        self.tab_widget.removeTab(index)
        ed.deleteLater()
        if self.tab_widget.count() == 0:
            self.new_file()

    def save_file(self):
        return self.save_editor(self.current_editor())

    def save_editor(self, ed):
        if ed is None:
            return False
        if not ed.filepath:
            path, _ = self.blurred(QFileDialog.getSaveFileName, self, "Save File", self.workspace, "All Files (*.*)")
            if not path:
                return False
            ed.set_filepath(path)
        try:
            with open(ed.filepath, "w", encoding="utf-8") as f:
                f.write(ed.text())
        except OSError as e:
            self.toast(f"Save failed: {e}", theme.T["ERR"])
            return False
        ed.setModified(False)
        self._refresh_tab_title(ed)
        self.update_status()
        self.toast("Saved", theme.T["OK"])
        return True

    def show_find(self):
        self.find_bar.show()
        anim = QPropertyAnimation(self.find_bar, b"maximumHeight", self)
        anim.setDuration(160)
        anim.setStartValue(self.find_bar.height())
        anim.setEndValue(42)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._find_anim = anim
        self.find_edit.setFocus()
        self.find_edit.selectAll()

    def hide_find(self):
        anim = QPropertyAnimation(self.find_bar, b"maximumHeight", self)
        anim.setDuration(140)
        anim.setStartValue(self.find_bar.height())
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.find_bar.hide)
        anim.start()
        self._find_anim = anim
        ed = self.current_editor()
        if ed:
            ed.setFocus()

    def find(self, forward=True):
        ed = self.current_editor()
        text = self.find_edit.text()
        if not ed or not text:
            return
        if forward and text == self._last_find:
            found = ed.findNext()
        else:
            found = ed.findFirst(text, False, False, False, True, forward)
            self._last_find = text
        if not found:
            self.toast("Not found", theme.T["WARN"])

    def toggle_terminal(self):
        self.set_terminal_open(not self._term_open)

    def set_terminal_open(self, opened):
        self._term_open = opened
        if opened:
            self.term_body.show()
        target = self.TERM_OPEN_H if opened else self.TERM_CLOSED_H
        anim = QPropertyAnimation(self.term_panel, b"maximumHeight", self)
        anim.setDuration(200)
        anim.setStartValue(self.term_panel.height())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        if not opened:
            anim.finished.connect(self.term_body.hide)
        anim.start()
        self._term_anim = anim
        self.btn_toggle.setIcon(theme.vicon("chev_down" if opened else "chev_up", theme.T["MUTED"], 12))

    def clear_terminal(self):
        self.terminal_output.clear()

    def write_term(self, text, color="#cbd5e1"):
        cur = self.terminal_output.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cur.insertText(text, fmt)
        self.terminal_output.setTextCursor(cur)
        self.terminal_output.ensureCursorVisible()

    def send_stdin(self):
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return
        text = self.stdin_edit.text() + "\n"
        self.process.write(text.encode("utf-8"))
        self.write_term(text, theme.T["ACCENT"])
        self.stdin_edit.clear()

    def start_task(self, program, args, cwd, title, on_done=None, python=None):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.toast("Process is already running", theme.T["WARN"])
            return False

        self._on_done = on_done
        self.clear_terminal()
        if not self._term_open:
            self.set_terminal_open(True)
        self.write_term(f"› {title}\n", theme.T["TEXT"])
        self.write_term(f"$ {program} {' '.join(args)}\n{'─' * 50}\n", theme.T["SUBTLE"])

        env = QProcessEnvironment.systemEnvironment()
        venv = venv_root_of(python)
        if venv:
            bin_dir = os.path.join(venv, "Scripts" if os.name == "nt" else "bin")
            env.insert("VIRTUAL_ENV", venv)
            env.insert("PATH", bin_dir + os.pathsep + env.value("PATH", ""))
        env.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(cwd)
        self.process.start(program, args)
        self.set_running(True, title)
        return True

    def set_running(self, running, title=""):
        self.act_run.setEnabled(not running)
        self.act_stop.setEnabled(running)
        self.lbl_run.setText(f"Running · {title}" if running else "")
        if running:
            self.lbl_status.setText("Executing…")
        else:
            ed = self.current_editor()
            self.lbl_status.setText((ed.filepath or "Untitled") if ed else "Ready")

    def run_current_file(self):
        ed = self.current_editor()
        if not ed:
            return
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.toast("A process is already running", theme.T["WARN"])
            return
        if not self.save_editor(ed) or not ed.filepath:
            return

        ext = os.path.splitext(ed.filepath)[1].lower()
        cwd = os.path.dirname(ed.filepath)
        name = os.path.basename(ed.filepath)
        base = os.path.splitext(name)[0]

        if ext in (".html", ".htm"):
            self.open_html_preview()
            return

        python = None
        if ext in (".py", ".pyw"):
            py = self.cmb_py.currentData()
            if not py or not os.path.isfile(py):
                self.toast("Invalid Python runtime", theme.T["ERR"])
                return
            program, args, python = py, ["-u", ed.filepath], py
        elif ext in (".bat", ".cmd"):
            program, args = "cmd.exe", ["/c", ed.filepath]
        elif ext in (".sh", ".bash"):
            program, args = shutil.which("bash") or "bash", [ed.filepath]
        elif ext == ".js":
            runtime = shutil.which("bun") or shutil.which("node") or "node"
            program, args = runtime, [ed.filepath]
        elif ext == ".ts":
            runtime = shutil.which("bun") or shutil.which("ts-node") or shutil.which("deno")
            if runtime and "deno" in runtime:
                program, args = runtime, ["run", ed.filepath]
            else:
                program, args = runtime or "ts-node", [ed.filepath]
        elif ext == ".go":
            program, args = shutil.which("go") or "go", ["run", ed.filepath]
        elif ext == ".rs":
            program, args = shutil.which("rustc") or "rustc", [ed.filepath, "-o", os.path.join(cwd, base)]
        elif ext in (".c", ".cpp"):
            compiler = shutil.which("g++") or shutil.which("gcc") or shutil.which("clang++")
            if not compiler:
                self.toast("GCC / Clang not found", theme.T["ERR"])
                return
            out_bin = os.path.join(cwd, f"{base}.exe" if os.name == "nt" else base)
            program, args = compiler, [ed.filepath, "-o", out_bin]
        else:
            self.toast(f"No runner configured for {ext}", theme.T["WARN"])
            return

        self.start_task(program, args, cwd, name, python=python)

    def stop_process(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.write_term("\n[Process terminated]\n", theme.T["WARN"])

    def handle_stdout(self):
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="ignore")
        self.write_term(data, "#cbd5e1")

    def handle_stderr(self):
        data = bytes(self.process.readAllStandardError()).decode("utf-8", errors="ignore")
        self.write_term(data, theme.T["ERR"])

    def on_process_finished(self, code, status):
        ok = code == 0 and status == QProcess.ExitStatus.NormalExit
        self.write_term(f"\n{'─' * 50}\nExit code {code}\n",
                        theme.T["OK"] if ok else theme.T["ERR"])
        self.set_running(False)
        self.toast("Finished" if ok else f"Exit code {code}",
                   theme.T["OK"] if ok else theme.T["ERR"])
        cb, self._on_done = self._on_done, None
        if cb:
            cb(ok)

    def on_process_error(self, err):
        if err == QProcess.ProcessError.FailedToStart:
            self.write_term("\nFailed to spawn process.\n", theme.T["ERR"])
            self.set_running(False)
            self.toast("Launch failed", theme.T["ERR"])
            cb, self._on_done = self._on_done, None
            if cb:
                cb(False)

    def show_about(self):
        self.blurred(
            QMessageBox.about, self, APP_NAME,
            f"<h3 style='color:{theme.T['TEXT']};margin-bottom:4px;'>{APP_NAME}</h3>"
            f"<p style='color:{theme.T['MUTED']};margin-top:0;'>{VERSION} · Monolith Studio Architecture</p>"
            "<p>• Giao diện tối giản chuẩn Zed / Cursor.<br>"
            "• Hỗ trợ HTML Live Preview, Python, Batch, C/C++, Rust, Go, JS, TS, Shell.<br>"
            "• Đổi giao diện UI/UX trực tiếp (Obsidian, Tokyo Night, One Dark, Monokai).<br>"
            "• Quản lý Workspace & Virtual Environments tích hợp sẵn.</p>"
            f"<p style='color:{theme.T['MUTED']};'>By <b>{CREDIT}</b></p>"
        )

    def closeEvent(self, event):
        dirty = any(self.tab_widget.widget(i).isModified() for i in range(self.tab_widget.count()))
        if dirty:
            res = self.blurred(
                QMessageBox.question, self, "Quit",
                "You have unsaved files. Do you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if res != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(1000)
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()