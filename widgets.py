from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QParallelAnimationGroup,
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QProgressBar,
    QGraphicsOpacityEffect
)
import app_theme as theme


def animate_widget_fade_in(widget, duration=220):
    pass


class Overlay(QWidget):
    MESSAGES = [
        "Initializing Monolith Studio Engine...",
        "Loading Dynamic Syntax Lexers...",
        "Preparing Hardware Accelerated Surface...",
        "Mounting Workspace Tree...",
        "Workspace Ready",
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self._backdrop = None
        self._tint = 200
        self._alpha = 1.0
        self._fade = None
        self._load = None
        self._card_anim = None

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
        card.setFixedSize(400, 250)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(34, 30, 34, 26)
        lay.setSpacing(10)

        self.logo = QLabel()
        self.logo.setPixmap(theme.make_logo(64))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel(theme.APP_NAME)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel(f"{theme.CREDIT}  ·  {theme.VERSION}")
        badge.setObjectName("splashBadge")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_lbl = QLabel(self.MESSAGES[0])
        self.status_lbl.setStyleSheet(f"color: {theme.T['BORDER_ACTIVE']}; font-size: 8.5pt; font-weight: 700;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.intro_bar = QProgressBar()
        self.intro_bar.setRange(0, 100)
        self.intro_bar.setValue(0)
        self.intro_bar.setTextVisible(False)
        self.intro_bar.setFixedHeight(4)
        self.intro_bar.valueChanged.connect(self._on_progress)

        lay.addStretch()
        lay.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(2)
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
        p.fillRect(self.rect(), QColor(6, 12, 24, self._tint))
        p.end()

    def set_backdrop(self, pix, tint):
        self._backdrop = pix
        self._tint = tint
        self.update()

    def start_intro(self, pix, on_done=None):
        self.set_backdrop(pix, 210)
        self.card.show()
        self._alpha = 1.0
        self.intro_bar.setValue(0)
        self.show()
        self.raise_()

        group = QParallelAnimationGroup(self)

        bar_anim = QPropertyAnimation(self.intro_bar, b"value", self)
        bar_anim.setDuration(2200)
        bar_anim.setStartValue(0)
        bar_anim.setEndValue(100)
        bar_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

        card_effect = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(card_effect)
        fade_card = QPropertyAnimation(card_effect, b"opacity", self)
        fade_card.setDuration(900)
        fade_card.setStartValue(0.0)
        fade_card.setEndValue(1.0)
        fade_card.setEasingCurve(QEasingCurve.Type.OutCubic)

        group.addAnimation(bar_anim)
        group.addAnimation(fade_card)

        def finished():
            QTimer.singleShot(200, lambda: self.fade_out(450, on_done))

        group.finished.connect(finished)
        group.start()
        self._load = group

    def show_backdrop(self, pix):
        self.set_backdrop(pix, 160)
        self.card.hide()
        self._alpha = 0.0
        self.show()
        self.raise_()

        anim = QPropertyAnimation(self, b"alpha", self)
        anim.setDuration(240)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        anim.start()
        self._fade = anim

    def fade_out(self, duration=350, on_done=None):
        self.card.hide()
        anim = QPropertyAnimation(self, b"alpha", self)
        anim.setDuration(duration)
        anim.setStartValue(self._alpha)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

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
            f"QFrame {{ background: {theme.T['PANEL']}; border: 1.5px solid {accent_color}; "
            f"border-radius: 9px; }}"
            f"QLabel {{ color: {theme.T['TEXT']}; border: none; background: transparent; font-size: 8.5pt; font-weight: 700; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 9, 18, 9)
        lay.setSpacing(10)

        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {accent_color}; border-radius: 4px;")
        lbl = QLabel(text)
        lay.addWidget(dot)
        lay.addWidget(lbl)
        self.adjustSize()

        end = QPoint(parent.width() - self.width() - 24,
                     parent.height() - self.height() - 40)
        start = end + QPoint(80, 0)
        self.move(start)
        self.show()
        self.raise_()

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        self._in_group = QParallelAnimationGroup(self)

        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setDuration(420)
        pos_anim.setStartValue(start)
        pos_anim.setEndValue(end)
        pos_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        op_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        op_anim.setDuration(350)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(1.0)
        op_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._in_group.addAnimation(pos_anim)
        self._in_group.addAnimation(op_anim)
        self._in_group.start()

        QTimer.singleShot(2800, self._slide_out)

    def _slide_out(self):
        self._out_group = QParallelAnimationGroup(self)

        pos_anim = QPropertyAnimation(self, b"pos", self)
        pos_anim.setDuration(320)
        pos_anim.setStartValue(self.pos())
        pos_anim.setEndValue(self.pos() + QPoint(60, 0))
        pos_anim.setEasingCurve(QEasingCurve.Type.InBack)

        op_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        op_anim.setDuration(280)
        op_anim.setStartValue(1.0)
        op_anim.setEndValue(0.0)
        op_anim.setEasingCurve(QEasingCurve.Type.InQuad)

        self._out_group.addAnimation(pos_anim)
        self._out_group.addAnimation(op_anim)
        self._out_group.finished.connect(self.deleteLater)
        self._out_group.start()