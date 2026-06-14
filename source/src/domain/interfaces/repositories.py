"""
Interfaces de domínio - Definem contratos que devem ser implementados.
Seguem o princípio de Inversão de Dependência (DIP).
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any


class IConfigRepository(ABC):
    """Interface para gerenciar configurações."""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração."""
        pass
    
    @abstractmethod
    def get_all(self) -> Dict[str, Any]:
        """Obtém todas as configurações."""
        pass


class IClipboardService(ABC):
    """Interface para gerenciar clipboard do sistema."""
    
    @abstractmethod
    def copy(self, text: str) -> bool:
        """Copia texto para clipboard."""
        pass
    
    @abstractmethod
    def paste(self) -> Optional[str]:
        """Obtém conteúdo do clipboard."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Limpa o clipboard."""
        pass


class IDataGenerator(ABC):
    """Interface para gerar dados temporários."""
    
    @abstractmethod
    def generate_cpf(self, formatted: bool = True) -> str:
        """Gera CPF válido."""
        pass
    
    @abstractmethod
    def generate_cep(self, formatted: bool = True) -> str:
        """Gera CEP válido."""
        pass
    
    @abstractmethod
    def generate_email(self) -> Dict[str, Optional[str]]:
        """Gera email temporário."""
        pass

    @abstractmethod
    def generate_name(self, base_name: str, counter: int, random_enabled: bool = False) -> Dict[str, Optional[str]]:
        """Gera nome com contador romano ou nome aleatório."""
        pass

    @abstractmethod
    def generate_cnpj(self, formatted: bool = True) -> Dict[str, Optional[str]]:
        """Gera CNPJ válido."""
        pass

    @abstractmethod
    def generate_phone(self, formatted: bool = True) -> Dict[str, Optional[str]]:
        """Gera celular brasileiro válido."""
        pass


class IShortcutService(ABC):
    """Interface para gerenciar atalhos globais de teclado."""
    
    @abstractmethod
    def register(self, hotkey: str, callback: callable) -> None:
        """Registra um atalho global."""
        pass
    
    @abstractmethod
    def unregister_all(self) -> None:
        """Remove todos os atalhos."""
        pass
    
    @abstractmethod
    def is_monitoring(self) -> bool:
        """Verifica se está monitorando."""
        pass


class ILogger(ABC):
    """Interface para logging centralizado."""
    
    @abstractmethod
    def debug(self, message: str) -> None:
        """Registra mensagem de debug."""
        pass
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Registra mensagem de informação."""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Registra mensagem de aviso."""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Registra mensagem de erro."""
        pass
