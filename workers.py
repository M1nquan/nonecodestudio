import io
import os
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile
from PyQt6.QtCore import QThread, pyqtSignal

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def venv_python(venv_dir):
    if os.name == "nt":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")


def venv_root_of(python_path):
    if not python_path:
        return None
    root = os.path.dirname(os.path.dirname(os.path.abspath(python_path)))
    return root if os.path.isfile(os.path.join(root, "pyvenv.cfg")) else None


def find_venvs(workspace):
    result = []
    if not workspace or not os.path.isdir(workspace):
        return result
    try:
        for name in sorted(os.listdir(workspace)):
            path = os.path.join(workspace, name)
            if os.path.isfile(os.path.join(path, "pyvenv.cfg")):
                py = venv_python(path)
                if os.path.isfile(py):
                    result.append((name, py))
    except OSError:
        pass
    return result


def parse_github_url(text):
    t = text.strip().rstrip("/")
    if not t:
        return None
    if t.startswith("git@github.com:"):
        t = t.split(":", 1)[1]
    else:
        for prefix in ("https://", "http://"):
            if t.startswith(prefix):
                t = t[len(prefix):]
        if t.startswith("www."):
            t = t[4:]
        if t.startswith("github.com/"):
            t = t[len("github.com/"):]
    parts = [p for p in t.split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    branch = parts[3] if len(parts) >= 4 and parts[2] == "tree" else None
    return owner, repo, branch


class CloneWorker(QThread):
    log = pyqtSignal(str)
    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, owner, repo, branch, parent_dir):
        super().__init__()
        self.owner, self.repo, self.branch, self.parent_dir = owner, repo, branch, parent_dir

    def run(self):
        dest = os.path.join(self.parent_dir, self.repo)
        if os.path.exists(dest):
            self.failed.emit(f"Folder exists: {dest}")
            return

        if shutil.which("git"):
            self.log.emit("Cloning with git...")
            cmd = ["git", "clone", "--depth", "1"]
            if self.branch:
                cmd += ["--branch", self.branch]
            cmd += [f"https://github.com/{self.owner}/{self.repo}.git", dest]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, creationflags=NO_WINDOW)
                if res.returncode == 0:
                    self.succeeded.emit(dest)
                    return
            except OSError:
                pass
            if os.path.exists(dest):
                shutil.rmtree(dest, ignore_errors=True)

        branches = [self.branch] if self.branch else ["main", "master"]
        for b in branches:
            self.log.emit(f"Downloading branch {b}...")
            url = f"https://codeload.github.com/{self.owner}/{self.repo}/zip/refs/heads/{b}"
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    data = r.read()
            except (urllib.error.HTTPError, urllib.error.URLError):
                continue
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    top = zf.namelist()[0].split("/")[0]
                    zf.extractall(self.parent_dir)
                os.rename(os.path.join(self.parent_dir, top), dest)
                self.succeeded.emit(dest)
                return
            except (zipfile.BadZipFile, OSError) as e:
                self.failed.emit(f"Extract error: {e}")
                return

        self.failed.emit("Failed to download repository.")
