#!/usr/bin/env bash
set -euo pipefail

# Gera FakeDataGenerator-x86_64.AppImage na raiz do repositório.
# Ícones: origem única em source/assets/; dentro do AppDir só há cópias exigidas pelo formato AppImage.
#
# O AppDir (pasta .AppDir) é temporário: fica em build/appimage/ e é apagado no início de cada build.
# O ficheiro FakeDataGenerator.png na raiz do AppDir é cópia de source/assets/app-icon.png porque o
# .desktop usa Icon=FakeDataGenerator e o appimagetool espera esse nome na raiz do AppDir — não duplica
# o repositório como “segunda fonte”; o binário empacotado já inclui assets/ via PyInstaller.
#
# Pré-requisitos: venv com source/requirements.txt (inclui pyinstaller).
# Uso: ./build_appimage.sh

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$BASE_DIR/source"
ASSETS_DIR="$SOURCE_DIR/assets"
NAME="FakeDataGenerator"
APPIMG_STAGING="$BASE_DIR/build/appimage"
APPDIR="$APPIMG_STAGING/${NAME}.AppDir"
TOOLS_DIR="$BASE_DIR/tools"
APPIMAGETOOL="$TOOLS_DIR/appimagetool-x86_64.AppImage"
OUTPUT_IMG="$BASE_DIR/${NAME}-x86_64.AppImage"

if [[ ! -f "$SOURCE_DIR/main.py" ]]; then
  echo "ERROR: $SOURCE_DIR/main.py não encontrado."
  exit 1
fi
if [[ ! -f "$ASSETS_DIR/app-icon.png" ]]; then
  echo "ERROR: $ASSETS_DIR/app-icon.png não encontrado (necessário para o AppImage)."
  exit 1
fi

if [[ -x "$BASE_DIR/.venv/bin/python" ]]; then
  PYTHON="$BASE_DIR/.venv/bin/python"
elif [[ -x "$BASE_DIR/.venv/bin/python3" ]]; then
  PYTHON="$BASE_DIR/.venv/bin/python3"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "[1/6] Limpando builds anteriores..."
# AppDir antigo na raiz do repo (layouts anteriores do script)
rm -rf "$BASE_DIR/${NAME}.AppDir"
rm -rf "$APPIMG_STAGING" "$SOURCE_DIR/build" "$SOURCE_DIR/dist" "$BASE_DIR"/*.AppImage
mkdir -p "$TOOLS_DIR"

echo "[2/6] PyInstaller (onefile) em source/ ..."
cd "$SOURCE_DIR"
PYI_ARGS=(
  -m PyInstaller
  --noconfirm
  --clean
  --onefile
  --windowed
  "--name=$NAME"
  "--add-data=src:src"
  "--add-data=assets:assets"
  --distpath=dist
  --workpath=build
  --specpath=.
  main.py
)
if [[ -f assets/app-icon.ico ]]; then
  PYI_ARGS+=(--icon=assets/app-icon.ico)
fi
"$PYTHON" "${PYI_ARGS[@]}"

BIN_PATH="$SOURCE_DIR/dist/$NAME"
if [[ ! -f "$BIN_PATH" ]]; then
  echo "ERROR: binário não encontrado em $BIN_PATH"
  exit 1
fi

echo "[3/6] Montando ${NAME}.AppDir (mínimo: AppRun, .desktop, ícone em assets) ..."
mkdir -p "$APPDIR/usr/bin"
cp "$BIN_PATH" "$APPDIR/usr/bin/$NAME"
chmod +x "$APPDIR/usr/bin/$NAME"

DESKTOP_NAME="${NAME}.desktop"
DESKTOP_ROOT="$APPDIR/$DESKTOP_NAME"

cat > "$DESKTOP_ROOT" <<EOF
[Desktop Entry]
Type=Application
Name=Fake Data Generator
Comment=Gerador de dados temporários (email, CPF, CEP)
Exec=$NAME
Icon=$NAME
Categories=Utility;
Terminal=false
StartupWMClass=$NAME
EOF

# appimagetool: Icon= + ficheiro na raiz do AppDir
cp "$ASSETS_DIR/app-icon.png" "$APPDIR/${NAME}.png"
ln -sf "${NAME}.png" "$APPDIR/.DirIcon"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/FakeDataGenerator" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

echo "[4/6] Baixando appimagetool (se faltar)..."
if [[ ! -f "$APPIMAGETOOL" ]]; then
  APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
  echo "  URL: $APPIMAGETOOL_URL"
  curl -fsSL -o "$APPIMAGETOOL" "$APPIMAGETOOL_URL"
  chmod +x "$APPIMAGETOOL"
fi

echo "[5/6] Gerando AppImage (pode demorar)..."
export ARCH=x86_64
export APPIMAGE_EXTRACT_AND_RUN=1
rm -f "$OUTPUT_IMG"
"$APPIMAGETOOL" "$APPDIR" "$OUTPUT_IMG"

echo "[6/6] Concluído."
ls -lh "$OUTPUT_IMG"
