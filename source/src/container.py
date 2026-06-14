"""
Container de Injeção de Dependência (DI).
Centraliza a criação e configuração de todas as dependências.
Segue o padrão Service Locator.
"""
from typing import Dict, Any
from .domain.interfaces.repositories import (
    IConfigRepository,
    IClipboardService,
    IDataGenerator,
    IShortcutService,
    ILogger
)
from .infrastructure.config.file_config_repository import FileConfigRepository
from .infrastructure.clipboard.system_clipboard import SystemClipboardService
from .infrastructure.data_generator.temp_mail_generator import TempMailDataGenerator
from .infrastructure.shortcuts.global_keyboard_shortcuts import GlobalKeyboardShortcutService
from .infrastructure.logger.console_logger import ConsoleLogger
from .application.use_cases.generate_data import (
    GenerateCPFUseCase,
    GenerateCEPUseCase,
    GenerateEmailUseCase,
    GenerateNameUseCase,
    GenerateCNPJUseCase,
    GeneratePhoneUseCase
)


class Container:
    """Container de injeção de dependência."""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def reset(cls) -> None:
        """Reseta todas as instâncias (útil para testes)."""
        cls._instances.clear()
    
    @classmethod
    def get_logger(cls, debug: bool = False) -> ILogger:
        """Obtém instância do logger."""
        key = "logger"
        if key not in cls._instances:
            cls._instances[key] = ConsoleLogger(debug_mode=debug)
        return cls._instances[key]
    
    @classmethod
    def get_config_repository(cls, config_path: str = None) -> IConfigRepository:
        """Obtém instância do repositório de configuração."""
        key = "config"
        if key not in cls._instances:
            cls._instances[key] = FileConfigRepository(config_path)
        return cls._instances[key]
    
    @classmethod
    def get_clipboard_service(cls) -> IClipboardService:
        """Obtém instância do serviço de clipboard."""
        key = "clipboard"
        if key not in cls._instances:
            cls._instances[key] = SystemClipboardService()
        return cls._instances[key]
    
    @classmethod
    def get_data_generator(cls, config: IConfigRepository = None) -> IDataGenerator:
        """Obtém instância do gerador de dados."""
        key = "data_generator"
        if key not in cls._instances:
            if config is None:
                config = cls.get_config_repository()
            api_key = config.get("api.rapidapi_key")
            cls._instances[key] = TempMailDataGenerator(api_key)
        return cls._instances[key]
    
    @classmethod
    def get_shortcut_service(cls, logger: ILogger = None) -> IShortcutService:
        """Obtém instância do serviço de atalhos."""
        key = "shortcuts"
        if key not in cls._instances:
            if logger is None:
                logger = cls.get_logger()
            cls._instances[key] = GlobalKeyboardShortcutService(logger)
        return cls._instances[key]
    
    # Casos de Uso
    @classmethod
    def get_generate_cpf_use_case(cls) -> GenerateCPFUseCase:
        """Obtém caso de uso de geração de CPF."""
        return GenerateCPFUseCase(
            data_generator=cls.get_data_generator(),
            clipboard_service=cls.get_clipboard_service(),
            logger=cls.get_logger()
        )
    
    @classmethod
    def get_generate_cep_use_case(cls) -> GenerateCEPUseCase:
        """Obtém caso de uso de geração de CEP."""
        return GenerateCEPUseCase(
            data_generator=cls.get_data_generator(),
            clipboard_service=cls.get_clipboard_service(),
            logger=cls.get_logger()
        )
    
    @classmethod
    def get_generate_email_use_case(cls) -> GenerateEmailUseCase:
        """Obtém caso de uso de geração de email."""
        return GenerateEmailUseCase(
            data_generator=cls.get_data_generator(),
            clipboard_service=cls.get_clipboard_service(),
            logger=cls.get_logger()
        )

    @classmethod
    def get_generate_name_use_case(cls, config: IConfigRepository = None) -> GenerateNameUseCase:
        """Obtém caso de uso de geração de nome."""
        if config is None:
            config = cls.get_config_repository()
        return GenerateNameUseCase(
            data_generator=cls.get_data_generator(config),
            clipboard_service=cls.get_clipboard_service(),
            config_repository=config,
            logger=cls.get_logger()
        )

    @classmethod
    def get_generate_cnpj_use_case(cls) -> GenerateCNPJUseCase:
        """Obtém caso de uso de geração de CNPJ."""
        return GenerateCNPJUseCase(
            data_generator=cls.get_data_generator(),
            clipboard_service=cls.get_clipboard_service(),
            logger=cls.get_logger()
        )

    @classmethod
    def get_generate_phone_use_case(cls) -> GeneratePhoneUseCase:
        """Obtém caso de uso de geração de celular."""
        return GeneratePhoneUseCase(
            data_generator=cls.get_data_generator(),
            clipboard_service=cls.get_clipboard_service(),
            logger=cls.get_logger()
        )
