# Instalação no Linux

Este documento descreve como instalar e executar o projeto Fake Data Generator em sistemas Linux (usuário e sistema), como habilitar inicialização automática e como gerar um binário com o PyInstaller.

## Pré-requisitos

Recomendado (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev build-essential \
  libxcb-xinerama0 libxkbcommon-x11-0 libglu1-mesa rsync
```

Observações:
- Outros sabores de Linux podem usar `dnf`, `pacman` ou `zypper` — adapte os nomes dos pacotes.
- Bibliotecas do sistema são necessárias para o PyQt5 funcionar corretamente.

## Instalação por usuário (recomendada)

1. Torne o instalador executável e rode-o:

```bash
chmod +x install_linux.sh
bash install_linux.sh
```

O script fará o seguinte por padrão:
- Copiará o conteúdo do projeto para `~/.local/share/fake-data-generator`.
- Criará um virtualenv em `~/.local/share/fake-data-generator/.venv`.
- Instalrá as dependências do `requirements.txt` nesse venv.
- Criará um wrapper executável em `~/.local/bin/fake-data-generator`.
- Criará a entrada desktop em `~/.local/share/applications/fake-data-generator.desktop`.

### Local do arquivo de configuração (oculto)

Por padrão, o instalador coloca a configuração da aplicação em um local não visível diretamente ao usuário:

- No modo *user* o wrapper exporta `FAKE_DATA_GENERATOR_CONFIG_DIR` apontando para:
  `~/.local/share/fake-data-generator/.config`
- No modo *system* (instalação em `/opt`) o wrapper exporta `FAKE_DATA_GENERATOR_CONFIG_DIR` apontando para:
  `/opt/fake-data-generator/.config`

A aplicação agora respeita a variável de ambiente `FAKE_DATA_GENERATOR_CONFIG_DIR`. Isso permite que o diretório de configuração fique dentro da pasta de instalação (oculto) em vez de ficar diretamente em `~/.config` ou visível na home do usuário.

Se desejar um local diferente, você pode definir `FAKE_DATA_GENERATOR_CONFIG_DIR` manualmente antes de executar o wrapper, por exemplo:

```bash
export FAKE_DATA_GENERATOR_CONFIG_DIR="$HOME/.config/FakeDataGenerator"
fake-data-generator
```

2. Habilitar autostart (opcional):

```bash
bash install_linux.sh --autostart
```

Isso copia o `.desktop` para `~/.config/autostart` para iniciar automaticamente quando o usuário fizer login.

3. Executar a aplicação:

```bash
~/.local/bin/fake-data-generator
# ou, se ~/.local/bin estiver no PATH:
fake-data-generator
```

## Instalação system-wide (requer sudo)

```bash
sudo bash install_linux.sh --system
```

Com essa opção o projeto será copiado para `/opt/fake-data-generator`, será criado um venv em `/opt/fake-data-generator/.venv` e será criado um wrapper em `/usr/local/bin/fake-data-generator`. A entrada desktop será instalada em `/usr/share/applications/`.

## Gerar binário (PyInstaller)

Se quiser distribuir/rodar sem Python instalado, gere um binário na mesma plataforma alvo:

```bash
# ative o venv (opcional) e rode
python build.py
# resultado em dist/FakeDataGenerator  (Linux) ou dist/FakeDataGenerator.exe (Windows)
```

Observações:
- Gere o binário na mesma arquitetura e distro alvo (build no Linux para Linux).
- Se ocorrerem erros, verifique mensagens (falta de bibliotecas do sistema, problemas com hooks do PyInstaller, etc.).

## Desinstalar

Para remover a instalação do usuário:

```bash
bash install_linux.sh --uninstall
```

Para remover instalação system-wide (quando instalado com `--system`):

```bash
sudo bash install_linux.sh --uninstall
```

O script tentará remover arquivos de `~/.local/share/fake-data-generator`, `~/.local/bin/fake-data-generator`, `~/.local/share/applications/fake-data-generator.desktop` e `~/.config/autostart/`.

## Permissões e atalhos globais

O projeto usa o pacote `keyboard` para atalhos globais. No Linux isso depende de **`/dev/uinput`** e de leitura em **`/dev/input/event*`** (normalmente o grupo **`input`**).

### Atenção: PyPI `keyboard==0.13.5` e o erro «You must be root»

A última versão publicada no PyPI (`0.13.5`) contém uma função `ensure_root()` que **falha sempre** se você não for root, **mesmo** com `/dev/uinput` e udev corretos. Por isso este repositório instala o `keyboard` a partir de um **snapshot do GitHub** (ver `source/requirements.txt`).

Depois de puxar alterações do repositório, reinstale dependências na sua venv:

```bash
pip uninstall -y keyboard
pip install -r source/requirements.txt
```

### Erro «Failed to run dumpkeys» (mesmo com grupo `tty`)

A biblioteca `keyboard` executa `dumpkeys --keys-only` para obter nomes de teclas. Isso usa o **mapa da consola virtual do kernel**, não o teclado do **Wayland**.

1. **Instale o pacote** que fornece `dumpkeys` (Ubuntu/Debian):

```bash
sudo apt install -y kbd
dumpkeys --keys-only | head
```

Se este comando falhar no mesmo utilizador com que abre a app gráfica, o problema não é só «clicar em ativar» — o ambiente ainda não permite `dumpkeys`.

2. **Grupo `tty`** (continua necessário na maioria dos sistemas):

```bash
sudo usermod -aG tty "$USER"
```

**Importante:** tem de **sair da sessão por completo** (ou reiniciar). Abrir um novo terminal não actualiza os grupos do processo do ambiente gráfico. `newgrp tty` só afecta aquele shell, não a janela do Qt.

3. **Wayland (GNOME/Ubuntu por omissão):** mesmo com `tty` e `kbd`, `dumpkeys` **costuma falhar** ou ser pouco fiável. Solução prática: no **ecrã de login**, no menu (engrenagem), escolha **«Ubuntu em Xorg»** ou **«GNOME em Xorg»**, entre na sessão e volte a testar os atalhos globais.

4. Confirme `groups` na sessão onde corre o app: deve incluir **`tty`** e **`input`**.

Sem permissão adequada para `/dev/uinput`, ainda pode aparecer erro de root; aí vale a secção seguinte (udev + `input`).

### Diagnóstico rápido (opcional)

Para confirmar que o problema é permissão, teste **só uma vez** com privilégios elevados (não use no dia a dia):

```bash
sudo ~/.local/bin/fake-data-generator
# ou, a partir do código: sudo python source/main.py
```

Se os atalhos funcionarem com `sudo` mas não como usuário normal, siga os passos abaixo.

### Ubuntu / Debian: udev + grupo `input` (recomendado)

1. **Garantir o módulo `uinput`** (na maioria das instalações já existe):

```bash
sudo modprobe uinput
ls -l /dev/uinput
```

Se o arquivo não aparecer, carregue no boot:

```bash
echo uinput | sudo tee /etc/modules-load.d/uinput.conf
```

2. **Instalar a regra udev** do repositório (a partir da **raiz** do projeto clonado):

```bash
sudo install -m 644 scripts/udev/99-uinput-keyboard-hotkeys.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=misc --sysname-match=uinput
```

3. **Colocar seu usuário no grupo `input`** (padrão no Ubuntu para acesso a dispositivos de entrada):

```bash
sudo groupadd -f input
sudo usermod -aG input "$USER"
```

4. **Sair da sessão e entrar de novo** (ou reiniciar). Sem isso, o grupo novo não aparece na sessão atual.

5. **Conferir**:

```bash
groups | grep -q input && echo "OK: grupo input ativo" || echo "Ainda sem grupo input — faça logout/login"
ls -l /dev/uinput
```

Esperado: algo como `crw-rw---- 1 root input … /dev/uinput` (o grupo `input` com leitura/escrita).

6. Abra o aplicativo **sem** `sudo` e ative de novo **Ativar atalhos globais**.

### Alternativa: regra só com `uaccess` (alguns desktops)

Se a regra acima não bastar na sua distro, você pode experimentar **em lugar** da linha `KERNEL=="uinput"` do arquivo (não use as duas ao mesmo tempo sem saber o efeito):

```text
KERNEL=="uinput", SUBSYSTEM=="misc", TAG+="uaccess", OPTIONS+="static_node=uinput"
```

Recarregue o udev como no passo 2. Em muitos sistemas com **systemd-logind**, `uaccess` concede o dispositivo ao usuário da sessão local ativa.

### Segurança (leitura rápida)

Quem está no grupo `input` (ou tem acesso a `uinput`) pode, em tese, injetar eventos de teclado. Isso é o mesmo tipo de permissão que outras ferramentas de automação pedem; use apenas em máquinas nas quais você confia.

### Arquivo de regra no repositório

O conteúdo canônico está em: [`scripts/udev/99-uinput-keyboard-hotkeys.rules`](scripts/udev/99-uinput-keyboard-hotkeys.rules).

## Problemas comuns

- Erro ao importar PyQt5: instale as dependências do sistema (veja pré-requisitos).
- Erros no build do PyInstaller: verifique `build.py` e mensagens do PyInstaller; pode ser necessário adicionar hooks ou incluir dados adicionais.
- Atalhos não funcionam: veja seção acima sobre permissões e teste com privilégios para diagnosticar.
- Erro «Failed to run dumpkeys»: veja a subsecção **«Failed to run dumpkeys»** (kbd, grupo tty com logout completo, sessão Xorg em vez de Wayland).

## Suporte

Se precisar que eu: executar o instalador em modo usuário no ambiente atual para validar, ou gerar/ajustar um `README.md` com instruções mais curtas, diga qual prefere.

*** Fim ***

## AppImage (distribuível único)

Este repositório inclui um script `build_appimage.sh` que automatiza a criação de um AppImage com **PyInstaller** (a partir de `source/main.py`, como no `build.py`) e **`appimagetool`**.

Passos rápidos:

```bash
# venv com dependências (inclui pyinstaller), na raiz do repositório
python3 -m venv .venv && source .venv/bin/activate
pip install -r source/requirements.txt

chmod +x build_appimage.sh
./build_appimage.sh
```

O que o script faz:
- Roda `python -m PyInstaller` em `source/` (onefile, `--windowed`, `--add-data=src:src`, `assets:assets`, `--icon` com `assets/app-icon.ico` se existir)
- Monta `build/appimage/FakeDataGenerator.AppDir` (temporário; apagado no próximo build) com `usr/bin/`, `AppRun`, `.desktop` na raiz e **cópia** de `source/assets/app-icon.png` renomeada para `FakeDataGenerator.png` (exigência do `Icon=` + appimagetool)
- Baixa `appimagetool` em `tools/` (se ainda não existir) e gera `FakeDataGenerator-x86_64.AppImage` na raiz

Ao final um arquivo `FakeDataGenerator-x86_64.AppImage` será gerado na raiz do projeto.

Notas:
- O ícone do AppImage vem de `source/assets/app-icon.png` (copiado para a raiz do AppDir como `FakeDataGenerator.png`). O PyInstaller usa `source/assets/app-icon.ico` como `--icon`, se existir.
- Para distribuir, basta tornar o AppImage executável e compartilhar:

```bash
chmod +x FakeDataGenerator-x86_64.AppImage
./FakeDataGenerator-x86_64.AppImage
```

