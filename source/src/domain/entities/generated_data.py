"""
Entidades de domínio - Representam conceitos principais do negócio.
Independentes de frameworks e implementações específicas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneratedData:
    """Entidade que representa dados gerados."""
    
    data_type: str  # 'email', 'cpf', 'cep', 'name', 'cnpj', 'phone'
    value: str
    formatted: bool = True
    error: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Verifica se os dados são válidos."""
        return self.error is None and self.value is not None
    
    def __str__(self) -> str:
        return self.value


@dataclass
class ShortcutConfig:
    """Entidade que representa configuração de atalho."""
    
    hotkey: str  # Ex: 'ctrl+shift+e'
    action_type: str  # Ex: 'generate_email'
    description: str  # Descrição do atalho
    
    def is_valid(self) -> bool:
        """Valida o formato do atalho."""
        return '+' in self.hotkey and len(self.hotkey.split('+')) >= 2
