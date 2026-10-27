import os
import subprocess
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QParallelAnimationGroup,
    QEasingCurve, pyqtProperty
)
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QProgressBar,
    QToolButton, QGraphicsOpacityEffect
)
import app_theme as theme


class AnimatedWindowButton(QToolButton):
    def __init__(self, text, parent=None, is_close=False):
        super().__init__(parent)
        self.setText(text)
        self._is_close = is_close
        self._scale = 1.0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(46, 34)

        if is_close:
            self.setObjectName("windowCloseBtn")
        else:
            self.setObjectName("windowBtn")

        self._anim = None

    def get_scale(self):
        return self._scale

    def set_scale(self, val):
        self._scale = float(val)
        self.update()

    scale = pyqtProperty(float, get_scale, set_scale)

    def enterEvent(self, event):
        self._animate_scale(1.18, 180, QEasingCurve.Type.OutBack)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_scale(1.0, 160, QEasingCurve.Type.OutQuad)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._animate_scale(0.88, 80, QEasingCurve.Type.InQuad)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._animate_scale(1.12, 140, QEasingCurve.Type.OutBack)
        super().mouseReleaseEvent(event)

    def _animate_scale(self, target, duration, easing):
        if self._anim is not None:
            self._anim.stop()
        anim = QPropertyAnimation(self, b"scale", self)
        anim.setDuration(duration)
        anim.setStartValue(self._scale)
        anim.setEndValue(target)
        anim.setEasingCurve(easing)
        anim.start()
        self._anim = anim

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        painter.translate(cx, cy)
        painter.scale(self._scale, self._scale)
        painter.translate(-cx, -cy)

        super().paintEvent(event)
        painter.end()


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


class MusicWatermark(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("musicWatermark")
        self.setStyleSheet(
            f"QFrame#musicWatermark {{"
            f"  background: {theme.T['SURFACE']};"
            f"  border: 1px solid {theme.T['BORDER_ACTIVE']};"
            f"  border-radius: 8px;"
            f"}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 5, 12, 5)
        lay.setSpacing(8)

        self.icon_lbl = QLabel()
        self.icon_lbl.setPixmap(theme.draw_vector_icon("music", theme.T["ACCENT"], 13))

        self.text_lbl = QLabel("None Code Studio • Ready")
        self.text_lbl.setStyleSheet(f"color: {theme.T['TEXT']}; font-size: 8pt; font-weight: 600; font-family: 'Segoe UI Variable Text';")

        lay.addWidget(self.icon_lbl)
        lay.addWidget(self.text_lbl)

        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.9)
        self.setGraphicsEffect(self._opacity)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.poll_media)
        self._timer.start(3000)
        self.poll_media()

    def poll_media(self):
        title = ""
        if os.name == "nt":
            try:
                cmd = 'powershell -NoProfile -Command "(Get-Process | Where-Object {$_.MainWindowTitle -ne \'\' -and ($_.ProcessName -match \'spotify|music|chrome|msedge|brave\')} | Select-Object -ExpandProperty MainWindowTitle -First 1)"'
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=1.5)
                out = res.stdout.strip()
                if out and out != theme.APP_NAME:
                    title = out
            except Exception:
                pass

        if title:
            if len(title) > 34:
                title = title[:31] + "…"
            self.text_lbl.setText(f"♪  {title}")
            self.icon_lbl.setPixmap(theme.draw_vector_icon("music", theme.T["OK"], 13))
        else:
            self.text_lbl.setText(f"None Code Studio  ·  {theme.VERSION}")
            self.icon_lbl.setPixmap(theme.draw_vector_icon("music", theme.T["MUTED"], 13))
        self.adjustSize()
        self.update_position()

    def update_position(self):
        if self.parent():
            p = self.parent()
            margin_right = 20
            margin_bottom = 32
            self.move(p.width() - self.width() - margin_right, p.height() - self.height() - margin_bottom)


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