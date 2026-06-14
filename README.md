# Fake Data Generator

Um aplicativo em Python que gera dados temporários (Email, CPF, CEP) e os copia automaticamente para o clipboard com um simples uso de atalho ou clique. Inclui interface gráfica(PyQt5), atalhos globais e suporte multiplataforma (Win/Linux).

## 🎯 Funcionalidades

- **Email Temporário**: Gera emails temporários usando a API Temp-Mail (RapidAPI)
- **CPF Válido**: Gera CPFs com dígitos verificadores válidos
- **CEP**: Gera CEPs válidos
- **Clipboard**: Copia automaticamente os dados gerados
- **Interface Gráfica Moderna**: Design escuro inspirado no GitHub, tema PyQt5
- **Atalhos Globais**: Use atalhos de teclado (Ctrl+Shift+E, etc.) mesmo fora do aplicativo
- **Bandeja do Sistema**: Minimize para a bandeja e minimize/feche com popup confirmação
- **Configuração Oculta**: Arquivo de config salvo em local seguro (`%APPDATA%\TempMailShortcut` no Windows, `~/.local/share/` no Linux)
- **Multiplataforma**: Executável para Windows (`.exe`) e AppImage para Linux (distribuível único)
- **Autostart**: Opção para inicializar com o sistema operacional

## 📋 Requisitos

- Python 3.8+
- Conexão com a internet (para gerar emails temporários)
- Chave de API RapidAPI (para usar o serviço de emails)

## 🚀 Instalação

## Baixar .exe para FakeDataGen.exe para Windows
## Executar build_appimage.sh para gerar AppImage - Linux

## 🔧 Fazendo sua Própria Versão 

### Opção 1: Executável pré-compilado (recomendado para usuários)

#### Windows
1. Baixe `TempMailShortcut.exe` da pasta `dist/`
2. Execute o arquivo
3. Na primeira execução, configure sua chave de API RapidAPI

#### Linux
1. Baixe `TempMailShortcut-x86_64.AppImage` (gerado via `build_appimage.sh`)
2. Torne executável: `chmod +x TempMailShortcut-x86_64.AppImage`
3. Execute: `./TempMailShortcut-x86_64.AppImage`

### Opção 2: Rodar a partir do código-fonte (para desenvolvedores)

1. Clone ou baixe o projeto
```bash
git clone <seu-repositório>
cd temp-mail-shortcut
```

2. Instale as dependências (em um venv)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instale dependências
cd source
pip install -r requirements.txt
```

3. Execute
```bash
python main.py
```

4. Na primeira execução, vá em **⚙️ Configurações** e adicione sua chave de API RapidAPI

## 🔑 Obtendo a Chave de API

1. Acesse [RapidAPI](https://rapidapi.com/)
2. Crie uma conta (se não tiver)
3. Procure por "Temp-Mail" na plataforma
4. Inscreva-se no serviço (há uma versão gratuita)
5. Copie sua chave de API
6. Cole no aplicativo em **⚙️ Configurações**

## 📁 Estrutura de Pastas

```
temp-mail-shortcut/
├── source/                    # Código-fonte e scripts de build
│   ├── src/                   # Código principal (DDD architecture)
│   │   ├── application/       # Casos de uso
│   │   ├── domain/            # Entities e interfaces
│   │   ├── infrastructure/    # Implementações (API, clipboard, logger, etc.)
│   │   ├── presentation/      # Controllers
│   │   ├── gui_qt5.py         # Interface gráfica PyQt5 (principal)
│   │   ├── main.py            # Ponto de entrada
│   │   └── config_manager.py  # Gerencia configurações
│   ├── build.py               # Script para gerar .exe (Windows)
│   ├── install.py             # Instalador Python
│   ├── requirements.txt       # Dependências do projeto
│   └── TempMailShortcut.spec  # Especificação PyInstaller
├── dist/                      # Artefatos de build (ignorado no git)
│   ├── TempMailShortcut.exe   # Executável Windows
│   └── TempMailShortcut.cmd   # Wrapper Windows (define config dir)
├── build_appimage.sh          # Script para gerar AppImage (Linux)
├── INSTALL_LINUX.md           # Documentação de instalação no Linux
└── README.md                  # Este arquivo
```

## 💾 Arquivo de Configuração

O arquivo `config.json` é salvo automaticamente em um local oculto:
- **Windows**: `%APPDATA%\TempMailShortcut\config.json`
- **Linux**: `~/.local/share/temp-mail-shortcut/.config/config.json` (se instalado via script) ou conforme `TEMPMAIL_CONFIG_DIR`

Conteúdo padrão:
```json
{
  "shortcuts": {
    "email": "ctrl+shift+e",
    "cpf": "ctrl+shift+c",
    "cep": "ctrl+shift+z",
    "name": "ctrl+shift+n",
    "cnpj": "ctrl+shift+j",
    "phone": "ctrl+shift+t"
  },
  "name": {
    "base": "",
    "counter": 0,
    "random_enabled": false
  },
  "api": {
    "rapidapi_key": "sua-chave-aqui",
    "rapidapi_host": "privatix-temp-mail-v1.p.rapidapi.com"
  },
  "hotkeys_enabled": false,
  "startup_with_os": false,
  "app_version": "1.0.0"
}
```

**Variável de ambiente**: você pode definir `TEMPMAIL_CONFIG_DIR` para usar um diretório de configuração customizado:
```bash
export TEMPMAIL_CONFIG_DIR="/caminho/customizado"
python main.py
```

## �️ Criando Executáveis

### Windows (.exe)

1. Entre na pasta `source/` e instale dependências:
```bash
cd source
pip install -r requirements.txt pyinstaller
```

2. Gere o executável:
```bash
python build.py
```

Resultado: `source/dist/TempMailShortcut.exe` e wrapper `TempMailShortcut.cmd`

### Linux (AppImage)

Veja [INSTALL_LINUX.md](INSTALL_LINUX.md) para instruções completas.

Resumo rápido (requer WSL2/Linux/Docker):
```bash
# ative venv com dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r source/requirements.txt pyinstaller

# rode o script de build
chmod +x build_appimage.sh
./build_appimage.sh
```

Resultado: `TempMailShortcut-x86_64.AppImage` na raiz do projeto

## 🎮 Como Usar

### Executar o aplicativo
- **Windows**: Duplo clique em `TempMailShortcut.exe` ou `TempMailShortcut.cmd`
- **Linux**: `./TempMailShortcut-x86_64.AppImage` ou `python main.py` (modo desenvolvimento)

### Configurar API (primeira vez)
1. Clique em **⚙️ Configurações** (ícone de engrenagem no header)
2. Cole sua chave de API RapidAPI (obtida em [RapidAPI](https://rapidapi.com/))
3. Clique no botão ✅ para salvar

### Gerar dados
1. Clique em **📧 Email**, **📝 CPF** ou **📍 CEP** — o dado é copiado automaticamente
2. Ou use os atalhos globais (se ativados em Configurações):
   - `Ctrl+Shift+E` → Email temporário
   - `Ctrl+Shift+C` → CPF
   - `Ctrl+Shift+Z` → CEP

### Bandeja do Sistema
- Clique no X da janela → popup pergunta se deseja "Minimizar" ou "Fechar"
- Minimizar: janela oculta, app continua em background
- Fechar: app encerra completamente
- Duplo clique no ícone da bandeja para reabrir

### Autostart (opcional)
- Marque **Inicializar com Sistema Operacional** em Configurações

## 🔑 Atalhos Globais (Nova Feature!)

Use dados temporários **de qualquer lugar** sem cliques:

| Atalho | Função |
|--------|--------|
| `Ctrl+Shift+E` | Copia email temporário |
| `Ctrl+Shift+C` | Copia CPF |
| `Ctrl+Shift+Z` | Copia CEP |

**Exemplo**: Você está em um formulário online, pressiona `Ctrl+Shift+C` e o CPF é copiado para o clipboard!

👉 Veja [GLOBAL_SHORTCUTS_GUIDE.md](GLOBAL_SHORTCUTS_GUIDE.md) para mais detalhes

## � Instalação no Linux

Para instruções detalhadas de instalação, autostart, desinstalação e build no Linux, veja [INSTALL_LINUX.md](INSTALL_LINUX.md).

Resumo:
- **Usuário**: `bash source/install_linux.sh` → instala em `~/.local/share/temp-mail-shortcut`
- **System-wide**: `sudo bash source/install_linux.sh --system` → instala em `/opt/temp-mail-shortcut`
- **AppImage**: `./build_appimage.sh` → gera `TempMailShortcut-x86_64.AppImage`

## 🔧 Troubleshooting

### "RapidAPI key não configurada"
- Vá em **⚙️ Configurações** → Cole sua chave de API → Clique em ✅ para salvar

### "Erro ao gerar email"
- Verifique conexão com internet
- Verifique se sua chave de API é válida em [RapidAPI](https://rapidapi.com/)
- Verifique se o plano RapidAPI permite requisições

### Atalhos globais não funcionam
- **Windows**: Alguns programas (ex: games em fullscreen) capturam atalhos primeiro — tente em outros contextos
- **Linux**: Pode requerer permissões elevadas (`/dev/uinput`) — veja [INSTALL_LINUX.md](INSTALL_LINUX.md#permissões-e-atalhos-globais)

### "Não consegue copiar para clipboard"
- **Windows**: Geralmente funcionava nativamente; se falhar, verifique permissões
- **Linux**: Instale `xclip` — `sudo apt install xclip`

### App não inicia ou fecha imediatamente
- Execute pelo terminal para ver mensagens de erro:
  ```bash
  # Fonte:
  python source/main.py
  
  # AppImage:
  ./TempMailShortcut-x86_64.AppImage
  ```

## 📦 Dependências

Veja [source/requirements.txt](source/requirements.txt) para lista completa. Principais:

- **PyQt5** (5.15+): Interface gráfica moderna
- **qtawesome**: Ícones FontAwesome no Qt
- **requests** (2.31+): Requisições HTTP para API RapidAPI
- **keyboard**: Atalhos globais de teclado
- **PyInstaller** (6.1+): Empacotamento em executável (apenas para build)

### Dependências do Sistema (Linux)

Se instalar via `source/requirements.txt` no Linux, você pode precisar:
```bash
sudo apt install python3-dev libxcb-xinerama0 libxkbcommon-x11-0 libglu1-mesa build-essential xclip
```

## 📝 Licença

Este projeto está disponível para uso pessoal e comercial.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para fazer fork e submit pull requests.

## 👥 Autor

Desenvolvido com ❤️ por Marcelo Alexandre

## ⚠️ Aviso Legal

Este aplicativo gera dados fictícios para fins de teste. Não use para fins ilegais ou prejudiciais. Certifique-se de estar em conformidade com as leis e regulamentações de sua jurisdição.
