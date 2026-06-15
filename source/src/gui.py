"""
Interface gráfica do aplicativo usando PySimpleGUI com design moderno.
Inspirado no padrão visual do GitHub com tema escuro minimalista.
Barra de título customizada interna.
"""
import PySimpleGUI as sg
import webbrowser
from pathlib import Path
from .config_manager import ConfigManager
from .data_generator import DataGenerator
from .clipboard_manager import ClipboardManager
from .shortcut_manager import ShortcutManager

# Configuração de tema moderno (inspirado no GitHub)
COLORS = {
    'bg': '#0d1117',           # Fundo escuro do GitHub
    'fg': '#c9d1d9',           # Texto claro
    'primary': '#58a6ff',      # Azul GitHub
    'success': '#3fb950',      # Verde
    'danger': '#f85149',       # Vermelho
    'warning': '#d29922',      # Amarelo/Laranja
    'border': "#010305",       # Bordas
    'card_bg': '#161b22',      # Fundo de cards
    'titlebar': '#010409',     # Barra de título (mais escura)
}

sg.theme('DarkGray13')
sg.set_options(
    font=('Segoe UI', 10),
    element_padding=(8, 8)
)


class FakeDataGeneratorGUI:
    """Interface gráfica do aplicativo com design moderno e barra de título customizada"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa a interface gráfica com tema moderno e barra customizada.
        
        Args:
            config_path: Caminho para a pasta de configuração
        """
        self.config_manager = ConfigManager(config_path)
        self.data_generator = DataGenerator(
            self.config_manager.get("api.rapidapi_key")
        )
        self.clipboard_manager = ClipboardManager()
        self.shortcut_manager = ShortcutManager(
            self.config_manager,
            callback_handler=self._on_shortcut_triggered
        )
        
        self.window = None
        self.is_minimized = False
        self.current_page = 'main'  # Página atual: 'main' ou 'config'
        self.api_key_visible = False  # Rastreia se API key está visível
        self.generated_data_log = []  # Log de dados gerados
    
    def _create_titlebar(self) -> list:
        """Cria uma barra de título customizada com botões de minimizar e fechar"""
        return [
            [
                sg.Column(
                    [
                        [
                            sg.Text(
                                'Fake Data Generator - By Marcelo A.',
                                font=('Segoe UI', 10, 'normal'),
                                text_color=COLORS['fg'],
                                expand_x=True,
                                key='-TITLEBAR-'
                            ),
                            sg.Button(
                                '−',  # Botão minimizar
                                key='-MINIMIZE-',
                                size=(2, 1),
                                button_color=(COLORS['fg'], COLORS['titlebar']),
                                border_width=0,
                                font=('Segoe UI', 10, 'bold')
                            ),
                            sg.Button(
                                '×',  # Botão fechar
                                key='-CLOSE-',
                                size=(2, 1),
                                button_color=(COLORS['danger'], COLORS['titlebar']),
                                border_width=0,
                                font=('Segoe UI', 10, 'bold')
                            ),
                        ]
                    ],
                    background_color=COLORS['titlebar'],
                    expand_x=True,
                    pad=(0, 0)
                )
            ]
        ]
    
    def _create_section_header(self, title: str) -> list:
        """Cria um header de seção estilo GitHub"""
        return [
            [sg.Text(title, font=('Segoe UI', 10, 'bold'), text_color=COLORS['primary'])],
            [sg.Text('_' * 45, text_color=COLORS['border'], font=('Segoe UI', 8))]
        ]
    
    def _create_thin_separator(self) -> list:
        """Cria um separador fino minimalista"""
        return [
            [sg.Text('·' * 25, text_color=COLORS['border'], font=('Segoe UI', 7), pad=(0, (3, 3)))]
        ]
    
    def _create_status_indicator(self) -> list:
        """Cria um indicador de status visual"""
        return [
            [
                sg.Frame(
                    'Status dos Atalhos',
                    [
                        [
                            sg.Text('Atalhos Globais', font=('Segoe UI', 10)),
                            sg.Text('', key='-STATUS_INDICATOR-', 
                                   font=('Segoe UI', 12, 'bold'),
                                   text_color=COLORS['danger'])
                        ],
                        [
                            sg.Text(
                                'Desativado',
                                key='-HOTKEY_STATUS-',
                                font=('Segoe UI', 9),
                                text_color=COLORS['warning'],
                                size=(35, 1)
                            )
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['card_bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))]  # Espaço
        ]
    
    def _create_shortcuts_display(self) -> list:
        """Cria a exibição de atalhos configurados com opção de editar inline"""
        email_shortcut = self.config_manager.get('shortcuts.email', 'Ctrl+Shift+E')
        cpf_shortcut = self.config_manager.get('shortcuts.cpf', 'Ctrl+Shift+C')
        cep_shortcut = self.config_manager.get('shortcuts.cep', 'Ctrl+Shift+Z')
        
        return [
            [
                sg.Frame(
                    'Atalhos Configurados',
                    [
                        # Email
                        [
                            sg.Button(
                                'Email',
                                key='-EMAIL_SHORTCUT-',
                                size=(8, 1),
                                font=('Segoe UI', 8, 'bold'),
                                border_width=1
                            ),
                            sg.Text('Email:', font=('Segoe UI', 9, 'bold'), size=(8, 1)),
                            sg.InputText(
                                email_shortcut,
                                key='-SHORTCUT_EMAIL_MAIN-',
                                size=(14, 1),
                                font=('Segoe UI', 9),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['primary']
                            ),
                            sg.Button(
                                '✓',
                                key='-UPDATE_EMAIL_SHORTCUT-',
                                size=(2, 1),
                                button_color=(COLORS['success'], COLORS['titlebar']),
                                border_width=0,
                                font=('Segoe UI', 9, 'bold')
                            ),
                        ],
                        # CPF
                        [
                            sg.Button(
                                'CPF',
                                key='-CPF_SHORTCUT-',
                                size=(8, 1),
                                font=('Segoe UI', 8, 'bold'),
                                border_width=1
                            ),
                            sg.Text('CPF:', font=('Segoe UI', 9, 'bold'), size=(8, 1)),
                            sg.InputText(
                                cpf_shortcut,
                                key='-SHORTCUT_CPF_MAIN-',
                                size=(14, 1),
                                font=('Segoe UI', 9),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['primary']
                            ),
                            sg.Button(
                                '✓',
                                key='-UPDATE_CPF_SHORTCUT-',
                                size=(2, 1),
                                button_color=(COLORS['success'], COLORS['titlebar']),
                                border_width=0,
                                font=('Segoe UI', 9, 'bold')
                            ),
                        ],
                        # CEP
                        [
                            sg.Button(
                                'CEP',
                                key='-CEP_SHORTCUT-',
                                size=(8, 1),
                                font=('Segoe UI', 8, 'bold'),
                                border_width=1
                            ),
                            sg.Text('CEP:', font=('Segoe UI', 9, 'bold'), size=(8, 1)),
                            sg.InputText(
                                cep_shortcut,
                                key='-SHORTCUT_CEP_MAIN-',
                                size=(14, 1),
                                font=('Segoe UI', 9),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['primary']
                            ),
                            sg.Button(
                                '✓',
                                key='-UPDATE_CEP_SHORTCUT-',
                                size=(2, 1),
                                button_color=(COLORS['success'], COLORS['titlebar']),
                                border_width=0,
                                font=('Segoe UI', 9, 'bold')
                            ),
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['card_bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))]  # Espaço
        ]
    
    def _create_api_key_field(self) -> list:
        """Cria o campo de API key com toggle para mostrar/esconder"""
        current_key = self.config_manager.get("api.rapidapi_key", "")
        
        return [
            *self._create_section_header('Informações de API Key'),
            [
                sg.InputText(
                    current_key,
                    key='-APIKEY_MAIN-',
                    password_char='*',
                    size=(28, 1),
                    font=('Segoe UI', 10),
                    background_color=COLORS['card_bg'],
                    text_color=COLORS['fg']
                ),
                sg.Button(
                    '👁',  # Olho para mostrar/esconder
                    key='-TOGGLE_API_KEY-',
                    size=(3, 1),
                    button_color=(COLORS['fg'], COLORS['border']),
                    border_width=0,
                    font=('Segoe UI', 9, 'bold'),
                    tooltip='Mostrar/Esconder API Key'
                ),
                sg.Button(
                    '✓',  # Confirmação
                    key='-UPDATE_API_KEY-',
                    size=(2, 1),
                    button_color=(COLORS['success'], COLORS['titlebar']),
                    border_width=0,
                    font=('Segoe UI', 9, 'bold'),
                    tooltip='Salvar API Key'
                ),
            ],
            [
                sg.Text('Consiga em: ', font=('Segoe UI', 8)),
                sg.Text(
                    'rapidapi.com',
                    font=('Segoe UI', 8, 'underline'),
                    text_color=COLORS['warning'],
                    key='-RAPIDAPI_LINK-',
                    enable_events=True,
                    tooltip='Clique para abrir rapidapi.com'
                ),
            ],
            *self._create_thin_separator(),
        ]
    
    def _create_action_buttons(self) -> list:
        """Cria botões de ação com design moderno e atalhos visuais"""
        button_style = {
            'font': ('Segoe UI', 9, 'bold'),
            'size': (12, 2),
            'border_width': 1,
        }
        
        return [
            [
                sg.Button(
                    'Email (E)',
                    key='-EMAIL-',
                    **button_style
                ),
                sg.Button(
                    'CPF (C)',
                    key='-CPF-',
                    **button_style
                ),
                sg.Button(
                    'CEP (Z)',
                    key='-CEP-',
                    **button_style
                ),
            ],
        ]
    
    def _create_shortcuts_usage_log(self) -> list:
        """Cria o painel de log de atalhos utilizados (lado direito)"""
        return [
            
        ]
    
    def _create_main_page(self) -> list:
        """Cria o layout da página principal com 2 colunas reorganizadas"""
        
        left_column = [
            # Seção 1: Texto e Descrição
            *self._create_section_header('Fake Data Generator'),
            [
                sg.Text(
                    'Gerador rápido de dados\ntemporários com um clique\nou atalho global',
                    font=('Segoe UI', 9),
                    text_color=COLORS['fg']
                )
            ],
            *self._create_thin_separator(),
            
            # Seção 2: Informações de API Key
            *self._create_api_key_field(),
            
            # Seção 3: Status dos Atalhos
            *self._create_section_header('Status'),
            [
                sg.Text('Globais: ', font=('Segoe UI', 8)),
                sg.Text('●', key='-STATUS_INDICATOR-', font=('Segoe UI', 10), text_color=COLORS['danger']),
                sg.Text('Desativado', key='-HOTKEY_STATUS-', font=('Segoe UI', 8, 'bold'), text_color=COLORS['warning']),
            ],
            [
                sg.Checkbox(
                    'Ativar atalhos',
                    key='-GLOBAL_HOTKEYS-',
                    default=False,
                    enable_events=True,
                    font=('Segoe UI', 8)
                )
            ],
            *self._create_thin_separator(),
            
            # Seção: Log de Atalhos Utilizados
            *self._create_shortcuts_usage_log(),
        ]
        
        right_column = [
            # Seção 4: Atalhos Configurados
            *self._create_section_header('Atalhos'),
            *self._create_shortcuts_display(),
            *self._create_thin_separator(),
            
            # Seção 6: Log de Resultados
            *self._create_section_header('Últimos Dados'),
            [
                sg.Multiline(
                    '',
                    size=(50, 12),
                    key='-GENERATED_LOG-',
                    disabled=True,
                    font=('Consolas', 8),
                    background_color=COLORS['card_bg'],
                    text_color=COLORS['success']
                )
            ],
        ]
        
        return [
            [
                sg.Column(left_column, vertical_alignment='top', expand_x=True, expand_y=True, pad=(5, 5), scrollable=False, vertical_scroll_only=True),
                sg.Column(right_column, vertical_alignment='top', expand_x=True, expand_y=True, pad=(5, 5), scrollable=False, vertical_scroll_only=True)
            ]
        ]
    
    def _create_config_page(self) -> list:
        """Cria o layout da página de configurações"""
        current_key = self.config_manager.get("api.rapidapi_key", "")
        email_shortcut = self.config_manager.get('shortcuts.email', 'ctrl+shift+e')
        cpf_shortcut = self.config_manager.get('shortcuts.cpf', 'ctrl+shift+c')
        cep_shortcut = self.config_manager.get('shortcuts.cep', 'ctrl+shift+z')
        
        return [
            [
                sg.Text(
                    'Configuracoes',
                    font=('Segoe UI', 14, 'bold'),
                    text_color=COLORS['primary']
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Seção API
            [
                sg.Frame(
                    'API RapidAPI',
                    [
                        [
                            sg.Text(
                                'Chave de API:',
                                font=('Segoe UI', 10),
                                size=(20, 1)
                            )
                        ],
                        [
                            sg.InputText(
                                current_key,
                                key='-APIKEY-',
                                password_char='*',
                                size=(35, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            )
                        ],
                        [
                            sg.Text(
                                'Obtenha em: https://rapidapi.com',
                                font=('Segoe UI', 8),
                                text_color=COLORS['warning']
                            )
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['card_bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Seção Atalhos
            [
                sg.Frame(
                    'Atalhos de Teclado',
                    [
                        [
                            sg.Text('Email:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                email_shortcut,
                                key='-SHORTCUT_EMAIL-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [sg.Text('', size=(40, 1))],
                        [
                            sg.Text('CPF:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                cpf_shortcut,
                                key='-SHORTCUT_CPF-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [sg.Text('', size=(40, 1))],
                        [
                            sg.Text('CEP:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                cep_shortcut,
                                key='-SHORTCUT_CEP-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [
                            sg.Text(
                                'Exemplo: ctrl+shift+e, alt+e, etc',
                                font=('Segoe UI', 8),
                                text_color=COLORS['warning']
                            )
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Botões
            [
                sg.Button(
                    'Salvar',
                    key='-CONFIG_SAVE-',
                    font=('Segoe UI', 10, 'bold'),
                    size=(15, 2),
                    button_color=(COLORS['fg'], COLORS['success']),
                    border_width=1
                ),
                sg.Button(
                    'Voltar',
                    key='-CONFIG_BACK-',
                    font=('Segoe UI', 10, 'bold'),
                    size=(15, 2),
                    border_width=1
                ),
            ]
        ]
    
    def create_main_window(self):
        """Cria a janela única com navegação entre páginas"""
        
        layout = [
            # Barra de título customizada
            *self._create_titlebar(),
            
            # Conteúdo das páginas (em Columns invisíveis)
            [
                # Página Principal
                sg.Column(
                    [
                        [
                            sg.Column(
                                self._create_main_page(),
                                background_color=COLORS['bg'],
                                expand_x=True,
                                expand_y=True,
                                pad=(10, 10)
                            )
                        ]
                    ],
                    key='-PAGE_MAIN-',
                    visible=True,
                    background_color=COLORS['bg'],
                    expand_x=True,
                    expand_y=True
                ),
                
                # Página de Configurações
                sg.Column(
                    [
                        [
                            sg.Column(
                                self._create_config_page(),
                                background_color=COLORS['bg'],
                                expand_x=True,
                                expand_y=True,
                                pad=(10, 10)
                            )
                        ]
                    ],
                    key='-PAGE_CONFIG-',
                    visible=False,
                    background_color=COLORS['bg'],
                    expand_x=True,
                    expand_y=True
                ),
            ]
        ]
        
        self.window = sg.Window(
            'Fake Data Generator',
            layout,
            size=(1200, 650),
            background_color=COLORS['bg'],
            finalize=True,
            no_titlebar=True,
            grab_anywhere=True,
            icon=None
        )
        
        # Nota: Os botões dentro de estruturas aninhadas (Frames/Columns) 
        # não precisam ter cores atualizadas aqui, pois já têm cores definidas na criação
    
    def create_config_window(self):
        """Cria a janela de configurações com design moderno"""
        
        current_key = self.config_manager.get("api.rapidapi_key", "")
        email_shortcut = self.config_manager.get('shortcuts.email', 'ctrl+shift+e')
        cpf_shortcut = self.config_manager.get('shortcuts.cpf', 'ctrl+shift+c')
        cep_shortcut = self.config_manager.get('shortcuts.cep', 'ctrl+shift+z')
        
        layout = [
            [
                sg.Text(
                    'Configuracoes',
                    font=('Segoe UI', 14, 'bold'),
                    text_color=COLORS['primary']
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Seção API
            [
                sg.Frame(
                    'API RapidAPI',
                    [
                        [
                            sg.Text(
                                'Chave de API:',
                                font=('Segoe UI', 10),
                                size=(20, 1)
                            )
                        ],
                        [
                            sg.InputText(
                                current_key,
                                key='-APIKEY-',
                                password_char='*',
                                size=(35, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            )
                        ],
                        [
                            sg.Text(
                                'Obtenha em: https://rapidapi.com',
                                font=('Segoe UI', 8),
                                text_color=COLORS['warning']
                            )
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['card_bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Seção Atalhos
            [
                sg.Frame(
                    'Atalhos de Teclado',
                    [
                        [
                            sg.Text('Email:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                email_shortcut,
                                key='-SHORTCUT_EMAIL-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [sg.Text('', size=(40, 1))],
                        [
                            sg.Text('CPF:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                cpf_shortcut,
                                key='-SHORTCUT_CPF-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [sg.Text('', size=(40, 1))],
                        [
                            sg.Text('CEP:', font=('Segoe UI', 10), size=(15, 1)),
                            sg.InputText(
                                cep_shortcut,
                                key='-SHORTCUT_CEP-',
                                size=(20, 1),
                                font=('Segoe UI', 10),
                                background_color=COLORS['card_bg'],
                                text_color=COLORS['fg']
                            ),
                        ],
                        [
                            sg.Text(
                                'Exemplo: ctrl+shift+e, alt+e, etc',
                                font=('Segoe UI', 8),
                                text_color=COLORS['warning']
                            )
                        ],
                    ],
                    font=('Segoe UI', 10, 'bold'),
                    title_color=COLORS['primary'],
                    background_color=COLORS['card_bg'],
                    border_width=1
                )
            ],
            [sg.Text('', size=(40, 1))],
            
            # Botões
            [
                sg.Button(
                    'Salvar',
                    key='-SAVE-',
                    font=('Segoe UI', 10, 'bold'),
                    size=(15, 2),
                    button_color=(COLORS['fg'], COLORS['success']),
                    border_width=1
                ),
                sg.Button(
                    'Cancelar',
                    key='-CANCEL-',
                    font=('Segoe UI', 10, 'bold'),
                    size=(15, 2),
                    border_width=1
                ),
            ]
        ]
        
        config_window = sg.Window(
            'Configuracoes',
            layout,
            modal=True,
            background_color=COLORS['bg'],
            size=(480, 500)
        )
        
        return config_window
    
    def handle_config_window(self, config_window):
        """Trata eventos da janela de configurações"""
        while True:
            event, values = config_window.read()
            
            if event == sg.WINDOW_CLOSED or event == '-CANCEL-':
                break
            
            if event == '-SAVE-':
                # Salva as configurações
                self.config_manager.set('api.rapidapi_key', values['-APIKEY-'])
                self.config_manager.set('shortcuts.email', values['-SHORTCUT_EMAIL-'])
                self.config_manager.set('shortcuts.cpf', values['-SHORTCUT_CPF-'])
                self.config_manager.set('shortcuts.cep', values['-SHORTCUT_CEP-'])
                
                # Atualiza o data generator com a nova chave
                self.data_generator.update_api_key(values['-APIKEY-'])
                self.shortcut_manager.update_api_key(values['-APIKEY-'])
                
                sg.popup_ok(
                    'Configuracoes salvas com sucesso!',
                    title='Sucesso',
                    background_color=COLORS['bg'],
                    text_color=COLORS['success']
                )
                break
        
        config_window.close()
    
    def update_output(self, message: str, message_type: str = 'info'):
        """
        Atualiza o campo de saída com uma mensagem formatada.
        
        Args:
            message: Mensagem a exibir
            message_type: 'success', 'error', 'warning', 'info'
        """
        if self.window:
            # Prefixos visuais para tipos de mensagem
            prefixes = {
                'success': '[OK]',
                'error': '[ERRO]',
                'warning': '[AVISO]',
                'info': '[INFO]',
            }
            prefix = prefixes.get(message_type, '[INFO]')
            
            current_output = self.window['-OUTPUT-'].get() if '-OUTPUT-' in self.window.AllKeysDict else ''
            new_output = f"{prefix} {message}\n" + current_output
            
            # Limita a exibição aos últimas linhas
            lines = new_output.split('\n')[:15]
            if '-OUTPUT-' in self.window.AllKeysDict:
                self.window['-OUTPUT-'].update('\n'.join(lines))
    
    def update_generated_log(self, data_type: str, value: str):
        """Atualiza o log de dados gerados"""
        if self.window:
            # Formata a mensagem
            if data_type == 'email':
                msg = f'Email criado: {value}'
            elif data_type == 'cpf':
                msg = f'CPF criado: {value}'
            elif data_type == 'cep':
                msg = f'CEP criado: {value}'
            else:
                msg = f'{data_type}: {value}'
            
            # Adiciona ao log
            self.generated_data_log.insert(0, msg)
            # Limita a 20 últimos itens
            self.generated_data_log = self.generated_data_log[:20]
            
            # Atualiza a window
            if '-GENERATED_LOG-' in self.window.AllKeysDict:
                self.window['-GENERATED_LOG-'].update('\n'.join(self.generated_data_log))
    
    def update_shortcuts_usage_log(self, shortcut_key: str):
        """Atualiza o log de atalhos utilizados"""
        if self.window:
            from datetime import datetime
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Mapeia teclas para nomes amigáveis
            shortcut_names = {
                'email': 'Email (Ctrl+Shift+E)',
                'cpf': 'CPF (Ctrl+Shift+C)',
                'cep': 'CEP (Ctrl+Shift+Z)'
            }
            
            name = shortcut_names.get(shortcut_key, shortcut_key)
            msg = f'[{timestamp}] {name}'
               
    def _on_shortcut_triggered(self, data_type: str, result: dict):
        """Callback quando um atalho global é acionado"""
        if data_type == 'email':
            if result.get('error'):
                self.update_output(f"Email: {result['error']}", 'error')
            else:
                self.update_output(f"Email copiado: {result['email']}", 'success')
                self.update_generated_log('email', result['email'])
                self.update_shortcuts_usage_log('email')
        
        elif data_type == 'cpf':
            if result.get('error'):
                self.update_output(f"CPF: {result['error']}", 'error')
            else:
                self.update_output(f"CPF copiado: {result['cpf']}", 'success')
                self.update_generated_log('cpf', result['cpf'])
                self.update_shortcuts_usage_log('cpf')
        
        elif data_type == 'cep':
            if result.get('error'):
                self.update_output(f"CEP: {result['error']}", 'error')
            else:
                self.update_output(f"CEP copiado: {result['cep']}", 'success')
                self.update_generated_log('cep', result['cep'])
                self.update_shortcuts_usage_log('cep')
    
    def _switch_page(self):
        """Alterna entre páginas (main/config) com visibilidade controlada"""
        if self.current_page == 'main':
            self.window['-PAGE_MAIN-'].update(visible=True)
            self.window['-PAGE_CONFIG-'].update(visible=False)
        elif self.current_page == 'config':
            self.window['-PAGE_MAIN-'].update(visible=False)
            self.window['-PAGE_CONFIG-'].update(visible=True)
    
    def run(self):
        """Executa a interface gráfica com tema moderno"""
        self.create_main_window()
        
        # Inicia monitoramento de atalhos globais por padrão
        try:
            self.shortcut_manager.start_monitoring()
            self.window['-GLOBAL_HOTKEYS-'].update(value=True)
            self.window['-HOTKEY_STATUS-'].update(
                value='Ativado',
                text_color=COLORS['success']
            )
            self.window['-STATUS_INDICATOR-'].update(
                '●',
                text_color=COLORS['success']
            )
            self.update_output('Atalhos globais iniciados', 'success')
        except Exception as e:
            self.update_output(f'Atalhos globais indisponivel: {str(e)}', 'warning')
        
        while True:
            event, values = self.window.read(timeout=100)
            
            if event == sg.WINDOW_CLOSED or event == '-EXIT-' or event == '-CLOSE-':
                break
            
            # Minimizar janela
            if event == '-MINIMIZE-':
                try:
                    self.window.hide()
                    self.is_minimized = True
                except Exception as e:
                    self.update_output(f'Erro ao minimizar: {str(e)[:40]}', 'error')
            
            # Controlar atalhos globais
            if event == '-GLOBAL_HOTKEYS-':
                if values['-GLOBAL_HOTKEYS-']:
                    try:
                        self.shortcut_manager.start_monitoring()
                        self.window['-HOTKEY_STATUS-'].update(
                            value='Ativado',
                            text_color=COLORS['success']
                        )
                        self.window['-STATUS_INDICATOR-'].update(
                            '●',
                            text_color=COLORS['success']
                        )
                        self.update_output('Atalhos globais ativados', 'success')
                    except Exception as e:
                        self.window['-GLOBAL_HOTKEYS-'].update(value=False)
                        self.window['-HOTKEY_STATUS-'].update(
                            value=f'Erro: {str(e)[:30]}...',
                            text_color=COLORS['danger']
                        )
                        self.window['-STATUS_INDICATOR-'].update(
                            '●',
                            text_color=COLORS['danger']
                        )
                        self.update_output(f'Erro ao ativar atalhos: {str(e)}', 'error')
                else:
                    try:
                        self.shortcut_manager.stop_monitoring()
                        self.window['-HOTKEY_STATUS-'].update(
                            value='Desativado',
                            text_color=COLORS['warning']
                        )
                        self.window['-STATUS_INDICATOR-'].update(
                            '●',
                            text_color=COLORS['danger']
                        )
                        self.update_output('Atalhos globais desativados', 'warning')
                    except Exception as e:
                        self.update_output(f'Erro ao desativar atalhos: {str(e)}', 'error')
            
            # Toggle API Key visibility
            if event == '-TOGGLE_API_KEY-':
                try:
                    current_value = self.window['-APIKEY_MAIN-'].get()
                    if self.api_key_visible:
                        # Esconder a API key
                        self.window['-APIKEY_MAIN-'].update(
                            value=current_value,
                            password_char='*'
                        )
                        self.api_key_visible = False
                    else:
                        # Mostrar a API key
                        self.window['-APIKEY_MAIN-'].update(
                            value=current_value,
                            password_char=''
                        )
                        self.api_key_visible = True
                except Exception as e:
                    self.update_output(f'Erro ao alternar visibilidade: {str(e)[:40]}', 'error')
            
            # Abrir link do RapidAPI
            if event == '-OPEN_RAPIDAPI_LINK-':
                try:
                    webbrowser.open('https://www.rapidapi.com')
                except Exception as e:
                    self.update_output(f'Erro ao abrir link: {str(e)[:40]}', 'error')
            
            # Clique no texto do RapidAPI
            if event == '-RAPIDAPI_LINK-':
                try:
                    webbrowser.open('https://www.rapidapi.com')
                except Exception as e:
                    self.update_output(f'Erro ao abrir link: {str(e)[:40]}', 'error')
            
            # Atualizar API Key
            if event == '-UPDATE_API_KEY-':
                new_key = values['-APIKEY_MAIN-'].strip()
                try:
                    self.config_manager.set('api.rapidapi_key', new_key)
                    saved_key = self.config_manager.get('api.rapidapi_key', '')

                    # Reforça na UI o valor persistido no sistema.
                    self.window['-APIKEY_MAIN-'].update(saved_key)

                    # Mantém serviços em memória com a chave mais recente.
                    self.data_generator.update_api_key(saved_key)
                    self.shortcut_manager.update_api_key(saved_key)

                    if saved_key:
                        self.update_output('API Key atualizada com sucesso!', 'success')
                    else:
                        self.update_output('API Key removida com sucesso!', 'success')
                except Exception as e:
                    self.update_output(f'Erro ao atualizar API Key: {str(e)[:40]}', 'error')
            
            # Gerar Email
            if event == '-EMAIL-':
                result = self.data_generator.generate_temporary_email()
                if result['error']:
                    self.update_output(f'Erro ao gerar email: {result["error"]}', 'error')
                else:
                    email = result['email']
                    if self.clipboard_manager.copy_to_clipboard(email):
                        self.update_output(f'Email copiado: {email}', 'success')
                        self.update_generated_log('email', email)
                    else:
                        self.update_output(f'Erro ao copiar email', 'error')
            
            # Gerar CPF
            elif event == '-CPF-':
                cpf = self.data_generator.generate_cpf(formatted=True)
                if self.clipboard_manager.copy_to_clipboard(cpf):
                    self.update_output(f'CPF copiado: {cpf}', 'success')
                    self.update_generated_log('cpf', cpf)
                else:
                    self.update_output('Erro ao copiar CPF', 'error')
            
            # Gerar CEP
            elif event == '-CEP-':
                cep = self.data_generator.generate_cep(formatted=True)
                if self.clipboard_manager.copy_to_clipboard(cep):
                    self.update_output(f'CEP copiado: {cep}', 'success')
                    self.update_generated_log('cep', cep)
                else:
                    self.update_output('Erro ao copiar CEP', 'error')
            
            # Gerar Email via botão de atalho
            elif event == '-EMAIL_SHORTCUT-':
                result = self.data_generator.generate_temporary_email()
                if result['error']:
                    self.update_output(f'Erro ao gerar email: {result["error"]}', 'error')
                else:
                    email = result['email']
                    if self.clipboard_manager.copy_to_clipboard(email):
                        self.update_output(f'Email copiado: {email}', 'success')
                        self.update_generated_log('email', email)
                    else:
                        self.update_output(f'Erro ao copiar email', 'error')
            
            # Gerar CPF via botão de atalho
            elif event == '-CPF_SHORTCUT-':
                cpf = self.data_generator.generate_cpf(formatted=True)
                if self.clipboard_manager.copy_to_clipboard(cpf):
                    self.update_output(f'CPF copiado: {cpf}', 'success')
                    self.update_generated_log('cpf', cpf)
                else:
                    self.update_output('Erro ao copiar CPF', 'error')
            
            # Gerar CEP via botão de atalho
            elif event == '-CEP_SHORTCUT-':
                cep = self.data_generator.generate_cep(formatted=True)
                if self.clipboard_manager.copy_to_clipboard(cep):
                    self.update_output(f'CEP copiado: {cep}', 'success')
                    self.update_generated_log('cep', cep)
                else:
                    self.update_output('Erro ao copiar CEP', 'error')
            
            # Atualizar atalho de Email
            if event == '-UPDATE_EMAIL_SHORTCUT-':
                new_shortcut = values['-SHORTCUT_EMAIL_MAIN-'].strip()
                if new_shortcut:
                    try:
                        self.config_manager.set('shortcuts.email', new_shortcut)
                        self.shortcut_manager.update_api_key(self.config_manager.get("api.rapidapi_key"))
                        if self.shortcut_manager.is_monitoring():
                            self.shortcut_manager.stop_monitoring()
                            self.shortcut_manager.start_monitoring()
                        self.update_output(f'Atalho Email atualizado: {new_shortcut}', 'success')
                    except Exception as e:
                        self.update_output(f'Erro ao atualizar atalho: {str(e)[:40]}', 'error')
                else:
                    self.update_output('Atalho nao pode estar vazio', 'warning')
            
            # Atualizar atalho de CPF
            if event == '-UPDATE_CPF_SHORTCUT-':
                new_shortcut = values['-SHORTCUT_CPF_MAIN-'].strip()
                if new_shortcut:
                    try:
                        self.config_manager.set('shortcuts.cpf', new_shortcut)
                        self.shortcut_manager.update_api_key(self.config_manager.get("api.rapidapi_key"))
                        if self.shortcut_manager.is_monitoring():
                            self.shortcut_manager.stop_monitoring()
                            self.shortcut_manager.start_monitoring()
                        self.update_output(f'Atalho CPF atualizado: {new_shortcut}', 'success')
                    except Exception as e:
                        self.update_output(f'Erro ao atualizar atalho: {str(e)[:40]}', 'error')
                else:
                    self.update_output('Atalho nao pode estar vazio', 'warning')
            
            # Atualizar atalho de CEP
            if event == '-UPDATE_CEP_SHORTCUT-':
                new_shortcut = values['-SHORTCUT_CEP_MAIN-'].strip()
                if new_shortcut:
                    try:
                        self.config_manager.set('shortcuts.cep', new_shortcut)
                        self.shortcut_manager.update_api_key(self.config_manager.get("api.rapidapi_key"))
                        if self.shortcut_manager.is_monitoring():
                            self.shortcut_manager.stop_monitoring()
                            self.shortcut_manager.start_monitoring()
                        self.update_output(f'Atalho CEP atualizado: {new_shortcut}', 'success')
                    except Exception as e:
                        self.update_output(f'Erro ao atualizar atalho: {str(e)[:40]}', 'error')
                else:
                    self.update_output('Atalho nao pode estar vazio', 'warning')
            
            # Abrir configurações
            elif event == '-SETTINGS-':
                self.current_page = 'config'
                self._switch_page()
                self.update_output('Abrindo configuracoes', 'info')
            
            # Voltar da página de configurações
            elif event == '-CONFIG_BACK-':
                self.current_page = 'main'
                self._switch_page()
                self.update_output('Retornando a pagina principal', 'info')
            
            # Salvar configurações
            elif event == '-CONFIG_SAVE-':
                try:
                    self.config_manager.set('api.rapidapi_key', values['-APIKEY-'])
                    self.config_manager.set('shortcuts.email', values['-SHORTCUT_EMAIL-'])
                    self.config_manager.set('shortcuts.cpf', values['-SHORTCUT_CPF-'])
                    self.config_manager.set('shortcuts.cep', values['-SHORTCUT_CEP-'])
                    
                    # Atualiza o data generator com a nova chave
                    self.data_generator.update_api_key(values['-APIKEY-'])
                    self.shortcut_manager.update_api_key(values['-APIKEY-'])
                    
                    # Atualizar atalhos
                    if self.shortcut_manager.is_monitoring():
                        self.shortcut_manager.stop_monitoring()
                        self.shortcut_manager.start_monitoring()
                    
                    self.update_output('Configuracoes salvas com sucesso!', 'success')
                except Exception as e:
                    self.update_output(f'Erro ao salvar configuracoes: {str(e)[:50]}', 'error')
                    self.update_output(f'Erro ao recarregar atalhos: {str(e)}', 'warning')
        
        # Para o monitoramento ao sair
        try:
            self.shortcut_manager.stop_monitoring()
        except Exception as e:
            print(f"Erro ao parar monitoramento: {e}")
        
        self.window.close()
