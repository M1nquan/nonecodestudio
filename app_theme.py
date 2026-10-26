import os
from PyQt6.QtCore import Qt, QPointF, QRectF, QStandardPaths
from PyQt6.QtGui import (
    QBrush, QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QLinearGradient
)

ORG = "none"
APP_NAME = "None Code Studio"
APP_SUB = "v0.4b"
BROWSE = "__browse__"
CREDIT = "M1nquan"
VERSION = "v0.4b"

THEMES = {
    "Aerogel Obsidian": {
        "BG": "rgba(9, 10, 15, 0.75)",
        "PANEL": "rgba(13, 14, 21, 0.70)",
        "EDITOR": "rgba(11, 12, 18, 0.65)",
        "SURFACE": "rgba(19, 21, 32, 0.60)",
        "SURFACE_HOVER": "rgba(26, 29, 46, 0.75)",
        "BORDER": "rgba(40, 45, 68, 0.45)",
        "BORDER_ACTIVE": "#38bdf8",
        "TEXT": "#e2e8f0",
        "MUTED": "#64748b",
        "SUBTLE": "#334155",
        "PRIMARY": "#38bdf8",
        "PRIMARY_FG": "#090a0f",
        "ACCENT": "#818cf8",
        "OK": "#10b981",
        "ERR": "#f43f5e",
        "WARN": "#fbbf24",
    },
    "Cyber Neon": {
        "BG": "rgba(4, 5, 10, 0.78)",
        "PANEL": "rgba(7, 9, 19, 0.72)",
        "EDITOR": "rgba(5, 6, 13, 0.68)",
        "SURFACE": "rgba(13, 17, 36, 0.65)",
        "SURFACE_HOVER": "rgba(23, 30, 61, 0.80)",
        "BORDER": "rgba(26, 34, 74, 0.50)",
        "BORDER_ACTIVE": "#00f0ff",
        "TEXT": "#e0f2fe",
        "MUTED": "#7081b9",
        "SUBTLE": "#2d386b",
        "PRIMARY": "#00f0ff",
        "PRIMARY_FG": "#02040a",
        "ACCENT": "#ff007f",
        "OK": "#00ff9f",
        "ERR": "#ff2a6d",
        "WARN": "#ffe600",
    },
    "Hyper Violet": {
        "BG": "rgba(7, 3, 15, 0.78)",
        "PANEL": "rgba(12, 6, 26, 0.72)",
        "EDITOR": "rgba(8, 4, 18, 0.68)",
        "SURFACE": "rgba(23, 12, 48, 0.65)",
        "SURFACE_HOVER": "rgba(39, 21, 82, 0.80)",
        "BORDER": "rgba(47, 22, 97, 0.50)",
        "BORDER_ACTIVE": "#bd00ff",
        "TEXT": "#f5f3ff",
        "MUTED": "#8b76bd",
        "SUBTLE": "#42247a",
        "PRIMARY": "#bd00ff",
        "PRIMARY_FG": "#07030f",
        "ACCENT": "#00f5ff",
        "OK": "#10b981",
        "ERR": "#ff0055",
        "WARN": "#ffb703",
    },
    "Tokyo Night": {
        "BG": "rgba(26, 27, 38, 0.75)",
        "PANEL": "rgba(22, 22, 30, 0.70)",
        "EDITOR": "rgba(26, 27, 38, 0.65)",
        "SURFACE": "rgba(36, 40, 59, 0.60)",
        "SURFACE_HOVER": "rgba(47, 53, 79, 0.75)",
        "BORDER": "rgba(41, 46, 66, 0.50)",
        "BORDER_ACTIVE": "#7aa2f7",
        "TEXT": "#c0caf5",
        "MUTED": "#787c99",
        "SUBTLE": "#414868",
        "PRIMARY": "#7aa2f7",
        "PRIMARY_FG": "#15161e",
        "ACCENT": "#7dcfff",
        "OK": "#9ece6a",
        "ERR": "#f7768e",
        "WARN": "#e0af68",
    }
}

CURRENT_THEME_NAME = "Aerogel Obsidian"
T = dict(THEMES[CURRENT_THEME_NAME])

EDITOR_PALETTE = [
    ("comment", "#64748b"), ("string", "#10b981"), ("keyword", "#818cf8"),
    ("number", "#fbbf24"), ("class", "#38bdf8"), ("function", "#67e8f9"),
    ("preprocessor", "#f43f5e"), ("tag", "#38bdf8"), ("attribute", "#c084fc"),
    ("identifier", "#e2e8f0"), ("operator", "#38bdf8"),
]

STYLE_TEMPLATE = """
QWidget {
    color: @TEXT@;
    font-family: 'Segoe UI Variable Text', 'Consolas', 'Inter', -apple-system, sans-serif;
    font-size: 9.5pt;
}
QMainWindow {
    background: transparent;
}
QWidget#central {
    background: @BG@;
    border: 1px solid @BORDER@;
    border-radius: 12px;
}
QDialog {
    background: @PANEL@;
    border: 1.5px solid @BORDER_ACTIVE@;
    border-radius: 10px;
}
QToolTip {
    background: @SURFACE@;
    color: @TEXT@;
    border: 1px solid @BORDER_ACTIVE@;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 8.5pt;
}
QWidget#customTitleBar {
    background: transparent;
    border-bottom: 1px solid @BORDER@;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}
QToolButton#windowBtn, QToolButton#windowCloseBtn {
    background: transparent;
    color: @MUTED@;
    border: none;
    padding: 0px 14px;
    font-size: 9pt;
    font-weight: 700;
}
QToolButton#windowBtn:hover {
    background: @SURFACE@;
    color: @TEXT@;
}
QToolButton#windowCloseBtn:hover {
    background: @ERR@;
    color: #ffffff;
    border-top-right-radius: 11px;
}
QMenuBar {
    background: transparent;
    color: @MUTED@;
    padding: 3px 6px;
    border-bottom: 1px solid @BORDER@;
    font-size: 8.5pt;
}
QMenuBar::item {
    padding: 4px 9px;
    border-radius: 4px;
    background: transparent;
}
QMenuBar::item:selected {
    background: @SURFACE@;
    color: @TEXT@;
}
QMenu {
    background: @PANEL@;
    border: 1px solid @BORDER_ACTIVE@;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px 6px 12px;
    border-radius: 4px;
    color: @TEXT@;
}
QMenu::item:selected {
    background: @SURFACE_HOVER@;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: @BORDER@;
    margin: 4px 6px;
}
QToolBar {
    background: transparent;
    border: none;
    border-bottom: 1px solid @BORDER@;
    padding: 4px 8px;
    spacing: 6px;
}
QToolBar::separator {
    width: 1px;
    background: @BORDER@;
    margin: 4px;
}
QToolButton, QPushButton {
    background: @SURFACE@;
    color: @TEXT@;
    border: 1px solid @BORDER@;
    border-radius: 6px;
    padding: 4px 12px;
    font-weight: 500;
    font-size: 8.5pt;
}
QToolButton {
    background: transparent;
    color: @MUTED@;
    border-color: transparent;
}
QToolButton:hover, QPushButton:hover {
    color: @TEXT@;
    background: @SURFACE_HOVER@;
    border-color: @BORDER_ACTIVE@;
}
QToolButton:pressed, QPushButton:pressed {
    background: @BORDER_ACTIVE@;
    color: @PRIMARY_FG@;
}
QToolButton:disabled, QPushButton:disabled {
    color: @SUBTLE@;
    border-color: transparent;
}
QToolButton#primary, QPushButton#primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 @PRIMARY@, stop:1 @ACCENT@);
    color: @PRIMARY_FG@;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 6px;
    padding: 4px 15px;
    font-weight: 700;
}
QToolButton#primary:hover, QPushButton#primary:hover {
    background: #ffffff;
    color: #000000;
    border-color: #ffffff;
}
QToolButton#danger, QPushButton#danger {
    background: transparent;
    color: @ERR@;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 4px 10px;
    font-weight: 600;
}
QToolButton#danger:hover, QPushButton#danger:hover {
    background: rgba(244, 63, 94, 0.20);
    color: #ff6b81;
    border-color: @ERR@;
}
QComboBox#themeSelector, QComboBox#runtimePill {
    background: @SURFACE@;
    color: @TEXT@;
    border: 1px solid @BORDER@;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 8.5pt;
    font-weight: 600;
}
QComboBox#themeSelector:hover, QComboBox#runtimePill:hover {
    border-color: @BORDER_ACTIVE@;
}
QComboBox::drop-down {
    border: none;
    width: 16px;
}
QComboBox::down-arrow {
    image: url(@CHEV_D@);
    width: 8px;
    height: 8px;
}
QComboBox QAbstractItemView {
    background: @PANEL@;
    color: @TEXT@;
    border: 1px solid @BORDER_ACTIVE@;
    border-radius: 6px;
    outline: 0;
    padding: 4px;
    selection-background-color: @SURFACE_HOVER@;
}
QFrame#sidebar {
    background: @PANEL@;
    border-right: 1px solid @BORDER@;
}
QLabel#sidebarTitle {
    color: @SUBTLE@;
    font-size: 7.5pt;
    font-weight: 800;
    letter-spacing: 1.4px;
    padding: 10px 12px 2px 12px;
}
QLabel#wsName {
    color: @TEXT@;
    font-weight: 700;
    font-size: 9pt;
    padding: 0 12px 6px 12px;
}
QTreeView {
    background: transparent;
    border: none;
    outline: 0;
    padding: 2px 4px;
    color: @MUTED@;
    font-size: 9pt;
}
QTreeView::item {
    padding: 4px 6px;
    border-radius: 5px;
    margin: 1px 0;
}
QTreeView::item:hover {
    background: @SURFACE@;
    color: @TEXT@;
}
QTreeView::item:selected {
    background: @SURFACE_HOVER@;
    color: #ffffff;
    border-left: 2px solid @BORDER_ACTIVE@;
}
QTabWidget {
    border: none;
    background: transparent;
}
QTabWidget::pane {
    border: none;
    background: @EDITOR@;
}
QTabBar {
    background: transparent;
    border: none;
    qproperty-drawBase: 0;
}
QTabBar::tab {
    background: transparent;
    color: @MUTED@;
    padding: 7px 16px;
    margin: 0;
    border-right: 1px solid @BORDER@;
    border-top: 2px solid transparent;
    font-size: 8.5pt;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: @EDITOR@;
    color: @TEXT@;
    border-top: 2.5px solid @BORDER_ACTIVE@;
    font-weight: 700;
}
QTabBar::tab:hover:!selected {
    background: @SURFACE@;
    color: @TEXT@;
}
QTabBar::close-button {
    image: url(@CLOSE_N@);
    subcontrol-position: right;
    margin-left: 4px;
}
QTabBar::close-button:hover {
    image: url(@CLOSE_H@);
    background: @SURFACE_HOVER@;
    border-radius: 2px;
}
QToolButton#tabPlusBtn {
    background: transparent;
    border: none;
    border-left: 1px solid @BORDER@;
    padding: 4px 10px;
}
QToolButton#tabPlusBtn:hover {
    background: @SURFACE_HOVER@;
}
QFrame#findBar {
    background: @SURFACE@;
    border: 1px solid @BORDER_ACTIVE@;
    border-radius: 6px;
    margin: 4px 8px;
}
QLineEdit {
    background: @SURFACE@;
    border: 1px solid @BORDER@;
    border-radius: 5px;
    padding: 4px 8px;
    color: @TEXT@;
}
QLineEdit:focus {
    border-color: @BORDER_ACTIVE@;
}
QFrame#termPanel {
    background: @PANEL@;
    border-top: 1px solid @BORDER@;
}
QWidget#cardHeader {
    background: transparent;
    border-bottom: 1px solid @BORDER@;
}
QLabel#termTitle {
    color: @SUBTLE@;
    font-size: 7.5pt;
    font-weight: 800;
    letter-spacing: 1.2px;
}
QTextEdit#termOut {
    background: @EDITOR@;
    color: #e2e8f0;
    border: none;
    padding: 6px 10px;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
}
QLineEdit#termIn {
    background: @SURFACE@;
    border: 1px solid @BORDER@;
    border-radius: 5px;
    margin: 4px 8px 6px 8px;
    font-family: 'Consolas', monospace;
    padding: 4px 8px;
    font-size: 8.5pt;
    color: @TEXT@;
}
QLineEdit#termIn:focus {
    border-color: @BORDER_ACTIVE@;
}
QStatusBar {
    background: transparent;
    color: @MUTED@;
    min-height: 24px;
    border-top: 1px solid @BORDER@;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}
QStatusBar QLabel {
    color: @MUTED@;
    font-size: 8pt;
    padding: 0 6px;
}
QLabel#statusPill {
    background: @SURFACE@;
    color: @TEXT@;
    border: 1px solid @BORDER@;
    border-radius: 4px;
    padding: 1px 7px;
    font-weight: 600;
}
QSplitter::handle {
    background: @BORDER@;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
    border: none;
}
QScrollBar::handle:vertical {
    background: @SURFACE_HOVER@;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: @BORDER_ACTIVE@;
}
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    margin: 0;
    border: none;
}
QScrollBar::handle:horizontal {
    background: @SURFACE_HOVER@;
    border-radius: 3px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: @BORDER_ACTIVE@;
}
QFrame#splashCard {
    background: @PANEL@;
    border: 1.5px solid @BORDER_ACTIVE@;
    border-radius: 14px;
}
QLabel#title {
    color: @TEXT@;
    font-size: 17px;
    font-weight: 800;
}
QLabel#splashBadge {
    color: @MUTED@;
    font-size: 8.5pt;
    font-weight: 600;
}
QProgressBar {
    background: @SURFACE@;
    border: 1px solid @BORDER@;
    border-radius: 2px;
}
QProgressBar::chunk {
    border-radius: 2px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @PRIMARY@, stop:1 @ACCENT@);
}
"""

def set_theme(name):
    global CURRENT_THEME_NAME, T
    if name in THEMES:
        CURRENT_THEME_NAME = name
        T.clear()
        T.update(THEMES[name])

def draw_vector_icon(kind, color, size=14):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(1.3)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)

    s = float(size)
    if kind == "close":
        p.drawLine(QPointF(s * 0.28, s * 0.28), QPointF(s * 0.72, s * 0.72))
        p.drawLine(QPointF(s * 0.72, s * 0.28), QPointF(s * 0.28, s * 0.72))
    elif kind == "plus":
        p.drawLine(QPointF(s * 0.5, s * 0.22), QPointF(s * 0.5, s * 0.78))
        p.drawLine(QPointF(s * 0.22, s * 0.5), QPointF(s * 0.78, s * 0.5))
    elif kind == "chev_down":
        p.drawLine(QPointF(s * 0.28, s * 0.40), QPointF(s * 0.5, s * 0.62))
        p.drawLine(QPointF(s * 0.5, s * 0.62), QPointF(s * 0.72, s * 0.40))
    elif kind == "chev_up":
        p.drawLine(QPointF(s * 0.28, s * 0.60), QPointF(s * 0.5, s * 0.38))
        p.drawLine(QPointF(s * 0.5, s * 0.38), QPointF(s * 0.72, s * 0.60))
    elif kind == "play":
        p.setPen(Qt.PenStyle.NoPen)
        grad = QLinearGradient(0, 0, s, s)
        grad.setColorAt(0, QColor(T["PRIMARY"]))
        grad.setColorAt(1, QColor(T["ACCENT"]))
        p.setBrush(QBrush(grad))
        p.drawPolygon(QPolygonF([
            QPointF(s * 0.28, s * 0.20), QPointF(s * 0.80, s * 0.50), QPointF(s * 0.28, s * 0.80),
        ]))
    elif kind == "stop":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(color)))
        p.drawRoundedRect(QRectF(s * 0.25, s * 0.25, s * 0.5, s * 0.5), 1.5, 1.5)
    elif kind == "folder":
        path = QPainterPath()
        path.moveTo(s * 0.15, s * 0.30)
        path.lineTo(s * 0.42, s * 0.30)
        path.lineTo(s * 0.50, s * 0.40)
        path.lineTo(s * 0.85, s * 0.40)
        path.lineTo(s * 0.85, s * 0.75)
        path.lineTo(s * 0.15, s * 0.75)
        path.closeSubpath()
        p.drawPath(path)
    elif kind == "git":
        p.drawEllipse(QPointF(s * 0.32, s * 0.28), s * 0.08, s * 0.08)
        p.drawEllipse(QPointF(s * 0.32, s * 0.72), s * 0.08, s * 0.08)
        p.drawEllipse(QPointF(s * 0.68, s * 0.50), s * 0.08, s * 0.08)
        p.drawLine(QPointF(s * 0.32, s * 0.36), QPointF(s * 0.32, s * 0.64))
        p.drawLine(QPointF(s * 0.40, s * 0.32), QPointF(s * 0.60, s * 0.46))
    elif kind == "save":
        p.drawRoundedRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), 2.0, 2.0)
        p.drawRect(QRectF(s * 0.34, s * 0.2, s * 0.32, s * 0.22))
        p.drawLine(QPointF(s * 0.34, s * 0.60), QPointF(s * 0.66, s * 0.60))
    elif kind == "search":
        p.drawEllipse(QPointF(s * 0.42, s * 0.42), s * 0.22, s * 0.22)
        p.drawLine(QPointF(s * 0.58, s * 0.58), QPointF(s * 0.78, s * 0.78))
    elif kind == "globe":
        p.drawEllipse(QPointF(s * 0.5, s * 0.5), s * 0.32, s * 0.32)
        p.drawLine(QPointF(s * 0.18, s * 0.5), QPointF(s * 0.82, s * 0.5))
        p.drawEllipse(QPointF(s * 0.5, s * 0.5), s * 0.16, s * 0.32)
    elif kind == "box":
        p.drawRoundedRect(QRectF(s * 0.18, s * 0.22, s * 0.64, s * 0.56), 2.0, 2.0)
        p.drawLine(QPointF(s * 0.32, s * 0.42), QPointF(s * 0.45, s * 0.52))
        p.drawLine(QPointF(s * 0.45, s * 0.52), QPointF(s * 0.32, s * 0.62))
        p.drawLine(QPointF(s * 0.52, s * 0.62), QPointF(s * 0.66, s * 0.62))
    p.end()
    return pm

def vicon(kind, color=None, size=14):
    return QIcon(draw_vector_icon(kind, color or T["MUTED"], size))

def make_style_assets():
    base = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation), "ncs_v04b_assets")
    os.makedirs(base, exist_ok=True)
    assets = {
        "CLOSE_N": ("close", T["MUTED"], 12),
        "CLOSE_H": ("close", T["TEXT"], 12),
        "CHEV_D": ("chev_down", T["MUTED"], 10)
    }
    out = {}
    for key, (kind, col, sz) in assets.items():
        path = os.path.join(base, f"{CURRENT_THEME_NAME}_{key.lower()}.png")
        draw_vector_icon(kind, col, sz).save(path, "PNG")
        out[key] = path.replace("\\", "/")
    return out

def build_style():
    vals = dict(T)
    vals.update(make_style_assets())
    s = STYLE_TEMPLATE
    for k, v in vals.items():
        s = s.replace(f"@{k}@", v)
    return s

def make_logo(size=48):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    rect = QRectF(1.5, 1.5, size - 3.0, size - 3.0)
    path = QPainterPath()
    path.addRoundedRect(rect, size * 0.26, size * 0.26)
    
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor(T["SURFACE"]))
    grad.setColorAt(1, QColor(T["PANEL"]))
    p.fillPath(path, QBrush(grad))

    pen = QPen(QColor(T["BORDER_ACTIVE"]))
    pen.setWidthF(1.4)
    p.setPen(pen)
    p.drawPath(path)

    cli_pen = QPen(QColor(T["PRIMARY"]))
    cli_pen.setWidthF(max(2.0, size * 0.08))
    cli_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    cli_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(cli_pen)
    p.drawLine(QPointF(size * 0.28, size * 0.32), QPointF(size * 0.44, size * 0.50))
    p.drawLine(QPointF(size * 0.44, size * 0.50), QPointF(size * 0.28, size * 0.68))

    under_pen = QPen(QColor(T["ACCENT"]))
    under_pen.setWidthF(max(2.0, size * 0.08))
    under_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(under_pen)
    p.drawLine(QPointF(size * 0.52, size * 0.68), QPointF(size * 0.72, size * 0.68))
    p.end()
    return pm

def gaussian_blur(pix, radius=10):
    if pix.isNull():
        return pix
    img = pix.toImage()
    w, h = max(1, img.width() // 5), max(1, img.height() // 5)
    small = img.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    blurred = small.scaled(img.width(), img.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return QPixmap.fromImage(blurred)