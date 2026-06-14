"""
Repositório de configuração - Implementa IConfigRepository.
Adaptação do código original config_manager.py
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ...domain.interfaces.repositories import IConfigRepository


class FileConfigRepository(IConfigRepository):
    """Gerencia configurações em arquivo JSON."""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o repositório de configuração.
        
        Args:
            config_path: Caminho para a pasta de configuração
        """
        # Priority for config path:
        # 1. explicit config_path argument
        # 2. environment variable TEMPMAIL_CONFIG_DIR
        # 3. platform default (AppData on Windows, hidden folder in home on *nix)
        env_path = os.environ.get('TEMPMAIL_CONFIG_DIR')
        if config_path is not None:
            self.config_dir = Path(config_path)
        elif env_path:
            self.config_dir = Path(env_path)
        else:
            self.config_dir = (
                Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'TempMailShortcut'
                if os.name == 'nt'
                else Path.home() / '.tempmail-shortcut'
            )
        
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.txt"
        
        self.default_config = {
            "shortcuts": {
                "email": "Ctrl+Shift+E",
                "cpf": "Ctrl+Shift+C",
                "cep": "Ctrl+Shift+Z",
                "name": "Ctrl+Shift+N",
                "cnpj": "Ctrl+Shift+J",
                "phone": "Ctrl+Shift+T"
            },
            "name": {
                "base": "",
                "counter": 0,
                "random_enabled": False
            },
            "api": {
                "rapidapi_key": "",
                "rapidapi_host": "privatix-temp-mail-v1.p.rapidapi.com"
            }
        }
        # State whether global hotkeys should be enabled on startup
        # Defaults to False for safety
        if "hotkeys_enabled" not in self.default_config:
            self.default_config["hotkeys_enabled"] = False
        if "startup_with_os" not in self.default_config:
            self.default_config["startup_with_os"] = False
        
        self._config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo."""
        if not self.config_file.exists():
            self._save(self.default_config)
            return self.default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return self.default_config
                return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return self.default_config
    
    def _save(self, config: Dict[str, Any]) -> None:
        """Salva configuração no arquivo."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor (suporta chaves aninhadas com ponto)."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """Define um valor (suporta chaves aninhadas com ponto)."""
        if key == "api.rapidapi_key":
            # Mantém valor persistido consistente e evita resíduos de espaços.
            value = "" if value is None else str(value).strip()

        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save(self._config)
    
    def get_all(self) -> Dict[str, Any]:
        """Obtém todas as configurações."""
        return self._config.copy()
