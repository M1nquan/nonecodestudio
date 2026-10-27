import os
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QFileDialog, QListWidget, QListWidgetItem
)
import app_theme as theme
from workers import parse_github_url, CloneWorker


class AnimatedDialog(QDialog):
    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(240)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._open_anim = anim


class CloneDialog(AnimatedDialog):
    def __init__(self, parent, default_dir):
        super().__init__(parent)
        self.setWindowTitle("Clone Repository")
        self.setMinimumWidth(500)
        self.worker = None
        self.result_path = None

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        title = QLabel("Clone Git Repository")
        title.setStyleSheet(f"font-size: 11.5pt; font-weight: 700; color: {theme.T['TEXT']};")
        hint = QLabel("Supports native git clone or direct GitHub ZIP archive download.")
        hint.setStyleSheet(f"color: {theme.T['MUTED']}; font-size: 8.5pt;")

        self.url = QLineEdit()
        self.url.setPlaceholderText("owner/repo or complete GitHub link...")
        self.branch = QLineEdit()
        self.branch.setPlaceholderText("Default branch (main / master)")
        self.dest = QLineEdit(default_dir)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self.pick_dir)
        dest_row = QHBoxLayout()
        dest_row.setSpacing(6)
        dest_row.addWidget(self.dest, 1)
        dest_row.addWidget(btn_browse)

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Repository", self.url)
        form.addRow("Branch", self.branch)
        form.addRow("Destination", dest_row)

        self.log = QLabel("")
        self.log.setStyleSheet(f"color: {theme.T['MUTED']}; font-size: 8.5pt;")
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(3)
        self.bar.hide()

        self.btn_ok = QPushButton("Clone")
        self.btn_ok.setObjectName("primary")
        self.btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ok.clicked.connect(self.start)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(self.btn_ok)

        lay.addWidget(title)
        lay.addWidget(hint)
        lay.addLayout(form)
        lay.addWidget(self.bar)
        lay.addWidget(self.log)
        lay.addLayout(buttons)

    def pick_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Save Location", self.dest.text())
        if d:
            self.dest.setText(d)

    def start(self):
        info = parse_github_url(self.url.text())
        if not info:
            self.log.setText("Invalid GitHub URL or path.")
            return
        owner, repo, branch_from_url = info
        branch = self.branch.text().strip() or branch_from_url
        parent_dir = self.dest.text().strip()
        if not os.path.isdir(parent_dir):
            self.log.setText("Target destination directory does not exist.")
            return
        self.btn_ok.setEnabled(False)
        self.bar.show()
        self.worker = CloneWorker(owner, repo, branch, parent_dir)
        self.worker.log.connect(self.log.setText)
        self.worker.succeeded.connect(self._ok)
        self.worker.failed.connect(self._fail)
        self.worker.start()

    def _ok(self, path):
        self.result_path = path
        self.accept()

    def _fail(self, msg):
        self.bar.hide()
        self.btn_ok.setEnabled(True)
        self.log.setText(msg)


class VenvDialog(AnimatedDialog):
    def __init__(self, win):
        super().__init__(win)
        self.win = win
        self.setWindowTitle("Python Environments")
        self.setMinimumSize(540, 380)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(10)

        title = QLabel("Python Runtimes")
        title.setStyleSheet(f"font-size: 11.5pt; font-weight: 700; color: {theme.T['TEXT']};")
        hint = QLabel(f"Active Workspace: {win.workspace}")
        hint.setStyleSheet(f"color: {theme.T['MUTED']}; font-size: 8.5pt;")

        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(lambda _i: self.use_selected())

        row = QHBoxLayout()
        row.setSpacing(8)

        self.btn_use = QPushButton("Set Default")
        self.btn_use.setObjectName("primary")
        self.btn_use.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_use.clicked.connect(self.use_selected)

        self.btn_req = QPushButton("Install requirements.txt")
        self.btn_req.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_req.clicked.connect(self.install_selected)

        self.btn_del = QPushButton("Delete venv")
        self.btn_del.setObjectName("danger")
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.clicked.connect(self.delete_selected)

        row.addWidget(self.btn_use)
        row.addWidget(self.btn_req)
        row.addWidget(self.btn_del)
        row.addStretch()

        bottom = QHBoxLayout()
        btn_new = QPushButton("Create new venv")
        btn_new.setIcon(theme.vicon("plus", theme.T["TEXT"], 13))
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self.create_new)

        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.reject)

        bottom.addWidget(btn_new)
        bottom.addStretch()
        bottom.addWidget(btn_close)

        lay.addWidget(title)
        lay.addWidget(hint)
        lay.addWidget(self.list, 1)
        lay.addLayout(row)
        lay.addLayout(bottom)
        self.populate()

    def populate(self):
        self.list.clear()
        for label, path in self.win.interpreters():
            item = QListWidgetItem(f"{label}\n{path}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.list.addItem(item)
        self.list.setCurrentRow(max(0, self.win.cmb_py.currentIndex()))

    def selected_path(self):
        item = self.list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def use_selected(self):
        path = self.selected_path()
        if path:
            self.win.refresh_interpreters(select=path)
            self.accept()

    def install_selected(self):
        path = self.selected_path()
        if path:
            self.accept()
            self.win.install_requirements(path)

    def delete_selected(self):
        path = self.selected_path()
        if path and self.win.delete_venv(path):
            self.populate()
            self.win.refresh_interpreters()

    def create_new(self):
        self.accept()
        self.win.prompt_create_venv()