#!/usr/bin/env python3
"""Lost Light — Installer e gestore della traduzione italiana.

GUI Tkinter identica nella struttura a quella di AION 2.
Installazione atomica e reversibile dei file di localizzazione (.bindict).
Include journal di ripristino per garantire il ritorno allo stato originale.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path

# Configurazione del gioco
APP_ID = "1797880"
DEFAULT_STEAM_BUILD = "25184116"
GAME_EXES = ["launcher.exe", "LostLight.exe", "Game_x64r.exe"]
PACKAGE_BASE = Path("Package/lazy_code/Encrypt_Python")
TARGET_LANG = "English"

# ANSI Color codes per modalità CLI
CLR_GOLD = "\033[93m"
CLR_ORANGE = "\033[38;5;208m"
CLR_GREEN = "\033[92m"
CLR_RED = "\033[91m"
CLR_CYAN = "\033[96m"
CLR_DIM = "\033[90m"
CLR_BOLD = "\033[1m"
CLR_RESET = "\033[0m"

ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def strip_ansi(text: str) -> str:
    """Rimuove sequenze di escape ANSI per una visualizzazione pulita in GUI."""
    return ANSI_ESCAPE_RE.sub("", text)

# Dizionario dei 18 file di localizzazione originali di Lost Light
KNOWN_TABLES: dict[str, dict[str, str]] = {
    "19b5e65a15e078d73a918d753b43e0ea": {
        "file": "gclient/data_bin/translate_banshu_data_bin.py",
        "sha256": "19BD18CFD567730B6DB859FF4CB892B158EB75F3AF61563277B564396D5DBF5E",
    },
    "1c56a716b5e21c00b244f9c256960de4": {
        "file": "gclient/data_bin/translate_th_data_bin.py",
        "sha256": "1C0AC8DE27F610D0E498824B9DBCE7CB3C3C7DB493E74D756D196A6D7D8B0513",
    },
    "241472366f91e8d3248725bf75e72105": {
        "file": "gclient/data_bin/translate_th_data_optbin.py",
        "sha256": "B1D4B7127D985EAC7F529A4E78D3E1D98CDF099FDDD85CEFAF96297721AF0748",
    },
    "281e76819216d479e7da64b86853fb76": {
        "file": "gclient/data_bin/translate_ru_data_bin.py",
        "sha256": "B1F0EB2F5CF4D818C6F1DE53BA8EDA20374479F50C8797C497DC99B8FD7A251E",
    },
    "2c4760d78c6e5ac81887ec2c4b964697": {
        "file": "gclient/data_bin/translate_de_data_bin.py",
        "sha256": "DA89A58AAFBE46054581DBD8C93A84FB01798588330F8D1A886CAFA818922E50",
    },
    "3138d73e735e602c35e711d28a40a10e": {
        "file": "gclient/data_bin/translate_en_data_bin.py",
        "sha256": "1FA598D0156CAB3F81263B305068995F9907583AF94B7B243C3244D3B823890C",
    },
    "42a6ac36024b0989b17e2166990e20b9": {
        "file": "gclient/data_bin/translate_en_data_optbin.py",
        "sha256": "81C40D2ADA844FB4A8F842DBD074E404F530F03A14EAF7BCC058A6217C119FCF",
    },
    "4e7f5238e8e04d306bb9c55ac151aa30": {
        "file": "gclient/data_bin/translate_pt-BR_data_bin.py",
        "sha256": "1D67CF26F393F3C334896AF3586BADCA2E84BDE80A1B5F478C417752A623A048",
    },
    "51ea24ac7ed9dd23d0f47d86b0789b9c": {
        "file": "gclient/data_bin/translate_ru_data_optbin.py",
        "sha256": "D14C3C7855365245C56E615E977730E6C81CD668CB84CFEAF96A38412B2E5CB5",
    },
    "9105f4caa300685d20ce9523ce590599": {
        "file": "gclient/data_bin/translate_ja_data_optbin.py",
        "sha256": "C717BC5426BA2F3925944304A58BDEDEDC57E58A9A9A0CACCCFBA92137E944B2",
    },
    "a3efe8c3651c0e0c61622763a73643c9": {
        "file": "gclient/data_bin/translate_es_data_bin.py",
        "sha256": "F55C2D64721BC4645208E06525436602D8E10A653019422EB2832E2E08110A73",
    },
    "c3eb30d14de6e37f6af1d831915d79fb": {
        "file": "gclient/data_bin/translate_kr_data_bin.py",
        "sha256": "45991DB140DBB8AA262D74B7B07D83B7CCDC84B3214F926827770E075D81C648",
    },
    "cf5e457356b1a1fcabc0f7321454cf33": {
        "file": "gclient/data_bin/translate_de_data_optbin.py",
        "sha256": "C0FF64B932ED861642D3F67F8CA02092C0D98342E55C394D896B30DEB1A2F452",
    },
    "d1f956858e625acf4e8ef250d2cf7e0f": {
        "file": "gclient/data_bin/translate_pt-BR_data_optbin.py",
        "sha256": "ED7BA641E673DB28B9EBD4C612E5E6941FFE34A19E99DE5387222E8D2425C519",
    },
    "d795cd146cc6df2f103b5680eb7b3c3c": {
        "file": "gclient/data_bin/translate_ja_data_bin.py",
        "sha256": "5D1C1E2B095A43D287B2E4E4B56D46793432C3A50E2835A731BDBD4272AB7FA5",
    },
    "e5cefe1c0610024a51ce4999f054d957": {
        "file": "gclient/data_bin/translate_es_data_optbin.py",
        "sha256": "BBF55126A9887D08CE4AE76C4FA87B7B522F219DF1B4C89291A937169C418AC8",
    },
    "e7e9f6ff27dcf55367421a65e44e72dd": {
        "file": "gclient/data_bin/translate_banshu_data_optbin.py",
        "sha256": "7E84FDED2279208E6910CBA423815C92DE0568BC90217351A184027950651B37",
    },
    "faf43559ea9ac97e46f712460a36aca4": {
        "file": "gclient/data_bin/translate_kr_data_optbin.py",
        "sha256": "B51C48C195F8B974EC57B02AA4543BB749209F3495FCF85CC36608D32638CABA",
    },
}

SHA256_RE = re.compile(r"[0-9A-Fa-f]{64}\Z")


class InstallError(Exception):
    pass


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest().upper()


def get_table_relative_path(file_hash: str, root: Path | None = None) -> Path:
    """Restituisce il percorso relativo del file nel gioco: Package/lazy_code/Encrypt_Python/<prefix>/<hash>"""
    prefix = file_hash[:2]
    cand = PACKAGE_BASE / prefix / file_hash
    if root is not None:
        if (root / cand).is_file():
            return cand
        alt = Path("lazy_code/Encrypt_Python") / prefix / file_hash
        if (root / alt).is_file():
            return alt
    return cand


def steam_libraries() -> list[Path]:
    if os.name != "nt":
        return []
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam = Path(winreg.QueryValueEx(key, "SteamPath")[0])
    except (OSError, FileNotFoundError):
        return []
    libraries = [steam]
    vdf = steam / "steamapps" / "libraryfolders.vdf"
    if vdf.is_file():
        source = vdf.read_text(encoding="utf-8-sig", errors="replace")
        for match in re.finditer(r'"path"\s+"([^"]+)"', source):
            libraries.append(Path(match.group(1).replace("\\\\", "\\")))
    return list(dict.fromkeys(libraries))


def find_game(explicit: Path | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    else:
        candidates.append(Path.cwd())
        for library in steam_libraries():
            candidates.append(library / "steamapps" / "common" / "Lost Light")
        candidates.extend([
            Path(r"C:\Program Files (x86)\Steam\steamapps\common\Lost Light"),
            Path(r"D:\SteamLibrary\steamapps\common\Lost Light"),
            Path(r"E:\SteamLibrary\steamapps\common\Lost Light"),
            Path(r"C:\Games\LostLight"),
            Path(r"D:\Games\LostLight"),
            Path(r"C:\Lost Light"),
            Path(r"D:\Lost Light"),
        ])

    for candidate in candidates:
        if candidate and candidate.is_dir():
            root = candidate.resolve()
            pkg = root / PACKAGE_BASE
            has_exe = any((root / exe).is_file() for exe in [
                "launcher.exe",
                "LostLight.exe",
                "Engine/Binaries/Win64/Game_x64r.exe",
            ])
            if pkg.is_dir() or has_exe:
                return root

    raise InstallError(
        "Cartella di Lost Light non trovata automaticamente.\n"
        "Seleziona manualmente la cartella del gioco con il pulsante 'Cartella Lost Light' o con --game-dir."
    )


def steam_build(root: Path) -> str:
    manifest = root.parent.parent / f"appmanifest_{APP_ID}.acf"
    if not manifest.is_file():
        return f"Hot Patch 570 (build {DEFAULT_STEAM_BUILD})"
    try:
        content = manifest.read_text(encoding="utf-8-sig", errors="replace")
        build = re.search(r'"buildid"\s+"(\d+)"', content)
        if build:
            return f"build {build.group(1)}"
    except Exception:
        pass
    return f"build {DEFAULT_STEAM_BUILD}"


def game_running() -> bool:
    if os.name != "nt":
        return False
    targets = {"game_x64r.exe", "lostlight.exe", "launcher.exe"}
    try:
        output = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=10,
        ).decode("mbcs", errors="replace")
        for row in csv.reader(output.splitlines()):
            if row and row[0].strip().casefold() in targets:
                return True
    except (OSError, subprocess.SubprocessError) as error:
        raise InstallError("Impossibile verificare se Lost Light è aperto. Riprova il controllo prima di installare o ripristinare.") from error
    return False


def require_closed() -> None:
    if game_running():
        raise InstallError("Lost Light è aperto. Chiudi il gioco e il launcher prima di continuare.")


def unsafe_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def safe_path(path: Path) -> None:
    for component in [*reversed(path.parents), path]:
        if unsafe_link(component):
            raise InstallError(f"Collegamento o reparse point non ammesso: {component}")


def state_file(root: Path, state_dir: Path | None = None) -> Path:
    base = state_dir if state_dir is not None else (
        Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "LostLightItalianTranslation"
    )
    base = base.absolute()
    identity = hashlib.sha256(str(root).casefold().encode("utf-8")).hexdigest()[:24]
    path = base / "installations" / f"{identity}.json"
    safe_path(path)
    if path.is_relative_to(root):
        raise InstallError("La cartella dei backup deve essere esterna alla cartella del gioco.")
    return path


@contextmanager
def installation_lock(state_path: Path):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_suffix(".lock")
    safe_path(lock_path)
    stream = lock_path.open("a+b")
    locked = False
    try:
        if stream.seek(0, os.SEEK_END) == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except OSError as exc:
            raise InstallError("Un'altra operazione su questa installazione è in corso.") from exc
        yield
    finally:
        if locked:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def read_state(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("not an object")
        return value
    except (OSError, ValueError) as exc:
        raise InstallError("Dati di ripristino non leggibili; operazione bloccata.") from exc


def write_state(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(path)
    temp = path.with_name(path.name + f".{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def remove_state(path: Path) -> None:
    path.unlink(missing_ok=True)


def load_payload_files(bundle: Path) -> dict[str, Path]:
    """Validate each distinct manifest destination, including hot-patch copies."""
    safe_path(bundle)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    result = {}
    for entry in manifest["files"]:
        rel = Path(entry["game_relative_path"])
        src_rel = Path(entry["payload_relative_path"])
        if rel.is_absolute() or src_rel.is_absolute() or ".." in rel.parts or ".." in src_rel.parts:
            raise InstallError("Percorso non valido nel manifest")
        texture_match = re.fullmatch(
            r"(?:Package|LocalData/Patch)/([0-9a-f]{2})/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.6",
            rel.as_posix(),
        ) if entry.get("kind") == "cocos_texture" else None
        valid_texture = bool(texture_match and texture_match[1] == texture_match[2][:2])
        if entry.get("kind") == "cocos_texture" and not valid_texture:
            raise InstallError("Destinazione texture non valida")
        if not (valid_texture or rel.as_posix().startswith("LocalData/Patch/") or rel.as_posix().startswith("Package/UIScript/")):
            raise InstallError("Destinazione fuori dalla patch del gioco")
        if entry.get("kind") == "cocos_atlas" and not (
            rel.as_posix().startswith(("Package/UIScript/", "LocalData/Patch/UIScript/"))
            and rel.suffix.lower() == ".plist"
        ):
            raise InstallError("Destinazione atlante non valida")
        src = bundle / src_rel
        safe_path(src)
        if not src.is_file() or digest(src).lower() != entry["sha256_patched"].lower():
            raise InstallError(f"Payload mancante o danneggiato: {src_rel}")
        key = hashlib.sha256(rel.as_posix().encode()).hexdigest()[:24]
        if key in result:
            raise InstallError("Destinazione duplicata")
        result[key] = src
    table_entries = [e for e in manifest["files"] if e.get("kind") not in {"cocos_layout", "cocos_atlas", "cocos_texture"}]
    if len(table_entries) != 4:
        raise InstallError("Il pacchetto deve contenere le quattro copie delle tabelle")
    return result


def payload_destinations(bundle: Path) -> dict[str, Path]:
    m = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    return {hashlib.sha256(e["game_relative_path"].encode()).hexdigest()[:24]: Path(e["game_relative_path"]) for e in m["files"]}


def installation_intact(root: Path, state: dict | None) -> bool:
    return bool(state and state.get("phase") == "installed" and bool(state.get("files")) and
        all((root / i["relative_path"]).is_file() and digest(root / i["relative_path"]) == i["patch_sha256"] for i in state["files"].values()))


def installation_file_counts(root: Path, state: dict | None) -> dict[str, int]:
    counts = dict(patched=0, original=0, changed=0, missing=0)
    for info in (state or {}).get("files", {}).values():
        path = root / info["relative_path"]
        safe_path(path)
        if not path.is_file():
            counts["missing"] += 1
            continue
        actual = digest(path)
        category = ("patched" if actual == info["patch_sha256"] else
                    "original" if actual == info["original_sha256"] else "changed")
        counts[category] += 1
    return counts


def atomic_copy(source: Path, target: Path) -> None:
    safe_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".ll-{uuid.uuid4().hex}.tmp")
    try:
        with source.open("rb") as src, temp.open("xb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
            dst.flush()
            os.fsync(dst.fileno())
        safe_path(target)
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def install(root: Path, bundle: Path, state_dir: Path | None = None) -> str:
    root = root.resolve()
    require_closed()

    payload_files = load_payload_files(bundle)
    destinations = payload_destinations(bundle)
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    accepted = {hashlib.sha256(e["game_relative_path"].encode()).hexdigest()[:24]: {e["sha256_original"].upper(), e["sha256_patched"].upper(), *[h.upper() for h in e.get("sha256_compatible", [])]} for e in manifest["files"]}
    version = root / "LocalData/Patch/pkgversion"
    if version.is_file() and version.read_text().strip() != manifest["package_version"]:
        raise InstallError("Versione hot patch non supportata: aggiorna il pacchetto di traduzione")
    if not payload_files:
        raise InstallError(
            "Nessun file di traduzione trovato nella cartella payload.\n"
            "Assicurati di aver scaricato la release completa con i file patchati."
        )

    state_path = state_file(root, state_dir)
    previous = read_state(state_path)
    expected = {k: digest(v) for k,v in payload_files.items()}
    if previous and previous.get("phase") == "installed" and (set(previous.get("files", {})) != set(expected) or any(previous["files"][k]["patch_sha256"] != v for k,v in expected.items() if k in previous.get("files", {}))):
        restore(root, state_dir, bundle)
    with installation_lock(state_path):
        existing = read_state(state_path)
        if installation_intact(root, existing):
            return (
                f"{CLR_GREEN}La traduzione italiana è già installata e attiva!{CLR_RESET}\n"
                f"Avvia Lost Light e assicurati che la lingua sia impostata su {CLR_BOLD}English{CLR_RESET}."
            )

        if existing:
            raise InstallError("Installazione precedente modificata o interrotta. Ripristina prima di reinstallare; il backup è conservato.")
        transaction = uuid.uuid4().hex
        backup_dir = state_path.parent / state_path.stem / transaction
        backup_dir.mkdir(parents=True, exist_ok=False)

        state = {
            "schema_version": 1,
            "phase": "installing",
            "game_dir": str(root),
            "transaction_id": transaction,
            "files": {},
        }

        # Backup atomico
        try:
            for file_hash, patch_file in payload_files.items():
                rel_path = destinations[file_hash]
                game_file = root / rel_path
                safe_path(game_file)

                if not game_file.is_file():
                    raise InstallError(f"File di gioco non trovato: {rel_path}")

                orig_hash = digest(game_file)
                if orig_hash not in accepted[file_hash]:
                    raise InstallError(f"File aggiornato o non compatibile: {rel_path}. Nessun file sostituito.")
                backup_file = backup_dir / f"before_{file_hash}.bin"
                with game_file.open("rb") as src, backup_file.open("xb") as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
                    dst.flush()
                    os.fsync(dst.fileno())

                state["files"][file_hash] = {
                    "relative_path": str(rel_path),
                    "original_sha256": orig_hash,
                    "patch_sha256": digest(patch_file),
                }

            # Scrivi il journal di recupero prima della sostituzione
            write_state(state_path, state)

            # Sostituzione atomica
            for file_hash, patch_file in payload_files.items():
                rel_path = destinations[file_hash]
                game_file = root / rel_path
                atomic_copy(patch_file, game_file)

            for key, info in state["files"].items():
                if digest(root / info["relative_path"]) != info["patch_sha256"]:
                    raise InstallError("Verifica dopo installazione non riuscita")

            # Aggiorna lo stato come 'installed'
            state["phase"] = "installed"
            write_state(state_path, state)

        except BaseException as exc:
            # Ripristino di emergenza da backup
            for file_hash, info in state.get("files", {}).items():
                backup_file = backup_dir / f"before_{file_hash}.bin"
                if backup_file.is_file():
                    game_file = root / info["relative_path"]
                    try:
                        atomic_copy(backup_file, game_file)
                    except Exception:
                        pass
            remove_state(state_path)
            raise InstallError(f"Installazione non riuscita, ripristino eseguito: {exc}") from exc

    return (
        f"{CLR_GREEN}Traduzione italiana installata con successo!{CLR_RESET}\n"
        f"File patchati: {len(payload_files)} file di localizzazione (tabelle, layout e atlanti).\n"
        f"Nel gioco, seleziona {CLR_BOLD}English{CLR_RESET}: verrà usata la traduzione italiana."
    )


def restore(root: Path, state_dir: Path | None = None, bundle: Path | None = None) -> str:
    root = root.resolve()
    require_closed()
    official = {}
    if bundle is not None:
        load_payload_files(bundle)
        manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
        version = root / "LocalData/Patch/pkgversion"
        if version.is_file() and version.read_text().strip() != manifest["package_version"]:
            raise InstallError("Versione hot patch non supportata: backup conservato")
        official = {Path(e["game_relative_path"]).as_posix(): e["sha256_original"].upper() for e in manifest["files"]}

    state_path = state_file(root, state_dir)
    with installation_lock(state_path):
        state = read_state(state_path)
        if state is None:
            raise InstallError("Nessuna installazione della traduzione trovata da ripristinare.")

        transaction = state.get("transaction_id", "")
        backup_dir = state_path.parent / state_path.stem / transaction
        if not backup_dir.is_dir():
            raise InstallError(f"Cartella di backup non trovata: {backup_dir}")

        already_official = set()
        for key, info in state.get("files", {}).items():
            backup = backup_dir / f"before_{key}.bin"
            if not backup.is_file() or digest(backup) != info["original_sha256"]:
                raise InstallError("Backup mancante o danneggiato: ripristino interrotto")
            target = root / info["relative_path"]
            if target.is_file() and digest(target) == official.get(Path(info["relative_path"]).as_posix()):
                already_official.add(key)
                continue
            if not target.is_file() or digest(target) not in {info["original_sha256"], info["patch_sha256"]}:
                raise InstallError("Il gioco ha aggiornato i file: backup conservato, nessun ripristino obsoleto applicato")

        state["phase"] = "restoring"
        write_state(state_path, state)

        restored_count = 0
        for file_hash, info in state.get("files", {}).items():
            if file_hash in already_official:
                continue
            backup_file = backup_dir / f"before_{file_hash}.bin"
            if not backup_file.is_file():
                raise InstallError(f"File di backup mancante per {file_hash}")

            game_file = root / info["relative_path"]
            atomic_copy(backup_file, game_file)
            restored_count += 1

        # Preserve backup history, including the older pre-install state.
        (backup_dir / "restored_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        remove_state(state_path)

    return (
        f"{CLR_GREEN}Ripristino completato con successo!{CLR_RESET}\n"
        f"Ripristinati {restored_count} file; conservati {len(already_official)} originali ufficiali già presenti. Backup conservati."
    )


def status(root: Path, bundle: Path, state_dir: Path | None = None) -> str:
    root = root.resolve()
    build_info = steam_build(root)
    state_path = state_file(root, state_dir)
    state = read_state(state_path)

    lines = [f"Lost Light Steam — {build_info}", "Slot: English — seleziona English nel gioco"]

    if state:
        phase = state.get("phase", "sconosciuto")
        if installation_intact(root, state):
            n_files = len(state.get("files", {}))
            lines.append(f"Traduzione: installata e integra ({n_files} file verificati)")
        elif phase == "installed":
            counts = installation_file_counts(root, state)
            lines.append("Traduzione: installazione alterata o sovrascritta")
            lines.append(f"File italiani: {counts['patched']}; originali ripristinati: {counts['original']}; "
                         f"altri contenuti: {counts['changed']}; mancanti: {counts['missing']}.")
            lines.append("Controllare la compatibilità prima di ripristinare o reinstallare.")
        elif phase == "installing":
            lines.append("Traduzione: installazione interrotta, recupero con restore")
        else:
            lines.append(f"Traduzione: {phase}")
    else:
        lines.append("Traduzione: nessuna installazione gestita")

    payload_files = load_payload_files(bundle) if bundle.is_dir() else {}
    if payload_files:
        lines.append(f"Pacchetto: {len(payload_files)} file pronti per l'installazione")
    else:
        lines.append("Pacchetto: vuoto o non presente")

    lines.append("Integrità verificata al momento del controllo; un download successivo può riscrivere i file.")
    lines.append("Questo controllo non prova caricamento, font o resa in gioco.")
    return "\n".join(lines)


# ---- Helper per asset grafici ----

def resource_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        base = Path(__file__).resolve().parents[1]

    for cand in [
        base / "assets" / name,
        base / name,
        base / "visual_assets" / name,
    ]:
        if cand.is_file():
            return cand
    return base / "assets" / name


# ---- GUI Tkinter identica ad AION 2 ----

def add_header(root, title: str, subtitle: str, art_name: str):
    """Costruisce l'header scuro (#101b27) con artwork, bandiera italiana e titoli."""
    import tkinter as tk

    header = tk.Frame(root, bg="#101b27")
    header.pack(fill="x")

    art_file = resource_path(art_name)
    image = None
    if art_file.is_file():
        try:
            image = tk.PhotoImage(file=str(art_file))
        except Exception:
            try:
                from PIL import Image, ImageTk
                im = Image.open(art_file)
                image = ImageTk.PhotoImage(im)
            except Exception:
                image = None

    if image is not None:
        image_label = tk.Label(header, image=image, bg="#101b27", borderwidth=0)
        image_label.image = image
        image_label.pack(side="left")
    else:
        image_label = None

    content = tk.Frame(header, bg="#101b27")
    content.pack(side="left", fill="both", expand=True, padx=20, pady=12)

    tk.Label(
        content,
        text="LOST LIGHT",
        font=("Segoe UI", 23, "bold"),
        fg="#e5f7ff",
        bg="#101b27",
    ).pack(anchor="w")

    row = tk.Frame(content, bg="#101b27")
    row.pack(anchor="w", pady=5)

    flag = tk.Canvas(row, width=30, height=18, bg="#101b27", highlightthickness=0)
    for i, color in enumerate(["#009246", "#ffffff", "#ce2b37"]):
        flag.create_rectangle(i * 10, 0, (i + 1) * 10, 18, fill=color, outline="")
    flag.pack(side="left", padx=(0, 8))

    tk.Label(
        row,
        text=title,
        font=("Segoe UI", 11, "bold"),
        fg="#92d9ed",
        bg="#101b27",
    ).pack(side="left")

    tk.Label(
        content,
        text=subtitle,
        font=("Segoe UI", 10),
        fg="#c1cddd",
        bg="#101b27",
    ).pack(anchor="w")

    tk.Label(
        root,
        text="Traduzione amatoriale · Artwork e logo © NetEase Games",
        font=("Segoe UI", 8),
        fg="#a8b9c8",
        bg="#101b27",
    ).pack(fill="x", ipady=3)

    return image_label


def gui(bundle: Path, state_dir: Path | None, game_dir: Path | None = None, smoke: bool = False) -> int:
    import tkinter as tk
    from tkinter import ttk, filedialog

    window = tk.Tk()
    window.title("Lost Light - Traduzione Italiana")
    if os.name == "nt":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sici29.LostLight.ItalianTranslation")
    try:
        window.iconbitmap(str(resource_path("lostlight-italiano.ico")))
    except tk.TclError:
        pass
    window.geometry("860x790")
    window.minsize(800, 740)
    window.configure(background="#f4f7f9")

    # Icona finestra
    icon_file = resource_path("lostlight-italiano.png")
    if icon_file.is_file():
        try:
            window._icon = tk.PhotoImage(file=str(icon_file))
            window.iconphoto(True, window._icon)
        except Exception:
            pass

    # Stile TTK (tema clam, font Segoe UI, bg #f4f7f9)
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure(".", font=("Segoe UI", 10), background="#f4f7f9", foreground="#172b40")
    style.configure("TFrame", background="#f4f7f9")
    style.configure("TLabel", background="#f4f7f9", foreground="#172b40")
    style.configure("TButton", font=("Segoe UI", 10), padding=(10, 7))
    style.configure("Accent.TButton", background="#15755b", foreground="white", font=("Segoe UI", 11, "bold"), padding=(16, 10))
    style.map("Accent.TButton", background=[("active", "#105b46")])
    style.map("TButton", background=[("active", "#dbe7ee"), ("disabled", "#e5e9ed")])

    # 1. Header con immagine artistica
    add_header(window, "Traduzione italiana", "Versione 1.0.0 · Il tuo prossimo raid, in italiano", "installer-art.png")

    if smoke:
        window.withdraw()

    selected_root: list[Path | None] = [game_dir]
    frame = ttk.Frame(window, padding=(20, 12))
    frame.pack(fill="both", expand=True)

    # 2. Info riga
    info_text = tk.StringVar(value=f"Steam · build {DEFAULT_STEAM_BUILD} · lingua del gioco: English")
    info_label = ttk.Label(frame, textvariable=info_text)
    info_label.pack(anchor="w", pady=(8, 16))

    # 3. Spinner / status durante il controllo iniziale
    location = tk.StringVar(value="Ricerca dell'installazione Steam…")
    location_label = ttk.Label(frame, textvariable=location, wraplength=665)
    location_label.pack(anchor="w")

    headline = tk.StringVar(value="Controllo della traduzione e del gioco…")
    action = tk.StringVar(value="Attendi il controllo iniziale.")

    ttk.Separator(frame).pack(fill="x", pady=12)

    # 4. Sezione "COSA FARE"
    headline_label = ttk.Label(frame, textvariable=headline, font=("Segoe UI", 12, "bold"), wraplength=665)
    headline_label.pack(anchor="w")
    ttk.Label(frame, text="COSA FARE", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 3))
    ttk.Label(frame, textvariable=action, wraplength=665).pack(anchor="w")

    # 5. Result box con nota fissa
    result = tk.Text(frame, wrap="word", height=8, font=("Segoe UI", 10), background="#f4f7f9", relief="flat")
    result.pack(fill="both", expand=True, pady=12)
    FIXED_NOTE = "La patch conserva il backup originale. Dopo l'installazione seleziona English nel gioco."
    result.insert("end", f"{FIXED_NOTE}\n")
    result.configure(state="disabled")
    result.tag_configure("success", foreground="#167345")
    result.tag_configure("error", foreground="#b42318")
    busy = [False]
    window.protocol("WM_DELETE_WINDOW", lambda: None if busy[0] else window.destroy())

    # 6. Pulsanti azione
    controls = ttk.Frame(frame)
    controls.pack(fill="x")
    buttons: list[ttk.Button] = []

    # Spinner animation controller
    spinner_active = [False]
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spinner_idx = [0]

    def spin(base_text: str):
        if spinner_active[0]:
            char = spinner_frames[spinner_idx[0] % len(spinner_frames)]
            spinner_idx[0] += 1
            location.set(f"{char} {base_text}")
            try:
                window.after(90, lambda: spin(base_text))
            except Exception:
                pass

    def start_spinner(msg: str):
        spinner_active[0] = True
        spin(msg)

    def stop_spinner():
        spinner_active[0] = False

    def run(command: str):
        busy[0] = True
        headline_label.configure(foreground="#172b40")
        for b in buttons:
            b.configure(state="disabled")

        if command == "check":
            start_spinner("Ricerca dell'installazione Steam…")
        elif command == "install":
            start_spinner("Installazione della traduzione in corso…")
        elif command == "restore":
            start_spinner("Ripristino dei file originali in corso…")

        def task():
            ok = False
            installed = False
            game_found = False
            message = ""
            loc_text = None
            build_disp = None

            try:
                root = find_game(selected_root[0])
                game_found = True
                loc_text = f"Cartella Lost Light: {root}"

                # Aggiorna spinner step
                if command == "check":
                    try:
                        window.after(0, lambda: start_spinner("Controllo della traduzione e del gioco…"))
                    except Exception:
                        pass

                b_id = steam_build(root)
                build_disp = f"Steam · {b_id} · lingua del gioco: English"

                if command == "install":
                    message = install(root, bundle, state_dir)
                elif command == "restore":
                    message = restore(root, state_dir, bundle)
                else:
                    message = status(root, bundle, state_dir)

                st = read_state(state_file(root, state_dir))
                installed = installation_intact(root, st)
                ok = True

            except InstallError as exc:
                message = str(exc)
                if not game_found:
                    loc_text = "Lost Light non trovato automaticamente."
            except Exception as exc:
                message = f"Operazione interrotta: {exc}"

            def done():
                busy[0] = False
                stop_spinner()
                if loc_text:
                    location.set(loc_text)
                if build_disp:
                    info_text.set(build_disp)

                if not game_found:
                    headline.set("Controllo da completare")
                    action.set("Lost Light non trovato. Indica la cartella del gioco con il pulsante qui sotto.")
                elif not ok:
                    headline_label.configure(foreground="#b42318")
                    headline.set("Controllo da completare")
                    action.set(f"Operazione interrotta: {strip_ansi(message)}")
                elif installed:
                    headline_label.configure(foreground="#167345")
                    headline.set("Installazione completata · File verificati" if command == "install" else "Traduzione installata · Integrità verificata")
                    action.set("File verificati adesso. Dopo un download del gioco usa Controllare per verificare eventuali riscritture.")
                    btn_install.configure(text="Aggiornare la traduzione")
                elif command == "restore" and ok:
                    headline_label.configure(foreground="#167345")
                    headline.set("Ripristino completato")
                    action.set("File ripristinati. Puoi installare nuovamente la traduzione.")
                elif st and st.get("phase") == "installed":
                    headline_label.configure(foreground="#b42318")
                    headline.set("Traduzione alterata o sovrascritta")
                    action.set("Il controllo ha rilevato file diversi dalla traduzione installata. Consulta il risultato prima di reinstallare.")
                    btn_install.configure(text="Aggiornare la traduzione")
                else:
                    headline_label.configure(foreground="#25344a")
                    headline.set("Pronto per installare")
                    action.set("Chiudi Lost Light e scegli Installare. Il backup viene creato automaticamente.")
                    btn_install.configure(text="Installare la traduzione")

                clean_msg = strip_ansi(message)
                result.configure(state="normal")
                result.delete("1.0", "end")
                result.insert("end", f"{clean_msg}\n", "success" if ok and command in ("install", "restore") else "error" if not ok else "")
                result.insert("end", f"\n{FIXED_NOTE}\n")
                result.configure(state="disabled")

                for b in buttons:
                    b.configure(state="normal")

            try:
                window.after(0, done)
            except (RuntimeError, tk.TclError):
                pass

        threading.Thread(target=task, daemon=True).start()

    def choose():
        val = filedialog.askdirectory(title="Cartella Lost Light")
        if val:
            selected_root[0] = Path(val)
            run("check")

    btn_install = ttk.Button(controls, text="Installare la traduzione", style="Accent.TButton", command=lambda: run("install"))
    btn_install.pack(side="left", padx=(0, 8))
    buttons.append(btn_install)

    btn_check = ttk.Button(controls, text="Controllare", command=lambda: run("check"))
    btn_check.pack(side="left", padx=(0, 8))
    buttons.append(btn_check)

    btn_restore = ttk.Button(controls, text="Ripristinare", command=lambda: run("restore"))
    btn_restore.pack(side="left", padx=(0, 8))
    buttons.append(btn_restore)

    # 7. Pulsante cartella separato
    btn_folder = ttk.Button(frame, text="Cartella Lost Light", command=choose)
    btn_folder.pack(anchor="w", pady=(10, 0))
    buttons.append(btn_folder)

    # 8. Footer
    ttk.Label(
        frame,
        text="Backup e ripristino automatici · Il gioco non viene avviato",
        font=("Segoe UI", 9),
    ).pack(anchor="w", pady=(12, 0))

    # Accessible interactive links, opened only on user click.
    import webbrowser
    links = ttk.Frame(frame)
    links.pack(fill="x", pady=(14, 0))
    for label, url in [("Altre traduzioni in italiano ↗", "https://sici29.github.io/gioca-in-italiano/"),
                       ("Offrimi un caffè ☕", "https://buymeacoffee.com/sici29"),
                       ("Sorgenti e assistenza ↗", "https://github.com/Sici29/Lost-Light-Italian-Translation")]:
        ttk.Button(links, text=label, command=lambda u=url: webbrowser.open(u)).pack(side="left", padx=(0, 8))
    ttk.Label(frame, text="Un progetto di Sici29 · Traduzione amatoriale", foreground="#556677").pack(anchor="w", pady=(8, 0))

    if smoke:
        def smoke_finish():
            window.destroy()
        window.after(300, smoke_finish)
    else:
        run("check")

    window.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lost Light — Installer e gestore della traduzione italiana"
    )
    parser.add_argument("command", nargs="?", choices=("check", "status", "install", "restore", "inspect"))
    parser.add_argument("--game-dir", type=Path, help="Percorso della cartella principale di Lost Light")
    parser.add_argument("--bundle-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--state-dir", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--gui-smoke", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args(argv)

    if getattr(sys, "frozen", False):
        _bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        _bundle_root = Path(__file__).resolve().parents[1]
    bundle = args.bundle_dir or _bundle_root / "payload"

    # Se nessun comando CLI è specificato, avvia la GUI
    if args.command is None:
        return gui(bundle, args.state_dir, args.game_dir, args.gui_smoke)

    # CLI fallback per esecuzione senza interfaccia
    try:
        if args.command == "inspect":
            payload_files = load_payload_files(bundle)
            print(f"Payload valido: {len(payload_files)} file pronti per l'installazione.")
            return 0

        root = find_game(args.game_dir)
        if args.command == "install":
            print(install(root, bundle, args.state_dir))
        elif args.command == "restore":
            print(restore(root, args.state_dir, bundle))
        else:
            print(status(root, bundle, args.state_dir))
        return 0
    except (InstallError, OSError) as exc:
        print(f"Operazione interrotta: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
