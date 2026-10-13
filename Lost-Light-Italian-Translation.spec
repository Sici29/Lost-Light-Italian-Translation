# -*- mode: python ; coding: utf-8 -*-

# Payload: tutti i file bindict patchati + manifest + data + assets GUI
from pathlib import Path
import json, sys
# Include every manifest-listed resource; no hard-coded four-file-only payload.
repo_root = Path(SPECPATH)
sys.path.insert(0, str(repo_root / "tools"))
from lostlight_it_installer import load_payload_files
from build_installer import verify_corpus_binding
load_payload_files(repo_root / "payload")
manifest = json.loads((repo_root / "payload/manifest.json").read_text(encoding="utf-8"))
verify_corpus_binding(repo_root, manifest)
payload_paths = [repo_root / "payload/manifest.json"] + [repo_root / "payload" / e["payload_relative_path"] for e in manifest["files"]]
asset_paths = [p for folder in ("assets", "data") for p in (repo_root / folder).rglob("*") if p.is_file() and p.name != ".gitkeep"]
datas = [(str(p), str(p.parent.relative_to(repo_root))) for p in payload_paths + asset_paths]
binaries = []
hiddenimports = ['PIL', 'PIL.Image', 'PIL.ImageTk', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog']

a = Analysis(
    [str(repo_root / 'tools/lostlight_it_installer.py')],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas', 'openpyxl', 'lxml', 'matplotlib', 'scipy', 'numpy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Lost-Light-Italian-Translation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(repo_root / 'assets/lostlight-italiano.ico'),
)
