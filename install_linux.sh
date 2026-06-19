#!/usr/bin/env bash
# Instala Fake Data Generator no Linux (usuário ou system-wide).
# Uso: bash install_linux.sh [--system] [--autostart] [--uninstall] [--help]
set -euo pipefail

APP_NAME="fake-data-generator"
APP_DISPLAY_NAME="Fake Data Generator"
MAIN_REL="source/main.py"
REQ_REL="source/requirements.txt"
ICON_REL="source/assets/app-icon.png"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_REPO="$(cd "$SCRIPT_DIR" && pwd)"

MODE="user"
AUTOSTART=0
UNINSTALL=0

usage() {
  cat <<EOF
Uso: $(basename "$0") [OPÇÕES]

Instalação por usuário (padrão):
  bash $(basename "$0")

Instalação system-wide (requer root):
  sudo bash $(basename "$0") --system

Autostart no login (após instalar):
  bash $(basename "$0") --autostart

Desinstalar:
  bash $(basename "$0") --uninstall
  sudo bash $(basename "$0") --uninstall --system

Opções:
  --system      Instala em /opt/fake-data-generator (system-wide)
  --autostart   Copia .desktop para autostart do usuário
  --uninstall   Remove a instalação
  --help        Mostra esta ajuda
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --system) MODE="system"; shift ;;
    --autostart) AUTOSTART=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "Opção desconhecida: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$MODE" == "system" && "$(id -u)" -ne 0 ]]; then
  echo "Erro: instalação --system requer root (use sudo)." >&2
  exit 1
fi

if [[ "$MODE" == "user" ]]; then
  INSTALL_DIR="${FAKE_DATA_GENERATOR_INSTALL_DIR:-$HOME/.local/share/$APP_NAME}"
  WRAPPER_BIN="$HOME/.local/bin/$APP_NAME"
  DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"
  AUTOSTART_FILE="$HOME/.config/autostart/$APP_NAME.desktop"
  CONFIG_DIR="$INSTALL_DIR/.config"
else
  INSTALL_DIR="/opt/$APP_NAME"
  WRAPPER_BIN="/usr/local/bin/$APP_NAME"
  DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
  AUTOSTART_FILE=""
  CONFIG_DIR="$INSTALL_DIR/.config"
fi

log() { echo "==> $*"; }

# Pacotes Debian/Ubuntu necessários para o plugin Qt xcb (PyQt5).
QT_XCB_APT_PACKAGES=(
  libxcb-cursor0
  libxcb-icccm4
  libxcb-image0
  libxcb-keysyms1
  libxcb-render-util0
  libxcb-xinerama0
  libxkbcommon-x11-0
  libglu1-mesa
)

check_qt_system_libs() {
  local venv_python="${1:-}"
  local xcb_plugin=""

  if [[ -n "$venv_python" && -d "$(dirname "$venv_python")" ]]; then
    xcb_plugin="$(find "$(dirname "$venv_python")/../lib" -path '*/PyQt5/Qt5/plugins/platforms/libqxcb.so' 2>/dev/null | head -1 || true)"
  fi

  if [[ -z "$xcb_plugin" || ! -f "$xcb_plugin" ]]; then
    return 0
  fi

  local missing=()
  while IFS= read -r lib; do
    [[ -n "$lib" ]] && missing+=("$lib")
  done < <(ldd "$xcb_plugin" 2>/dev/null | awk '/not found/ { print $1 }' || true)

  if [[ ${#missing[@]} -eq 0 ]]; then
    return 0
  fi

  echo
  echo "Aviso: bibliotecas do sistema em falta para o Qt (plugin xcb):"
  printf '  - %s\n' "${missing[@]}"
  echo
  echo "Instale os pacotes recomendados (Debian/Ubuntu):"
  echo "  sudo apt update"
  echo "  sudo apt install -y ${QT_XCB_APT_PACKAGES[*]}"
  echo
  if [[ "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
    echo "Sessão Wayland detectada: o wrapper usará QT_QPA_PLATFORM=wayland até instalar as libs acima."
  fi
  echo
}

remove_path() {
  local path="$1"
  if [[ -e "$path" || -L "$path" ]]; then
    rm -rf "$path"
    log "Removido: $path"
  fi
}

do_uninstall() {
  log "Desinstalando ($MODE)..."
  remove_path "$WRAPPER_BIN"
  remove_path "$DESKTOP_FILE"
  if [[ -n "$AUTOSTART_FILE" ]]; then
    remove_path "$AUTOSTART_FILE"
  fi
  remove_path "$INSTALL_DIR"
  log "Desinstalação concluída."
}

write_wrapper() {
  local wrapper="$1"
  local install_dir="$2"
  local config_dir="$3"
  mkdir -p "$(dirname "$wrapper")"
  cat > "$wrapper" <<EOF
#!/usr/bin/env bash
set -euo pipefail
export FAKE_DATA_GENERATOR_CONFIG_DIR="${config_dir}"
# GNOME/Wayland: sem libxcb-* o plugin xcb falha; wayland funciona nativamente.
if [[ "\${XDG_SESSION_TYPE:-}" == "wayland" && -z "\${QT_QPA_PLATFORM:-}" ]]; then
  export QT_QPA_PLATFORM=wayland
fi
exec "${install_dir}/.venv/bin/python" "${install_dir}/${MAIN_REL}" "\$@"
EOF
  chmod +x "$wrapper"
  log "Wrapper: $wrapper"
}

write_desktop() {
  local desktop="$1"
  local exec_cmd="$2"
  local icon_path="$3"
  mkdir -p "$(dirname "$desktop")"
  cat > "$desktop" <<EOF
[Desktop Entry]
Type=Application
Name=${APP_DISPLAY_NAME}
Comment=Gerador de dados temporários (email, CPF, CEP)
Exec=${exec_cmd}
Icon=${icon_path}
Categories=Utility;
Terminal=false
StartupWMClass=FakeDataGenerator
EOF
  log "Desktop: $desktop"
}

setup_autostart() {
  if [[ "$MODE" != "user" ]]; then
    echo "Autostart só está disponível no modo usuário." >&2
    exit 1
  fi
  if [[ ! -f "$DESKTOP_FILE" ]]; then
    echo "Instalação não encontrada. Rode primeiro: bash install_linux.sh" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$AUTOSTART_FILE")"
  cp "$DESKTOP_FILE" "$AUTOSTART_FILE"
  chmod 644 "$AUTOSTART_FILE"
  log "Autostart: $AUTOSTART_FILE"
}

if [[ "$UNINSTALL" -eq 1 ]]; then
  do_uninstall
  exit 0
fi

if [[ ! -f "$SOURCE_REPO/$MAIN_REL" ]]; then
  echo "Erro: $SOURCE_REPO/$MAIN_REL não encontrado." >&2
  echo "Execute este script a partir da raiz do repositório clonado." >&2
  exit 1
fi

if [[ ! -f "$SOURCE_REPO/$REQ_REL" ]]; then
  echo "Erro: $SOURCE_REPO/$REQ_REL não encontrado." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Erro: python3 não encontrado. Instale python3 e python3-venv." >&2
  exit 1
fi

if [[ "$AUTOSTART" -eq 1 && -f "$INSTALL_DIR/$MAIN_REL" ]]; then
  setup_autostart
  exit 0
fi

log "Instalando em: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"

log "Copiando arquivos do projeto..."
rsync -a --delete \
  --exclude '.git/' \
  --exclude '.venv/' \
  --exclude '*/.venv/' \
  --exclude 'dist/' \
  --exclude 'build/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'tools/' \
  --exclude '*.AppImage' \
  --exclude '*.AppDir/' \
  --exclude 'FakeDataGenerator.exe' \
  "$SOURCE_REPO/" "$INSTALL_DIR/"

log "Criando virtualenv..."
if [[ ! -d "$INSTALL_DIR/.venv" ]]; then
  python3 -m venv "$INSTALL_DIR/.venv"
fi

log "Instalando dependências Python..."
"$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/$REQ_REL"

check_qt_system_libs "$INSTALL_DIR/.venv/bin/python"

write_wrapper "$WRAPPER_BIN" "$INSTALL_DIR" "$CONFIG_DIR"

ICON_PATH="$INSTALL_DIR/$ICON_REL"
if [[ ! -f "$ICON_PATH" ]]; then
  ICON_PATH=""
fi

write_desktop "$DESKTOP_FILE" "$WRAPPER_BIN" "$ICON_PATH"

if [[ "$AUTOSTART" -eq 1 ]]; then
  setup_autostart
fi

log "Instalação concluída."
echo
echo "Execute:"
if [[ "$MODE" == "user" ]]; then
  echo "  $WRAPPER_BIN"
  if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo
    echo "Nota: ~/.local/bin não está no PATH deste shell. Adicione ao ~/.zshrc ou ~/.bashrc:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo "  # ou use sempre o caminho completo acima"
  else
    echo "  # ou:"
    echo "  $APP_NAME"
  fi
else
  echo "  $WRAPPER_BIN"
fi
echo
echo "Configuração: $CONFIG_DIR"
