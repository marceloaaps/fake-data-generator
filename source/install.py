"""
Script para instalar o aplicativo localmente.
Executa a instalação de dependências e prepara o ambiente.
"""
import subprocess
import sys
from pathlib import Path
import shutil


def install_dependencies():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        sys.exit(1)


def check_system_requirements():
    """Verifica requisitos do sistema"""
    print("🔍 Verificando requisitos do sistema...")
    
    # Verifica Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ é necessário (atual: {sys.version_info.major}.{sys.version_info.minor})")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Verifica pip
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True
        )
        print("✅ pip disponível")
    except subprocess.CalledProcessError:
        print("❌ pip não encontrado")
        sys.exit(1)


def setup_project():
    """Configura o projeto"""
    print("\n⚙️  Configurando projeto...")
    
    project_dir = Path(__file__).parent
    
    # Cria pasta de config se não existir
    config_dir = project_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    print("✅ Projeto configurado!")


def main():
    """Executa o setup completo"""
    print("=" * 50)
    print("🚀 Instalação - Fake Data Generator")
    print("=" * 50)
    
    check_system_requirements()
    install_dependencies()
    setup_project()
    
    print("\n" + "=" * 50)
    print("✅ Instalação concluída com sucesso!")
    print("=" * 50)
    print("\nPróximos passos:")
    print("1. Execute: python main.py")
    print("2. Configure sua chave de API RapidAPI")
    print("3. Comece a gerar dados!")
    print("\nPara criar um executável:")
    print("   python build.py")


if __name__ == "__main__":
    main()
