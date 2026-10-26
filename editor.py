import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QFrame
from PyQt6.Qsci import (
    QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJava,
    QsciLexerJavaScript, QsciLexerHTML, QsciLexerCSS, QsciLexerSQL,
    QsciLexerJSON, QsciLexerMarkdown, QsciLexerBash, QsciLexerBatch
)
import app_theme as theme


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
        T = theme.T
        default_fg = QColor(T["TEXT"])
        default_bg = QColor(T["EDITOR"])
        base_font = QFont("Consolas", 11)

        lexer.setDefaultPaper(default_bg)
        lexer.setDefaultColor(default_fg)
        lexer.setFont(base_font)

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
                    self._apply_base_lexer_style(lexer)

                    if ext in (".bat", ".cmd"):
                        batch_style_ids = {
                            0: T["TEXT"], 1: T["MUTED"], 2: T["WARN"],
                            3: T["OK"], 4: T["ACCENT"], 5: T["PRIMARY"],
                            6: "#f472b6", 7: T["MUTED"]
                        }
                        for s, col in batch_style_ids.items():
                            lexer.setColor(QColor(col), s)

                    elif ext in (".css", ".scss", ".less"):
                        css_styles = {
                            0: T["TEXT"],
                            1: T["ACCENT"],
                            2: "#60a5fa",
                            3: "#c084fc",
                            4: "#f472b6",
                            5: "#93c5fd",
                            6: "#94a3b8",
                            7: "#93c5fd",
                            8: T["OK"],
                            9: T["MUTED"],
                            10: "#c084fc",
                            11: T["WARN"],
                            12: "#38bdf8",
                            13: "#fb923c",
                            14: "#fb923c",
                            15: "#60a5fa",
                            16: "#60a5fa",
                            17: "#60a5fa",
                            18: "#f472b6",
                            19: "#38bdf8",
                            20: "#38bdf8",
                            21: "#38bdf8",
                            22: "#38bdf8",
                            23: "#94a3b8",
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