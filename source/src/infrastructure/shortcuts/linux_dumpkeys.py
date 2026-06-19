"""
Workaround Linux: dumpkeys precisa de um descritor de consola (VT).

Em sessões Wayland/GDM o processo gráfico (ou terminais sem TTY, ex. Cursor)
não tem stdin ligado a /dev/ttyN; dumpkeys falha mesmo com kbd + grupo tty.

Redirecionar stdin a partir da VT da sessão (loginctl) ou /dev/ttyN do utilizador
restaura o comportamento que existia ao correr o app a partir de um terminal normal.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def session_tty_device() -> Optional[Path]:
    """Devolve /dev/ttyN associado à sessão gráfica actual, se existir."""
    if not sys.platform.startswith("linux"):
        return None

    candidates: list[str] = []

    sid = os.environ.get("XDG_SESSION_ID")
    if sid:
        candidates.append(sid)

    user = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
    try:
        for line in subprocess.check_output(
            ["loginctl", "list-sessions", "--no-legend"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] == user and parts[0] not in candidates:
                candidates.append(parts[0])
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        pass

    for session_id in candidates:
        try:
            tty = subprocess.check_output(
                ["loginctl", "show-session", session_id, "-p", "TTY", "--value"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        except (subprocess.CalledProcessError, OSError):
            continue
        if tty.startswith("tty"):
            dev = Path("/dev") / tty
            if dev.exists():
                return dev

    uid = os.getuid()
    for i in range(1, 64):
        dev = Path(f"/dev/tty{i}")
        if not dev.exists():
            continue
        try:
            if dev.stat().st_uid == uid:
                return dev
        except OSError:
            continue

    return None


def apply_dumpkeys_workaround() -> None:
    """Faz patch em keyboard._nixkeyboard.build_tables antes do primeiro uso."""
    if not sys.platform.startswith("linux"):
        return

    import keyboard._nixkeyboard as nixkb

    if getattr(nixkb, "_fdg_dumpkeys_patched", False):
        return

    original_build_tables = nixkb.build_tables

    def build_tables_with_session_tty() -> None:
        if nixkb.to_name and nixkb.from_name:
            return

        tty_dev = session_tty_device()
        if tty_dev is None:
            original_build_tables()
            return

        real_check_output = nixkb.check_output

        def check_output(cmd, *args, **kwargs):
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "dumpkeys":
                kwargs.setdefault("universal_newlines", True)
                with open(tty_dev) as tty_in:
                    return real_check_output(cmd, *args, stdin=tty_in, **kwargs)
            return real_check_output(cmd, *args, **kwargs)

        nixkb.check_output = check_output
        try:
            original_build_tables()
        finally:
            nixkb.check_output = real_check_output

    nixkb.build_tables = build_tables_with_session_tty
    nixkb._fdg_dumpkeys_patched = True
