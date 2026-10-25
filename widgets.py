from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QProgressBar
)
from theme import APP_NAME, CREDIT, VERSION, T, make_logo


def animate_widget_fade_in(widget, duration=220):
    """Không gắn QGraphicsOpacityEffect lên QsciScintilla/QTreeView để tránh lỗi QPainter."""
    pass


class Overlay(QWidget):
    MESSAGES = [
        "Initializing Monolith Engine...",
        "Loading Syntax Lexers...",
        "Mounting Workspace...",
        "Ready",
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._backdrop = None
        self._tint = 180
        self._alpha = 1.0
        self._fade = None
        self._load = None

        self.card = self._build_card()
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.card)
        row.addStretch()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch()
        root.addLayout(row)
        root.addStretch()
        self.hide()

    def get_alpha(self):
        return self._alpha

    def set_alpha(self, val):
        self._alpha = float(val)
        self.update()

    alpha = pyqtProperty(float, get_alpha, set_alpha)

    def _build_card(self):
        card = QFrame()
        card.setObjectName("splashCard")
        card.setFixedSize(380, 240)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(32, 28, 32, 24)
        lay.setSpacing(8)

        self.logo = QLabel()
        self.logo.setPixmap(make_logo(60))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(APP_NAME)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel(f"{CREDIT}  ·  {VERSION}")
        badge.setObjectName("splashBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_lbl = QLabel(self.MESSAGES[0])
        self.status_lbl.setStyleSheet(f"color: {T['MUTED']}; font-size: 8pt;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.intro_bar = QProgressBar()
        self.intro_bar.setRange(0, 100)
        self.intro_bar.setValue(0)
        self.intro_bar.setTextVisible(False)
        self.intro_bar.setFixedHeight(3)
        self.intro_bar.valueChanged.connect(self._on_progress)

        lay.addStretch()
        lay.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(4)
        lay.addWidget(title)
        lay.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)
        lay.addStretch()
        lay.addWidget(self.status_lbl)
        lay.addWidget(self.intro_bar)
        return card

    def _on_progress(self, val):
        idx = min(len(self.MESSAGES) - 1, val * len(self.MESSAGES) // 100)
        self.status_lbl.setText(self.MESSAGES[idx])

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setOpacity(self._alpha)
        if self._backdrop is not None:
            p.drawPixmap(self.rect(), self._backdrop)
        p.fillRect(self.rect(), QColor(9, 10, 15, self._tint))
        p.end()

    def set_backdrop(self, pix, tint):
        self._backdrop = pix
        self._tint = tint
        self.update()

    def start_intro(self, pix, on_done=None):
        self.set_backdrop(pix, 195)
        self.card.show()
        self._alpha = 1.0
        self.intro_bar.setValue(0)
        self.show()
        self.raise_()

        anim = QPropertyAnimation(self.intro_bar, b"value", self)
        anim.setDuration(1400)
        anim.setStartValue(0)
        anim.setEndValue(100)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def finished():
            QTimer.singleShot(150, lambda: self.fade_out(300, on_done))
        anim.finished.connect(finished)
        anim.start()
        self._load = anim

    def show_backdrop(self, pix):
        self.set_backdrop(pix, 150)
        self.card.hide()
        self._alpha = 0.0
        self.show()
        self.raise_()

        anim = QPropertyAnimation(self, b"alpha", self)
        anim.setDuration(160)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._fade = anim

    def fade_out(self, duration=200, on_done=None):
        self.card.hide()
        anim = QPropertyAnimation(self, b"alpha", self)
        anim.setDuration(duration)
        anim.setStartValue(self._alpha)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def finished():
            self.hide()
            if on_done:
                on_done()
        anim.finished.connect(finished)
        anim.start()
        self._fade = anim


class Toast(QFrame):
    def __init__(self, parent, text, accent_color):
        for old in parent.findChildren(Toast):
            old.deleteLater()
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background: {T['SURFACE']}; border: 1px solid {T['BORDER_ACTIVE']}; "
            f"border-radius: 8px; }}"
            f"QLabel {{ color: {T['TEXT']}; border: none; background: transparent; font-size: 8.5pt; font-weight: 600; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 16, 8)
        lay.setSpacing(9)

        dot = QLabel()
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(f"background: {accent_color}; border-radius: 3.5px;")
        lbl = QLabel(text)
        lay.addWidget(dot)
        lay.addWidget(lbl)
        self.adjustSize()

        end = QPoint(parent.width() - self.width() - 24,
                     parent.height() - self.height() - 38)
        start = end + QPoint(40, 0)
        self.move(start)
        self.show()
        self.raise_()

        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setDuration(300)
        pos_anim.setStartValue(start)
        pos_anim.setEndValue(end)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        pos_anim.start()
        self._in = pos_anim
        QTimer.singleShot(2200, self._slide_out)

    def _slide_out(self):
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(220)
        anim.setStartValue(self.pos())
        anim.setEndValue(self.pos() + QPoint(0, 40))
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self.deleteLater)
        anim.start()
        self._out = anim