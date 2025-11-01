"""Helpers to install Ollama into a `bin` folder.

Provides:
- install_ollama(download_url, bin_dir="bin", timeout=60): download and extract an asset
- ensure_ollama_installed(download_url, bin_dir="bin", timeout=60): check bin_dir; if empty, install

This implementation uses only the Python standard library so it works on a plain Python
installation on Windows. It supports .zip and .tar.gz (tgz) assets and single-file executables.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
import zipfile
import tarfile
from typing import List, Optional


def _is_dir_nonempty(path: Path) -> bool:
    """Return True if path exists and contains at least one file or directory.
    Treat missing directory as empty.
    """
    try:
        if not path.exists():
            return False
        # any() short-circuits on first found entry
        return any(path.iterdir())
    except Exception:
        return False


def install_ollama(download_url: str, bin_dir: str = "bin", timeout: int = 60) -> List[str]:
    """Download `download_url`, extract/move relevant files into `bin_dir` and return list of installed paths.

    - download_url: direct URL to .zip, .tar.gz (.tgz) or single executable file.
    - bin_dir: destination folder (created if needed).
    - timeout: network timeout in seconds.

    Raises ValueError if download_url is empty, RuntimeError on install failures.
    """
    if not download_url:
        raise ValueError("download_url is required")

    bin_path = Path(bin_dir)
    bin_path.mkdir(parents=True, exist_ok=True)

    tmp_dir = Path(tempfile.mkdtemp(prefix="install_ollama_"))
    tmp_file = tmp_dir / "asset"

    try:
        # Download
        print(f"Downloading {download_url} ...")
        with urllib.request.urlopen(download_url, timeout=timeout) as resp:
            with open(tmp_file, "wb") as out:
                shutil.copyfileobj(resp, out)

        name = download_url.lower()
        extracted_files: List[Path] = []

        # Extract or treat as single file
        if name.endswith(".zip"):
            print("Detected zip archive, extracting...")
            with zipfile.ZipFile(tmp_file, "r") as zf:
                zf.extractall(tmp_dir)
            extracted_files = [p for p in tmp_dir.rglob("*") if p.is_file()]

        elif name.endswith(".tar.gz") or name.endswith(".tgz"):
            print("Detected tar.gz archive, extracting...")
            with tarfile.open(tmp_file, "r:gz") as tf:
                tf.extractall(tmp_dir)
            extracted_files = [p for p in tmp_dir.rglob("*") if p.is_file()]

        else:
            # single file
            print("Downloaded single file; moving to bin directory...")
            target = bin_path / Path(download_url).name
            shutil.move(str(tmp_file), str(target))
            # make executable on Unix
            if os.name != "nt":
                try:
                    st = os.stat(str(target))
                    os.chmod(str(target), st.st_mode | 0o111)
                except Exception:
                    pass
            return [str(target)]

        # Heuristics to pick files to move to bin_dir:
        # - any file whose name contains 'ollama'
        # - any file in a top-level 'bin' directory inside the archive
        # - any obvious executable (.exe on Windows, executable bit on Unix)
        moved: List[str] = []

        for p in extracted_files:
            name_lower = p.name.lower()
            parent_name = p.parent.name.lower()

            pick = False
            # obvious matches
            if "ollama" in name_lower or parent_name == "bin":
                pick = True

            # windows executable
            if not pick and os.name == "nt" and p.suffix.lower() == ".exe":
                pick = True

            # unix executable bit
            if not pick and os.name != "nt" and os.access(p, os.X_OK):
                pick = True

            # fallback: files at top-level (small depth)
            if not pick:
                try:
                    rel = p.relative_to(tmp_dir)
                    if len(rel.parts) <= 2:
                        pick = True
                except Exception:
                    pass

            if pick:
                dest = bin_path / p.name
                # ensure parent exists (bin root always exists)
                try:
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(p), str(dest))
                except Exception:
                    # try copy as fallback
                    try:
                        shutil.copy2(str(p), str(dest))
                    except Exception:
                        continue
                moved.append(str(dest))

        # Ensure executable bits on unix
        if os.name != "nt":
            for m in moved:
                try:
                    st = os.stat(m)
                    os.chmod(m, st.st_mode | 0o111)
                except Exception:
                    pass

        if not moved:
            raise RuntimeError("No files were selected to install from the archive; check the archive structure.")

        print("Installed files:")
        for mm in moved:
            print(" -", mm)
        return moved

    finally:
        # cleanup temporary dir (if any files remain moved, they won't be removed)
        try:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
        except Exception:
            pass


def ensure_ollama_installed(download_url: Optional[str], bin_dir: str = "bin", timeout: int = 60) -> List[str]:
    """Ensure `bin_dir` contains installation files for Ollama. If the folder is empty, download+install.

    - download_url: if None, the function will check environment variable OLLAMA_DOWNLOAD_URL and use it.
      If still None, raises ValueError.
    - Returns list of installed paths (possibly empty if already present).
    """
    bin_path = Path(bin_dir)
    # treat non-existing as empty
    nonempty = _is_dir_nonempty(bin_path)

    if nonempty:
        print(f"Bin directory '{bin_dir}' already contains files; skipping installation.")
        return [str(p) for p in bin_path.iterdir()]

    # empty -> proceed to install
    url = download_url or os.environ.get("OLLAMA_DOWNLOAD_URL")
    if not url:
        raise ValueError("No download_url provided and OLLAMA_DOWNLOAD_URL not set; cannot install.")

    print(f"Bin directory '{bin_dir}' is empty; installing Ollama from: {url}")
    installed = install_ollama(url, bin_dir=bin_dir, timeout=timeout)
    return installed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Install Ollama into a bin folder if it's empty.")
    parser.add_argument("--url", help="Direct download URL for the Ollama asset", default=None)
    parser.add_argument("--bin", help="Destination bin directory", default="bin")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    try:
        paths = ensure_ollama_installed(args.url, bin_dir=args.bin, timeout=args.timeout)
        if paths:
            print("Done. Installed:")
            for p in paths:
                print("  -", p)
        else:
            print("Done. No changes made.")
    except Exception as e:
        print("Installation failed:", e)
        raise
