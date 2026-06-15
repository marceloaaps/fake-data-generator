"""
Script para construir o executável (.exe) usando PyInstaller
Uso: python build.py
"""
import subprocess
import sys
import os
from pathlib import Path


def _same_interpreter(a: Path, b: Path) -> bool:
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.realpath(a) == os.path.realpath(b)


def _ensure_pyinstaller_importable() -> None:
    """Garante PyInstaller importável; re-exec com o Python do venv se VIRTUAL_ENV estiver ativo mas outro binário estiver no comando."""
    try:
        import PyInstaller  # noqa: F401
        return
    except ImportError:
        pass

    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        here = Path(__file__).resolve()
        this_exe = Path(sys.executable).resolve()
        for name in ("python3", "python"):
            candidate = (Path(venv) / "bin" / name).resolve()
            if not candidate.is_file():
                continue
            if _same_interpreter(candidate, this_exe):
                continue
            os.execv(str(candidate), [str(candidate), str(here), *sys.argv[1:]])

    print("❌ PyInstaller não está disponível neste interpretador.")
    print(f"   sys.executable = {sys.executable}")
    if venv:
        print("   Com venv ativo, use: .venv/bin/python build.py (ou python3 build.py)")
    else:
        print("   Execute: pip install pyinstaller (no mesmo Python que roda este script)")
    sys.exit(1)


def build_exe():
    """Constrói o executável para Windows"""
    
    print("🔨 Iniciando build do executável...")
    
    # Caminho do projeto
    project_dir = Path(__file__).parent
    assets_dir = project_dir / "assets"
    icon_path = assets_dir / "app-icon.ico"
    
    # Comando PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",           # Cria um arquivo único
        "--windowed",          # Sem console
        "--name=FakeDataGenerator",
        f"--add-data=src{os.pathsep}src",  # Inclui pasta src (usa separador correto por SO)
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
        str(project_dir / "main.py")
    ]

    if assets_dir.exists():
        cmd.insert(-1, f"--add-data=assets{os.pathsep}assets")
        if icon_path.exists():
            cmd.insert(-1, f"--icon={str(icon_path.resolve())}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=project_dir)
        print("✅ Build concluído com sucesso!")
        exe_name = "FakeDataGenerator.exe" if os.name == "nt" else "FakeDataGenerator"
        print(f"\nExecutável criado em: {project_dir / 'dist' / exe_name}")
        print("\nPróximos passos:")
        print("1. Teste o executável")
        print("2. Configure sua chave de API na primeira execução")
        print("3. Distribua conforme necessário")
        # On Windows, create a small .cmd wrapper that sets a config dir in %APPDATA%
        try:
            dist_dir = project_dir / 'dist'
            exe_path = dist_dir / 'FakeDataGenerator.exe'
            wrapper_path = dist_dir / 'FakeDataGenerator.cmd'
            if os.name == 'nt' and exe_path.exists():
                with open(wrapper_path, 'w', newline='\r\n') as w:
                    w.write('@echo off\r\n')
                    w.write('set "FAKE_DATA_GENERATOR_CONFIG_DIR=%APPDATA%\\FakeDataGenerator"\r\n')
                    w.write('"%~dp0\\FakeDataGenerator.exe" %*\r\n')
                print(f"Criado wrapper Windows em: {wrapper_path}")
        except Exception:
            pass
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar build: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    _ensure_pyinstaller_importable()
    build_exe()
