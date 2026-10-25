import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QFrame
from PyQt6.Qsci import (
    QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJava,
    QsciLexerJavaScript, QsciLexerHTML, QsciLexerCSS, QsciLexerSQL,
    QsciLexerJSON, QsciLexerMarkdown, QsciLexerBash, QsciLexerBatch
)
import theme


class CodeEditor(QsciScintilla):
    def __init__(self, filepath=None, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._setup_ui()
        if filepath and os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                self.setText(f.read())
        self.apply_lexer()
        self.setModified(False)

    def _setup_ui(self):
        T = theme.T
        self.setFrameShape(QFrame.Shape.NoFrame)
        font = QFont("Consolas", 11)
        self.setFont(font)
        self.setUtf8(True)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "00000")
        self.setMarginsFont(font)
        self.setMarginsForegroundColor(QColor(T["MUTED"]))
        self.setMarginsBackgroundColor(QColor(T["EDITOR"]))
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.setFoldMarginColors(QColor(T["EDITOR"]), QColor(T["EDITOR"]))
        self.setCaretForegroundColor(QColor(T["ACCENT"]))
        self.setCaretWidth(2)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(T["SURFACE"]))
        self.setSelectionBackgroundColor(QColor(T["SURFACE_HOVER"]))
        self.setSelectionForegroundColor(QColor("#ffffff"))
        self.setMatchedBraceBackgroundColor(QColor(T["BORDER_ACTIVE"]))
        self.setMatchedBraceForegroundColor(QColor(T["ACCENT"]))
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationGuidesForegroundColor(QColor(T["BORDER"]))
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(2)
        self.setPaper(QColor(T["EDITOR"]))
        self.setColor(QColor(T["TEXT"]))

    def _apply_base_lexer_style(self, lexer):
        """Ép nền đen và toàn bộ chữ sang màu sáng trắng dịu trước, chống hoàn toàn hiện tượng đen chữ."""
        T = theme.T
        default_fg = QColor(T["TEXT"])
        default_bg = QColor(T["EDITOR"])
        base_font = QFont("Consolas", 11)

        lexer.setDefaultPaper(default_bg)
        lexer.setDefaultColor(default_fg)
        lexer.setFont(base_font)

        # Quét sạch 128 style IDs của Scintilla để không một token nào bị mang màu đen mặc định
        for s in range(128):
            lexer.setPaper(default_bg, s)
            lexer.setColor(default_fg, s)
            lexer.setFont(base_font, s)

    def apply_lexer(self):
        T = theme.T
        lexer = None
        if self.filepath:
            ext = os.path.splitext(self.filepath)[1].lower()
            mapping = {
                (".py", ".pyw"): QsciLexerPython,
                (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs", ".rs", ".go"): QsciLexerCPP,
                (".java",): QsciLexerJava,
                (".js", ".ts", ".jsx", ".tsx"): QsciLexerJavaScript,
                (".html", ".htm", ".xhtml"): QsciLexerHTML,
                (".css", ".scss", ".less"): QsciLexerCSS,
                (".sql",): QsciLexerSQL,
                (".json",): QsciLexerJSON,
                (".md", ".markdown"): QsciLexerMarkdown,
                (".sh", ".bash", ".zsh"): QsciLexerBash,
                (".bat", ".cmd"): QsciLexerBatch,
            }
            for exts, cls in mapping.items():
                if ext in exts:
                    lexer = cls(self)
                    # 1. Ép toàn bộ 128 style sáng rõ trước
                    self._apply_base_lexer_style(lexer)

                    # 2. Tuỳ biến từng ngôn ngữ cụ thể
                    if ext in (".bat", ".cmd"):
                        batch_style_ids = {
                            0: T["TEXT"], 1: T["MUTED"], 2: T["WARN"],
                            3: T["OK"], 4: T["ACCENT"], 5: T["PRIMARY"],
                            6: "#f472b6", 7: T["MUTED"]
                        }
                        for s, col in batch_style_ids.items():
                            lexer.setColor(QColor(col), s)

                    elif ext in (".css", ".scss", ".less"):
                        # Fix chuẩn theo Style ID của Scintilla LexCSS (0 -> 25)
                        css_styles = {
                            0: T["TEXT"],        # Default Text
                            1: T["ACCENT"],      # Tag (div, body, html...)
                            2: "#60a5fa",        # Class (.btn, .header...)
                            3: "#c084fc",        # PseudoClass (:hover, :active...)
                            4: "#f472b6",        # Unknown PseudoClass
                            5: "#93c5fd",        # Operator ({, }, :, ;, ,)
                            6: "#94a3b8",        # Identifier
                            7: "#93c5fd",        # Unknown Property
                            8: T["OK"],          # Value (10px, bold, center...)
                            9: T["MUTED"],       # Comment (/* ... */)
                            10: "#c084fc",       # ID Selector (#app...)
                            11: T["WARN"],       # Important (!important)
                            12: "#38bdf8",       # Directive (@media, @import...)
                            13: "#fb923c",       # Double Quoted String
                            14: "#fb923c",       # Single Quoted String
                            15: "#60a5fa",       # CSS1 Property
                            16: "#60a5fa",       # CSS2 Property
                            17: "#60a5fa",       # CSS3 Property
                            18: "#f472b6",       # PseudoElement (::before, ::after)
                            19: "#38bdf8",       # Extended CSS Property
                            20: "#38bdf8",       # Extended PseudoClass
                            21: "#38bdf8",       # Extended PseudoElement
                            22: "#38bdf8",       # Media Rule
                            23: "#94a3b8",       # Variable (--primary, --border...)
                        }
                        for s, col in css_styles.items():
                            lexer.setColor(QColor(col), s)

                    elif ext in (".html", ".htm", ".xhtml"):
                        for s in range(128):
                            desc = lexer.description(s).lower()
                            if "tag" in desc:
                                lexer.setColor(QColor(T["ACCENT"]), s)
                            elif "attribute" in desc:
                                lexer.setColor(QColor("#93c5fd"), s)
                            elif "string" in desc:
                                lexer.setColor(QColor(T["OK"]), s)
                            elif "comment" in desc:
                                lexer.setColor(QColor(T["MUTED"]), s)

                    else:
                        for s in range(128):
                            name = lexer.description(s)
                            if not name:
                                continue
                            low = name.lower()
                            for key, col in theme.EDITOR_PALETTE:
                                if key in low:
                                    lexer.setColor(QColor(col), s)
                                    break
                    break

        self.setLexer(lexer)
        self.setPaper(QColor(T["EDITOR"]))
        self.setColor(QColor(T["TEXT"]))
        self.setMarginsBackgroundColor(QColor(T["EDITOR"]))
        self.setFoldMarginColors(QColor(T["EDITOR"]), QColor(T["EDITOR"]))

    def set_filepath(self, path):
        self.filepath = path
        self.apply_lexer()

    def language_name(self):
        if self.filepath:
            ext = os.path.splitext(self.filepath)[1].lower()
            names = {
                ".py": "Python", ".cpp": "C++", ".c": "C", ".h": "Header",
                ".rs": "Rust", ".go": "Go", ".js": "JavaScript", ".ts": "TypeScript",
                ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "SCSS",
                ".less": "LESS", ".json": "JSON", ".md": "Markdown",
                ".sh": "Shell", ".bat": "Batch", ".cmd": "Batch",
                ".java": "Java", ".sql": "SQL"
            }
            if ext in names:
                return names[ext]
        lx = self.lexer()
        return lx.language() if lx else "Plain Text"