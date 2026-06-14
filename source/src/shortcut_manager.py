"""
Gerenciador de Atalhos - COMPATIBILIDADE LEGADO.
Redireciona para nova arquitetura via container.
"""
from .container import Container
from .domain.interfaces.repositories import ILogger


class ShortcutManager:
    """Compatibilidade legado para ShortcutManager."""
    
    def __init__(self, config_manager, callback_handler=None):
        self.config_manager = config_manager
        self.callback_handler = callback_handler
        self.logger = Container.get_logger()
        self.shortcut_service = Container.get_shortcut_service(self.logger)
        self.data_generator = Container.get_data_generator(config_manager._repo)
        self.registered_shortcuts = {}
        self.monitoring = False
    
    def _normalize_shortcut(self, hotkey: str) -> str:
        """Normaliza atalho para formato padrão."""
        return hotkey.lower().strip()
    
    def start_monitoring(self):
        """Inicia monitoramento de atalhos."""
        shortcuts_config = self.config_manager.config.get("shortcuts", {})
        
        def on_email():
            try:
                from .application.use_cases.generate_data import GenerateEmailUseCase
                use_case = GenerateEmailUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.logger
                )
                result = use_case.execute()
                if self.callback_handler:
                    self.callback_handler("email", {"email": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para email")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar email: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("email", {"email": None, "error": str(e)})
        
        def on_cpf():
            try:
                from .application.use_cases.generate_data import GenerateCPFUseCase
                use_case = GenerateCPFUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.logger
                )
                result = use_case.execute()
                if self.callback_handler:
                    self.callback_handler("cpf", {"cpf": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para cpf")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar CPF: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("cpf", {"cpf": None, "error": str(e)})

        def on_name():
            try:
                from .application.use_cases.generate_data import GenerateNameUseCase
                use_case = GenerateNameUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.config_manager._repo,
                    self.logger
                )
                result = use_case.execute()
                if self.callback_handler:
                    self.callback_handler("name", {"name": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para name")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar nome: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("name", {"name": None, "error": str(e)})

        def on_cnpj():
            try:
                from .application.use_cases.generate_data import GenerateCNPJUseCase
                use_case = GenerateCNPJUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.logger
                )
                result = use_case.execute(formatted=True)
                if self.callback_handler:
                    self.callback_handler("cnpj", {"cnpj": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para cnpj")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar CNPJ: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("cnpj", {"cnpj": None, "error": str(e)})

        def on_phone():
            try:
                from .application.use_cases.generate_data import GeneratePhoneUseCase
                use_case = GeneratePhoneUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.logger
                )
                result = use_case.execute(formatted=True)
                if self.callback_handler:
                    self.callback_handler("phone", {"phone": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para phone")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar celular: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("phone", {"phone": None, "error": str(e)})
        
        def on_cep():
            try:
                from .application.use_cases.generate_data import GenerateCEPUseCase
                use_case = GenerateCEPUseCase(
                    self.data_generator,
                    Container.get_clipboard_service(),
                    self.logger
                )
                result = use_case.execute()
                if self.callback_handler:
                    self.callback_handler("cep", {"cep": result.value, "error": result.error})
                else:
                    self.logger.debug("Nenhum callback_handler definido para cep")
            except Exception as e:
                import traceback
                self.logger.error(f"Erro ao gerar CEP: {str(e)}\n{traceback.format_exc()}")
                if self.callback_handler:
                    self.callback_handler("cep", {"cep": None, "error": str(e)})
        
        try:
            # Limpar atalhos anteriores
            self.shortcut_service.unregister_all()
            
            # Registrar novos atalhos
            email_key = shortcuts_config.get("email", "ctrl+shift+e")
            name_key = shortcuts_config.get("name", "ctrl+shift+n")
            cpf_key = shortcuts_config.get("cpf", "ctrl+shift+c")
            cnpj_key = shortcuts_config.get("cnpj", "ctrl+shift+j")
            phone_key = shortcuts_config.get("phone", "ctrl+shift+t")
            cep_key = shortcuts_config.get("cep", "ctrl+shift+z")
            
            self.shortcut_service.register(email_key, on_email)
            self.shortcut_service.register(name_key, on_name)
            self.shortcut_service.register(cpf_key, on_cpf)
            self.shortcut_service.register(cnpj_key, on_cnpj)
            self.shortcut_service.register(phone_key, on_phone)
            self.shortcut_service.register(cep_key, on_cep)
            self.monitoring = True
            self.logger.info(
                f"Atalhos registrados: email={email_key}, name={name_key}, cpf={cpf_key}, cnpj={cnpj_key}, phone={phone_key}, cep={cep_key}"
            )
        except Exception as e:
            import traceback
            self.logger.error(f"Falha ao registrar atalhos: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def stop_monitoring(self):
        """Para o monitoramento de atalhos."""
        try:
            self.shortcut_service.unregister_all()
            self.monitoring = False
            self.logger.info("Atalhos removidos")
        except Exception as e:
            self.logger.error(f"Erro ao remover atalhos: {str(e)}")
    
    def is_monitoring(self):
        """Verifica se está monitorando."""
        return self.monitoring
    
    def update_api_key(self, key: str):
        """Atualiza chave de API."""
        self.data_generator.update_api_key(key)
