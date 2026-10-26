<div align="center">

# None Code Studio
### *Minimalist • Featherlight • Aerogel Glass Desktop IDE*

[![Version](https://img.shields.io/badge/Release-v0.4b-38bdf8?style=for-the-badge&logo=github)](https://github.com/M1nquan/nonecodestudio/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6%20%7C%20QScintilla-10b981?style=for-the-badge&logo=qt)](https://riverbankcomputing.com/software/qscintilla/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-6366f1?style=for-the-badge&logo=windows)](https://github.com/M1nquan/nonecodestudio/releases/latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge&logo=gnu)](LICENSE)

<br/>

**None Code Studio** is an ultra-fast, distraction-free desktop code editor designed around modern aesthetics inspired by Zed and Cursor. Powered by PyQt6 and QScintilla, it boots in milliseconds with a tiny memory footprint, native translucent Aerogel glass styling, and an integrated execution environment.

[Download Portable (.exe)](https://github.com/M1nquan/nonecodestudio/releases/latest) • [Report Bug](https://github.com/M1nquan/nonecodestudio/issues) • [Request Feature](https://github.com/M1nquan/nonecodestudio/issues)

</div>

---

## ⚡ Highlights & Key Features

* **Aerogel Glass UI:** Translucent frameless acrylic window with hardware-accelerated ambient glowing borders and fluid spring-based animations.
* **Instant HTML Live Preview:** Hit <kbd>Ctrl</kbd> + <kbd>B</kbd> or click the Globe button to instantly project and inspect HTML/CSS templates in your default browser.
* **Smart Runner Integration:** One-click asynchronous code execution (<kbd>F5</kbd>) with native support for Python, Batch, C/C++, Rust, Go, JavaScript, TypeScript, and Shell scripts.
* **Integrated Console:** Non-blocking standard output, standard error, and live interactive `stdin` pipeline without freezing the interface.
* **Python Environment Manager:** Automatic virtual environment (`.venv`) detection, creation wizard, runtime switching, and one-click `requirements.txt` installer.
* **Git Clone Wizard:** Clone remote Git repositories or fetch project archives directly into an isolated workspace directory (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>).
* **OTA Background Updater:** Automatic non-blocking release scanning via GitHub REST API with safe self-replacing batch routines.

---

## 🎨 Themes

None Code Studio includes 4 handcrafted color schemes matching syntax lexer styles:

| Theme Name | Style Baseline | Dominant Colors |
| :--- | :--- | :--- |
| **Aerogel Obsidian** | Deep Acrylic Space | `#090a0f`, `#38bdf8`, `#818cf8` |
| **Cyber Neon** | High-Contrast Synthwave | `#04050a`, `#00f0ff`, `#ff007f` |
| **Hyper Violet** | Amethyst Crystal Glow | `#07030f`, `#bd00ff`, `#00f5ff` |
| **Tokyo Night** | Cool Midnight Palette | `#1a1b26`, `#7aa2f7`, `#7dcfff` |

---

## 🚀 Quick Start

### Option 1: Standalone Portable Binary (Recommended)
Download the standalone executable directly from GitHub Releases:
* **Binary:** `nonecodestudio.exe` (~37 MB)
* **Installation:** None required. Extract and double-click to run.

### Option 2: Run from Source

#### Prerequisites
* Python 3.10 or higher
* Git (optional, for repository cloning features)

#### Installation
```bash
# Clone the repository
git clone [https://github.com/M1nquan/nonecodestudio.git](https://github.com/M1nquan/nonecodestudio.git)
cd nonecodestudio

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Launch studio
python main.py
