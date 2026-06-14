"""
Adaptadores para compatibilidade com código legado.
Permitem que o código antigo continue funcionando enquanto migramos para nova arquitetura.
"""
from .domain.interfaces.repositories import (
    IConfigRepository,
    IClipboardService,
    IDataGenerator,
    IShortcutService,
    ILogger
)
from .container import Container


# Adaptadores para compatibilidade com código legado

class LegacyConfigManagerAdapter:
    """Adaptador para manter compatibilidade com ConfigManager antigo."""
    
    def __init__(self, config_path: str = None):
        self._repo = Container.get_config_repository(config_path)
    
    def get(self, key: str, default=None):
        return self._repo.get(key, default)
    
    def set(self, key: str, value):
        self._repo.set(key, value)
    
    def get_config_path(self):
        if hasattr(self._repo, 'config_dir'):
            return str(self._repo.config_dir)
        return ""
    
    def get_config_file_path(self):
        if hasattr(self._repo, 'config_file'):
            return str(self._repo.config_file)
        return ""
    
    @property
    def config(self):
        return self._repo.get_all()


class LegacyDataGeneratorAdapter:
    """Adaptador para manter compatibilidade com DataGenerator antigo."""
    
    def __init__(self, rapidapi_key: str = None):
        self._generator = Container.get_data_generator()
        if rapidapi_key is not None:
            self._generator.update_api_key(rapidapi_key)
    
    def generate_cpf(self, formatted: bool = True) -> str:
        return self._generator.generate_cpf(formatted)
    
    def generate_cep(self, formatted: bool = True) -> str:
        return self._generator.generate_cep(formatted)
    
    def generate_temporary_email(self):
        return self._generator.generate_email()
    
    def update_api_key(self, key: str):
        self._generator.update_api_key(key)


class LegacyClipboardManagerAdapter:
    """Adaptador para manter compatibilidade com ClipboardManager antigo."""
    
    def __init__(self):
        self._service = Container.get_clipboard_service()
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        service = Container.get_clipboard_service()
        return service.copy(text)
    
    @staticmethod
    def get_clipboard():
        service = Container.get_clipboard_service()
        return service.paste()
    
    @staticmethod
    def clear_clipboard() -> bool:
        service = Container.get_clipboard_service()
        return service.clear()
