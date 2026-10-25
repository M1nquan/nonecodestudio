import os
from PyQt6.QtCore import Qt, QPointF, QRectF, QStandardPaths
from PyQt6.QtGui import (
    QBrush, QColor, QIcon, QImage, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
)

ORG, APP_NAME = "none", "none code studio"
BROWSE = "__browse__"
CREDIT = "none"
VERSION = "ver 0.2b"

THEMES = {
    "Deep Obsidian": {
        "BG": "#090a0f", "PANEL": "#0d0e15", "EDITOR": "#0b0c12",
        "SURFACE": "#131520", "SURFACE_HOVER": "#1a1d2e", "BORDER": "#191c2b",
        "BORDER_ACTIVE": "#282d44", "TEXT": "#e2e8f0", "MUTED": "#64748b",
        "SUBTLE": "#334155", "PRIMARY": "#f8fafc", "PRIMARY_FG": "#090a0f",
        "ACCENT": "#38bdf8", "OK": "#10b981", "ERR": "#f43f5e", "WARN": "#fbbf24",
    },
    "Tokyo Night": {
        "BG": "#1a1b26", "PANEL": "#16161e", "EDITOR": "#1a1b26",
        "SURFACE": "#24283b", "SURFACE_HOVER": "#2f354f", "BORDER": "#292e42",
        "BORDER_ACTIVE": "#3d59a1", "TEXT": "#c0caf5", "MUTED": "#787c99",
        "SUBTLE": "#414868", "PRIMARY": "#7aa2f7", "PRIMARY_FG": "#15161e",
        "ACCENT": "#7dcfff", "OK": "#9ece6a", "ERR": "#f7768e", "WARN": "#e0af68",
    },
    "One Dark Pro": {
        "BG": "#21252b", "PANEL": "#1e2227", "EDITOR": "#282c34",
        "SURFACE": "#2c313a", "SURFACE_HOVER": "#3e4451", "BORDER": "#181a1f",
        "BORDER_ACTIVE": "#4b5263", "TEXT": "#abb2bf", "MUTED": "#5c6370",
        "SUBTLE": "#4b5263", "PRIMARY": "#61afef", "PRIMARY_FG": "#1e2227",
        "ACCENT": "#56b6c2", "OK": "#98c379", "ERR": "#e06c75", "WARN": "#e5c07b",
    },
    "Monokai Pro": {
        "BG": "#221f22", "PANEL": "#19181a", "EDITOR": "#2d2a2e",
        "SURFACE": "#3a373b", "SURFACE_HOVER": "#4a474b", "BORDER": "#19181a",
        "BORDER_ACTIVE": "#5b595c", "TEXT": "#fcfcfa", "MUTED": "#727072",
        "SUBTLE": "#403e41", "PRIMARY": "#ffd866", "PRIMARY_FG": "#221f22",
        "ACCENT": "#a9dc76", "OK": "#a9dc76", "ERR": "#ff6188", "WARN": "#fc9867",
    }
}

CURRENT_THEME_NAME = "Deep Obsidian"
T = dict(THEMES[CURRENT_THEME_NAME])

EDITOR_PALETTE = [
    ("comment", "#64748b"), ("string", "#86efac"), ("keyword", "#c084fc"),
    ("number", "#fb923c"), ("class", "#38bdf8"), ("function", "#60a5fa"),
    ("preprocessor", "#f472b6"), ("tag", "#38bdf8"), ("attribute", "#93c5fd"),
    ("identifier", "#cbd5e1"), ("operator", "#94a3b8"),
]

STYLE_TEMPLATE = """
QWidget {
    color: @TEXT@;
    font-family: 'Segoe UI Variable Text', 'Inter', 'Segoe UI', -apple-system, sans-serif;
    font-size: 9.5pt;
}
QMainWindow, QWidget#central { background: @BG@; }
QDialog { background: @PANEL@; border: 1px solid @BORDER_ACTIVE@; border-radius: 8px; }
QToolTip {
    background: @SURFACE@; color: @TEXT@; border: 1px solid @BORDER_ACTIVE@;
    padding: 5px 9px; border-radius: 4px; font-size: 8.5pt;
}
QWidget#customTitleBar { background: @BG@; border-bottom: 1px solid @BORDER@; }
QToolButton#windowBtn, QToolButton#windowCloseBtn {
    background: transparent; color: @MUTED@; border: none; padding: 0px 14px; font-size: 9pt; font-weight: 600;
}
QToolButton#windowBtn:hover { background: @SURFACE@; color: @TEXT@; }
QToolButton#windowCloseBtn:hover { background: @ERR@; color: #ffffff; }

QMenuBar {
    background: @BG@; color: @MUTED@; padding: 2px 6px; border-bottom: 1px solid @BORDER@; font-size: 8.5pt;
}
QMenuBar::item { padding: 4px 8px; border-radius: 4px; background: transparent; }
QMenuBar::item:selected { background: @SURFACE@; color: @TEXT@; }
QMenu { background: @SURFACE@; border: 1px solid @BORDER_ACTIVE@; border-radius: 6px; padding: 4px; }
QMenu::item { padding: 5px 20px 5px 10px; border-radius: 4px; color: @TEXT@; }
QMenu::item:selected { background: @SURFACE_HOVER@; color: #ffffff; }
QMenu::separator { height: 1px; background: @BORDER@; margin: 4px 6px; }

QToolBar { background: @BG@; border: none; border-bottom: 1px solid @BORDER@; padding: 3px 8px; spacing: 5px; }
QToolBar::separator { width: 1px; background: @BORDER@; margin: 4px; }

QToolButton, QPushButton {
    background: @SURFACE@; color: @TEXT@; border: 1px solid @BORDER@;
    border-radius: 5px; padding: 4px 10px; font-weight: 500; font-size: 8.5pt;
}
QToolButton { background: transparent; color: @MUTED@; border-color: transparent; }
QToolButton:hover, QPushButton:hover { color: @TEXT@; background: @SURFACE_HOVER@; border-color: @BORDER_ACTIVE@; }
QToolButton:pressed, QPushButton:pressed { background: @BORDER_ACTIVE@; }
QToolButton:disabled, QPushButton:disabled { color: @SUBTLE@; border-color: transparent; }

QToolButton#primary, QPushButton#primary {
    background-color: @PRIMARY@; color: @PRIMARY_FG@; border: 1px solid @PRIMARY@;
    border-radius: 5px; padding: 4px 14px; font-weight: 700;
}
QToolButton#primary:hover, QPushButton#primary:hover { background-color: #ffffff; color: #000000; border-color: #ffffff; }

QToolButton#danger, QPushButton#danger {
    background: transparent; color: @ERR@; border: 1px solid transparent; border-radius: 5px; padding: 4px 10px; font-weight: 600;
}
QToolButton#danger:hover, QPushButton#danger:hover { background: rgba(244, 63, 94, 0.16); color: #ff6b81; border-color: @ERR@; }

QComboBox#themeSelector, QComboBox#runtimePill {
    background: @SURFACE@; color: @TEXT@; border: 1px solid @BORDER@; border-radius: 5px; padding: 2px 8px; font-size: 8.5pt;
}
QComboBox#themeSelector:hover, QComboBox#runtimePill:hover { border-color: @BORDER_ACTIVE@; }
QComboBox::drop-down { border: none; width: 16px; }
QComboBox::down-arrow { image: url(@CHEV_D@); width: 8px; height: 8px; }
QComboBox QAbstractItemView {
    background: @SURFACE@; color: @TEXT@; border: 1px solid @BORDER_ACTIVE@;
    border-radius: 4px; outline: 0; padding: 3px; selection-background-color: @SURFACE_HOVER@;
}

QFrame#sidebar { background: @PANEL@; border-right: 1px solid @BORDER@; }
QLabel#sidebarTitle { color: @SUBTLE@; font-size: 7.5pt; font-weight: 700; letter-spacing: 1.2px; padding: 10px 12px 2px 12px; }
QLabel#wsName { color: @TEXT@; font-weight: 600; font-size: 9pt; padding: 0 12px 6px 12px; }
QTreeView { background: transparent; border: none; outline: 0; padding: 2px 4px; color: @MUTED@; font-size: 9pt; }
QTreeView::item { padding: 3px 6px; border-radius: 4px; margin: 1px 0; }
QTreeView::item:hover { background: @SURFACE@; color: @TEXT@; }
QTreeView::item:selected { background: @SURFACE_HOVER@; color: #ffffff; }

QTabWidget { border: none; background: @BG@; }
QTabWidget::pane { border: none; background: @EDITOR@; }
QTabBar { background: @BG@; border: none; qproperty-drawBase: 0; }
QTabBar::tab { background: @BG@; color: @MUTED@; padding: 6px 14px; margin: 0; border-right: 1px solid @BORDER@; border-top: 2px solid transparent; font-size: 8.5pt; }
QTabBar::tab:selected { background: @EDITOR@; color: @TEXT@; border-top: 2px solid @ACCENT@; font-weight: 600; }
QTabBar::tab:hover:!selected { background: @PANEL@; color: @TEXT@; }
QTabBar::close-button { image: url(@CLOSE_N@); subcontrol-position: right; margin-left: 4px; }
QTabBar::close-button:hover { image: url(@CLOSE_H@); background: @SURFACE_HOVER@; border-radius: 2px; }

QToolButton#tabPlusBtn { background: @BG@; border: none; border-left: 1px solid @BORDER@; border-radius: 0px; padding: 4px 8px; }
QToolButton#tabPlusBtn:hover { background: @SURFACE_HOVER@; }

QFrame#findBar { background: @SURFACE@; border: 1px solid @BORDER_ACTIVE@; border-radius: 6px; margin: 4px 8px; }
QLineEdit { background: @SURFACE@; border: 1px solid @BORDER@; border-radius: 4px; padding: 4px 8px; color: @TEXT@; }
QLineEdit:focus { border-color: @ACCENT@; }

QFrame#termPanel { background: @PANEL@; border-top: 1px solid @BORDER@; }
QWidget#cardHeader { background: @BG@; border-bottom: 1px solid @BORDER@; }
QLabel#termTitle { color: @SUBTLE@; font-size: 7.5pt; font-weight: 700; letter-spacing: 1px; }
QTextEdit#termOut { background: @EDITOR@; color: #e2e8f0; border: none; padding: 6px 10px; font-family: 'Consolas', monospace; font-size: 9pt; }
QLineEdit#termIn { background: @SURFACE@; border: 1px solid @BORDER@; border-radius: 4px; margin: 4px 8px 6px 8px; font-family: 'Consolas', monospace; padding: 4px 8px; font-size: 8.5pt; }

QStatusBar { background: @BG@; color: @MUTED@; min-height: 22px; border-top: 1px solid @BORDER@; }
QStatusBar QLabel { color: @MUTED@; font-size: 8pt; padding: 0 6px; }
QLabel#statusPill { background: @SURFACE@; color: @TEXT@; border: 1px solid @BORDER@; border-radius: 3px; padding: 1px 6px; font-weight: 600; }

QSplitter::handle { background: @BORDER@; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

QScrollBar:vertical { background: @EDITOR@; width: 6px; margin: 0; border: none; }
QScrollBar::handle:vertical { background: #1e2436; border-radius: 3px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #334155; }

QScrollBar:horizontal { background: @EDITOR@; height: 6px; margin: 0; border: none; }
QScrollBar::handle:horizontal { background: #1e2436; border-radius: 3px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #334155; }

QFrame#splashCard { background: @PANEL@; border: 1px solid @BORDER_ACTIVE@; border-radius: 12px; }
QLabel#title { color: @TEXT@; font-size: 15px; font-weight: 700; }
QLabel#splashBadge { color: @MUTED@; font-size: 8pt; font-weight: 500; }
QProgressBar { background: @SURFACE@; border: none; border-radius: 1px; }
QProgressBar::chunk { border-radius: 1px; background: @ACCENT@; }
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
        p.setBrush(QBrush(QColor(color)))
        p.drawPolygon(QPolygonF([
            QPointF(s * 0.28, s * 0.20), QPointF(s * 0.78, s * 0.50), QPointF(s * 0.28, s * 0.80),
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
    base = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation), "none_studio_assets_v2")
    os.makedirs(base, exist_ok=True)
    assets = {"CLOSE_N": ("close", T["MUTED"], 12), "CLOSE_H": ("close", T["TEXT"], 12), "CHEV_D": ("chev_down", T["MUTED"], 10)}
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

    rect = QRectF(1.0, 1.0, size - 2.0, size - 2.0)
    path = QPainterPath()
    path.addRoundedRect(rect, size * 0.25, size * 0.25)
    p.fillPath(path, QBrush(QColor(T["SURFACE"])))

    pen = QPen(QColor(T["BORDER_ACTIVE"]))
    pen.setWidthF(1.2)
    p.setPen(pen)
    p.drawPath(path)

    cli_pen = QPen(QColor(T["ACCENT"]))
    cli_pen.setWidthF(max(2.0, size * 0.08))
    cli_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    cli_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(cli_pen)
    p.drawLine(QPointF(size * 0.30, size * 0.34), QPointF(size * 0.46, size * 0.50))
    p.drawLine(QPointF(size * 0.46, size * 0.50), QPointF(size * 0.30, size * 0.66))

    under_pen = QPen(QColor(T["PRIMARY"]))
    under_pen.setWidthF(max(2.0, size * 0.08))
    under_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(under_pen)
    p.drawLine(QPointF(size * 0.54, size * 0.66), QPointF(size * 0.70, size * 0.66))
    p.end()
    return pm

def gaussian_blur(pix, radius=10):
    if pix.isNull():
        return pix
    img = pix.toImage()
    w, h = max(1, img.width() // 6), max(1, img.height() // 6)
    small = img.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    blurred = small.scaled(img.width(), img.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    return QPixmap.fromImage(blurred)  # Đã sửa: Phải trả về QPixmap