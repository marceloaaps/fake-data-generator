"""
Serviço de atalhos globais - Implementa IShortcutService.
Adaptação do código original shortcut_manager.py
"""
import sys

from .linux_dumpkeys import apply_dumpkeys_workaround

apply_dumpkeys_workaround()

import keyboard
from typing import Dict, Callable, Optional, List, Tuple
from ...domain.interfaces.repositories import IShortcutService, ILogger


class LinuxGlobalHotkeyPermissionError(RuntimeError):
    """Falta permissão no Linux para a biblioteca `keyboard` registrar hooks globais."""


class LinuxGlobalHotkeyDumpkeysError(RuntimeError):
    """Linux: o utilitário dumpkeys (mapa da consola) falhou — comum em Wayland ou sem pacote kbd."""


def _looks_like_keyboard_root_error(exc: BaseException) -> bool:
    if not sys.platform.startswith("linux"):
        return False
    t = str(exc).lower()
    return "must be root" in t or ("root" in t and "library" in t and "linux" in t)


_LINUX_HOTKEY_HELP = (
    "No Linux, os atalhos globais precisam ler /dev/input e /dev/uinput (grupo input, regras uinput — "
    "veja INSTALL_LINUX.md).\n\n"
    "Se você já configurou udev e o grupo input e AINDA vê «must be root»: a versão antiga do pacote "
    "«keyboard» no PyPI (0.13.5) ignora isso e exige root. Reinstale as dependências do projeto "
    "(pip install -r source/requirements.txt) para obter o keyboard instalado a partir do GitHub upstream.\n\n"
    "• Teste rápido: rodar o app com sudo (só para isolar causa).\n"
    "• Sem atalhos globais: use os botões Email, CPF e CEP na janela do app."
)

_DUMPKEYS_HELP = (
    "A biblioteca «keyboard» usa o comando «dumpkeys» (pacote kbd) para mapear nomes de teclas.\n\n"
    "O que verificar:\n"
    "• Pacote: sudo apt install kbd\n"
    "• Grupo tty: sudo usermod -aG tty \"$USER\" — encerre a sessão por completo após adicionar.\n"
    "• Grupo input + udev uinput (veja INSTALL_LINUX.md).\n"
    "• Teste com a VT da sessão: dumpkeys --keys-only </dev/tty2 | head "
    "(substitua tty2 pelo TTY de loginctl show-session \"$XDG_SESSION_ID\" -p TTY).\n"
    "• «dumpkeys | head» sem redirecionamento falha em muitos terminais Wayland sem TTY — "
    "isso não significa que os atalhos do app não funcionem.\n\n"
    "Se nada disto resolver, use os botões da janela sem atalhos globais."
)


def _looks_like_dumpkeys_error(exc: BaseException) -> bool:
    if not sys.platform.startswith("linux"):
        return False
    t = str(exc).lower()
    return "dumpkeys" in t


class GlobalKeyboardShortcutService(IShortcutService):
    """Gerencia atalhos globais de teclado com suporte a threading."""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
        self.registered_hotkeys: Dict[str, str] = {}
        self.hotkey_callbacks: List[Tuple[str, Callable]] = []
        self.monitoring = False
        # listener thread removed; keyboard module handles hooks
    
    def register(self, hotkey: str, callback: Callable) -> None:
        """Registra um atalho global."""
        try:
            normalized = hotkey.lower().strip().replace(' ', '')

            # Normalize plus signs consistently
            normalized = normalized.replace('+', '+')

            # Debug log before registration
            self.logger.debug(f"Registering hotkey request: raw='{hotkey}', normalized='{normalized}'")

            # Add the hotkey. Do not suppress by default to avoid swallowing events
            # that might interfere with subsequent hotkeys; this also helps debugging.
            keyboard.add_hotkey(normalized, callback, suppress=False)
            self.registered_hotkeys[hotkey] = normalized
            self.hotkey_callbacks.append((normalized, callback))
            self.monitoring = True

            self.logger.debug(f"✓ Atalho registrado: {hotkey} -> {normalized}")
        except Exception as e:
            self.logger.error(f"✗ Erro ao registrar atalho {hotkey}: {str(e)}")
            if _looks_like_keyboard_root_error(e):
                raise LinuxGlobalHotkeyPermissionError(_LINUX_HOTKEY_HELP) from e
            if _looks_like_dumpkeys_error(e):
                raise LinuxGlobalHotkeyDumpkeysError(_DUMPKEYS_HELP) from e
            raise
    
    def unregister_all(self) -> None:
        """Remove todos os atalhos registrados."""
        try:
            self.logger.debug(f"Unregistering all hotkeys: {self.registered_hotkeys}")

            # Compatibilidade: algumas versões do pacote `keyboard` falham no
            # clear_all_hotkeys() por atributos internos ausentes (ex.: blocking_hotkeys).
            # Primeiro removemos de forma explícita os atalhos que registramos.
            for normalized, _callback in list(self.hotkey_callbacks):
                try:
                    keyboard.remove_hotkey(normalized)
                except Exception:
                    pass

            # Tenta limpar atalhos remanescentes sem quebrar o fluxo.
            try:
                keyboard.clear_all_hotkeys()
            except Exception as clear_err:
                self.logger.debug(f"clear_all_hotkeys() ignorado por compatibilidade: {clear_err}")

            self.registered_hotkeys.clear()
            self.hotkey_callbacks.clear()
            self.monitoring = False
            self.logger.debug("✓ Todos os atalhos removidos")
        except Exception as e:
            self.logger.error(f"✗ Erro ao remover atalhos: {str(e)}")
    
    def is_monitoring(self) -> bool:
        """Verifica se está monitorando atalhos."""
        return self.monitoring
