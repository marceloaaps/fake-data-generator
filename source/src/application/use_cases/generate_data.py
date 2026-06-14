"""
Casos de uso - Implementam a lógica de negócio da aplicação.
Dependem apenas de interfaces de domínio.
"""
from typing import Dict, Optional
from ...domain.interfaces.repositories import (
    IDataGenerator, IClipboardService, IConfigRepository, ILogger
)
from ...domain.entities.generated_data import GeneratedData


class GenerateCPFUseCase:
    """Caso de uso para gerar e copiar CPF."""
    
    def __init__(
        self,
        data_generator: IDataGenerator,
        clipboard_service: IClipboardService,
        logger: ILogger
    ):
        """
        Args:
            data_generator: Serviço de geração de dados
            clipboard_service: Serviço de clipboard
            logger: Serviço de logging
        """
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.logger = logger
    
    def execute(self, formatted: bool = True) -> GeneratedData:
        """
        Executa o caso de uso.
        
        Returns:
            GeneratedData com CPF gerado
        """
        try:
            cpf = self.data_generator.generate_cpf(formatted)
            
            if self.clipboard_service.copy(cpf):
                self.logger.info(f"CPF copiado: {cpf}")
                return GeneratedData(
                    data_type="cpf",
                    value=cpf,
                    formatted=formatted
                )
            else:
                error_msg = "Erro ao copiar CPF para clipboard"
                self.logger.error(error_msg)
                return GeneratedData(
                    data_type="cpf",
                    value="",
                    error=error_msg
                )
        except Exception as e:
            error_msg = f"Erro ao gerar CPF: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(
                data_type="cpf",
                value="",
                error=error_msg
            )


class GenerateCEPUseCase:
    """Caso de uso para gerar e copiar CEP."""
    
    def __init__(
        self,
        data_generator: IDataGenerator,
        clipboard_service: IClipboardService,
        logger: ILogger
    ):
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.logger = logger
    
    def execute(self, formatted: bool = True) -> GeneratedData:
        """Executa o caso de uso."""
        try:
            cep = self.data_generator.generate_cep(formatted)
            
            if self.clipboard_service.copy(cep):
                self.logger.info(f"CEP copiado: {cep}")
                return GeneratedData(
                    data_type="cep",
                    value=cep,
                    formatted=formatted
                )
            else:
                error_msg = "Erro ao copiar CEP para clipboard"
                self.logger.error(error_msg)
                return GeneratedData(
                    data_type="cep",
                    value="",
                    error=error_msg
                )
        except Exception as e:
            error_msg = f"Erro ao gerar CEP: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(
                data_type="cep",
                value="",
                error=error_msg
            )


class GenerateEmailUseCase:
    """Caso de uso para gerar e copiar email temporário."""
    
    def __init__(
        self,
        data_generator: IDataGenerator,
        clipboard_service: IClipboardService,
        logger: ILogger
    ):
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.logger = logger
    
    def execute(self) -> GeneratedData:
        """Executa o caso de uso."""
        try:
            result = self.data_generator.generate_email()
            
            if result.get("error"):
                error_msg = result["error"]
                self.logger.warning(f"Email: {error_msg}")
                return GeneratedData(
                    data_type="email",
                    value="",
                    error=error_msg
                )
            
            email = result.get("email", "")
            
            if self.clipboard_service.copy(email):
                self.logger.info(f"Email copiado: {email}")
                return GeneratedData(
                    data_type="email",
                    value=email
                )
            else:
                error_msg = "Erro ao copiar email para clipboard"
                self.logger.error(error_msg)
                return GeneratedData(
                    data_type="email",
                    value="",
                    error=error_msg
                )
        except Exception as e:
            error_msg = f"Erro ao gerar email: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(
                data_type="email",
                value="",
                error=error_msg
            )


class GenerateNameUseCase:
    """Caso de uso para gerar e copiar nome com contador ou modo aleatório."""

    def __init__(
        self,
        data_generator: IDataGenerator,
        clipboard_service: IClipboardService,
        config_repository: IConfigRepository,
        logger: ILogger
    ):
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.config_repository = config_repository
        self.logger = logger

    def execute(self) -> GeneratedData:
        try:
            base_name = str(self.config_repository.get("name.base", "") or "").strip()
            counter = int(self.config_repository.get("name.counter", 0) or 0)
            random_enabled = bool(self.config_repository.get("name.random_enabled", False))

            result = self.data_generator.generate_name(base_name, counter, random_enabled)

            if result.get("error"):
                error_msg = result["error"]
                self.logger.warning(f"Nome: {error_msg}")
                return GeneratedData(
                    data_type="name",
                    value="",
                    error=error_msg
                )

            name = result.get("name", "")
            if not name:
                error_msg = "Erro ao gerar nome"
                self.logger.error(error_msg)
                return GeneratedData(data_type="name", value="", error=error_msg)

            if self.clipboard_service.copy(name):
                if not random_enabled:
                    next_counter = int(result.get("counter", counter) or counter)
                    self.config_repository.set("name.counter", next_counter)

                self.logger.info(f"Nome copiado: {name}")
                return GeneratedData(
                    data_type="name",
                    value=name
                )

            error_msg = "Erro ao copiar nome para clipboard"
            self.logger.error(error_msg)
            return GeneratedData(data_type="name", value="", error=error_msg)
        except Exception as e:
            error_msg = f"Erro ao gerar nome: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(
                data_type="name",
                value="",
                error=error_msg
            )


class GenerateCNPJUseCase:
    """Caso de uso para gerar e copiar CNPJ."""

    def __init__(self, data_generator: IDataGenerator, clipboard_service: IClipboardService, logger: ILogger):
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.logger = logger

    def execute(self, formatted: bool = True) -> GeneratedData:
        try:
            result = self.data_generator.generate_cnpj(formatted)
            if result.get("error"):
                error_msg = result["error"]
                self.logger.warning(f"CNPJ: {error_msg}")
                return GeneratedData(data_type="cnpj", value="", error=error_msg)

            cnpj = result.get("cnpj", "")
            if self.clipboard_service.copy(cnpj):
                self.logger.info(f"CNPJ copiado: {cnpj}")
                return GeneratedData(data_type="cnpj", value=cnpj, formatted=formatted)

            error_msg = "Erro ao copiar CNPJ para clipboard"
            self.logger.error(error_msg)
            return GeneratedData(data_type="cnpj", value="", error=error_msg)
        except Exception as e:
            error_msg = f"Erro ao gerar CNPJ: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(data_type="cnpj", value="", error=error_msg)


class GeneratePhoneUseCase:
    """Caso de uso para gerar e copiar celular brasileiro."""

    def __init__(self, data_generator: IDataGenerator, clipboard_service: IClipboardService, logger: ILogger):
        self.data_generator = data_generator
        self.clipboard_service = clipboard_service
        self.logger = logger

    def execute(self, formatted: bool = True) -> GeneratedData:
        try:
            result = self.data_generator.generate_phone(formatted)
            if result.get("error"):
                error_msg = result["error"]
                self.logger.warning(f"Telefone: {error_msg}")
                return GeneratedData(data_type="phone", value="", error=error_msg)

            phone = result.get("phone", "")
            if self.clipboard_service.copy(phone):
                self.logger.info(f"Telefone copiado: {phone}")
                return GeneratedData(data_type="phone", value=phone, formatted=formatted)

            error_msg = "Erro ao copiar telefone para clipboard"
            self.logger.error(error_msg)
            return GeneratedData(data_type="phone", value="", error=error_msg)
        except Exception as e:
            error_msg = f"Erro ao gerar telefone: {str(e)}"
            self.logger.error(error_msg)
            return GeneratedData(data_type="phone", value="", error=error_msg)
