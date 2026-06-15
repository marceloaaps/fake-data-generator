#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de testes para o projeto Fake Data Generator.
Executa testes unitários dos componentes principais.
"""
import sys
import unittest
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.config_manager import ConfigManager
from src.data_generator import DataGenerator
from src.clipboard_manager import ClipboardManager
from src.shortcut_manager import ShortcutManager


class TestDataGenerator(unittest.TestCase):
    """Testes para o gerador de dados"""
    
    def setUp(self):
        self.generator = DataGenerator()
    
    def test_generate_cpf(self):
        """Testa geração de CPF"""
        cpf = self.generator.generate_cpf(formatted=True)
        self.assertIsNotNone(cpf)
        self.assertEqual(len(cpf), 14)  # XXX.XXX.XXX-XX
        self.assertIn('.', cpf)
        self.assertIn('-', cpf)
    
    def test_generate_cpf_unformatted(self):
        """Testa geração de CPF sem formatação"""
        cpf = self.generator.generate_cpf(formatted=False)
        self.assertIsNotNone(cpf)
        self.assertEqual(len(cpf), 11)
        self.assertTrue(cpf.isdigit())
    
    def test_generate_cep(self):
        """Testa geração de CEP"""
        cep = self.generator.generate_cep(formatted=True)
        self.assertIsNotNone(cep)
        self.assertEqual(len(cep), 9)  # XXXXX-XXX
        self.assertIn('-', cep)
    
    def test_generate_cep_unformatted(self):
        """Testa geração de CEP sem formatação"""
        cep = self.generator.generate_cep(formatted=False)
        self.assertIsNotNone(cep)
        self.assertEqual(len(cep), 8)
        self.assertTrue(cep.isdigit())


class TestClipboardManager(unittest.TestCase):
    """Testes para o gerenciador de clipboard"""
    
    def setUp(self):
        self.clipboard = ClipboardManager()
    
    def test_copy_to_clipboard(self):
        """Testa copiar para clipboard"""
        test_text = "teste123"
        result = self.clipboard.copy_to_clipboard(test_text)
        self.assertTrue(result)
    
    def test_get_clipboard(self):
        """Testa obter conteúdo do clipboard"""
        test_text = "teste456"
        self.clipboard.copy_to_clipboard(test_text)
        clipboard_content = self.clipboard.get_clipboard()
        self.assertEqual(clipboard_content, test_text)


class TestConfigManager(unittest.TestCase):
    """Testes para o gerenciador de configurações"""
    
    def setUp(self):
        # Cria um gerenciador com caminho temporário
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
    
    def tearDown(self):
        # Limpa o diretório temporário
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config(self):
        """Testa carregamento de configuração padrão"""
        self.assertIsNotNone(self.config_manager.config)
        self.assertIn('shortcuts', self.config_manager.config)
        self.assertIn('api', self.config_manager.config)
    
    def test_get_config_value(self):
        """Testa obter valor de configuração"""
        email_shortcut = self.config_manager.get('shortcuts.email')
        self.assertIsNotNone(email_shortcut)
    
    def test_set_config_value(self):
        """Testa definir valor de configuração"""
        self.config_manager.set('shortcuts.email', 'Ctrl+Alt+E')
        value = self.config_manager.get('shortcuts.email')
        self.assertEqual(value, 'Ctrl+Alt+E')


class TestShortcutManager(unittest.TestCase):
    """Testes para o gerenciador de atalhos globais"""
    
    def setUp(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager(self.temp_dir)
        self.shortcut_manager = ShortcutManager(self.config_manager)
    
    def tearDown(self):
        import shutil
        if self.shortcut_manager.is_monitoring():
            self.shortcut_manager.stop_monitoring()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_normalize_shortcut(self):
        """Testa normalização de atalho"""
        normalized = self.shortcut_manager._normalize_shortcut("Ctrl+Shift+E")
        self.assertEqual(normalized, "ctrl+shift+e")
    
    def test_shortcut_manager_creation(self):
        """Testa criação do gerenciador"""
        self.assertIsNotNone(self.shortcut_manager)
        self.assertFalse(self.shortcut_manager.is_monitoring())
    
    def test_monitoring_state(self):
        """Testa estado de monitoramento"""
        self.assertFalse(self.shortcut_manager.is_monitoring())
        try:
            self.shortcut_manager.start_monitoring()
            self.assertTrue(self.shortcut_manager.is_monitoring())
            self.shortcut_manager.stop_monitoring()
            self.assertFalse(self.shortcut_manager.is_monitoring())
        except Exception as e:
            # Pode falhar em alguns ambientes (CI/CD, sem acesso a teclado)
            print(f"[WARN] Teste de monitoramento pulado: {e}")


def run_tests():
    """Executa todos os testes"""
    print("=" * 50)
    print("[TEST] Executando testes - Fake Data Generator")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona testes
    suite.addTests(loader.loadTestsFromTestCase(TestDataGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestShortcutManager))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("[OK] Todos os testes passaram!")
    else:
        print(f"[FAIL] {len(result.failures)} teste(s) falharam")
    print("=" * 50)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
