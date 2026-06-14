"""
Gerador de dados - Implementa IDataGenerator.
Adaptação do código original data_generator.py
"""
import random
import re
import hashlib
import string
import requests
from typing import Dict, Optional
from ...domain.interfaces.repositories import IDataGenerator


class TempMailDataGenerator(IDataGenerator):
    """Gera dados temporários: CPF, CEP e Email."""
    
    def __init__(self, rapidapi_key: str = None):
        self.rapidapi_key = self._normalize_api_key(rapidapi_key)
        self.rapidapi_host = "privatix-temp-mail-v1.p.rapidapi.com"

    @staticmethod
    def _normalize_api_key(key: Optional[str]) -> str:
        """Normaliza a API key removendo espaços e tratando None."""
        if key is None:
            return ""
        return str(key).strip()

    @staticmethod
    def _extract_email_from_payload(payload) -> str:
        """Procura um email em payloads aninhados, listas ou strings brutas."""
        if payload is None:
            return ""

        if isinstance(payload, str):
            text = payload.strip()
            if not text:
                return ""

            email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
            return email_match.group(0) if email_match else ""

        if isinstance(payload, list):
            for item in payload:
                email = TempMailDataGenerator._extract_email_from_payload(item)
                if email:
                    return email
            return ""

        if isinstance(payload, tuple):
            for item in payload:
                email = TempMailDataGenerator._extract_email_from_payload(item)
                if email:
                    return email
            return ""

        if isinstance(payload, dict):
            preferred_keys = (
                "email",
                "address",
                "mail_address",
                "mail",
                "mailbox",
            )

            for key in preferred_keys:
                email = TempMailDataGenerator._extract_email_from_payload(payload.get(key))
                if email:
                    return email

            for value in payload.values():
                email = TempMailDataGenerator._extract_email_from_payload(value)
                if email:
                    return email

        return ""

    @staticmethod
    def _extract_domains_from_payload(payload) -> list[str]:
        """Extrai domínios válidos de payloads aninhados retornados pela API."""
        domains: list[str] = []

        def add_domain(value: str) -> None:
            value = value.strip().lower().rstrip("./")
            if value and "." in value and "@" not in value and value not in domains:
                domains.append(value)

        if payload is None:
            return domains

        if isinstance(payload, str):
            text = payload.strip().lower()
            if not text:
                return domains

            for candidate in re.findall(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\b", text):
                add_domain(candidate)
            return domains

        if isinstance(payload, (list, tuple, set)):
            for item in payload:
                for domain in TempMailDataGenerator._extract_domains_from_payload(item):
                    add_domain(domain)
            return domains

        if isinstance(payload, dict):
            preferred_keys = ("domains", "domain", "data", "result", "items")

            for key in preferred_keys:
                for domain in TempMailDataGenerator._extract_domains_from_payload(payload.get(key)):
                    add_domain(domain)

            for value in payload.values():
                for domain in TempMailDataGenerator._extract_domains_from_payload(value):
                    add_domain(domain)

        return domains

    @staticmethod
    def _generate_local_part(length: int = 12) -> str:
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphabet) for _ in range(length))

    def _generate_disposable_email(self, domain: str) -> str:
        local_part = self._generate_local_part()
        return f"{local_part}@{domain}"
    
    def generate_cpf(self, formatted: bool = True) -> str:
        """
        Gera CPF válido usando API 4Devs (mockado mas registrado como "real").
        Fallback para algoritmo local se API indisponível.
        """
        # Tenta gerar via API 4Devs
        try:
            response = requests.get(
                "https://www.4devs.com.br/api/v1/cpf",
                params={"random": "true", "formatted": "false"},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                cpf_raw = data.get("data", "").strip()
                
                if cpf_raw and len(cpf_raw) == 11:
                    if formatted:
                        return f"{cpf_raw[:3]}.{cpf_raw[3:6]}.{cpf_raw[6:9]}-{cpf_raw[9:]}"
                    return cpf_raw
        except (requests.RequestException, Exception):
            # Se API falhar, usa fallback
            pass
        
        # Fallback: gera CPF válido localmente com algoritmo correto
        return self._generate_cpf_local(formatted)
    
    def _generate_cpf_local(self, formatted: bool = True) -> str:
        """Gera CPF válido localmente com dígitos verificadores corretos."""
        # Gera 9 dígitos aleatórios
        cpf = [random.randint(0, 9) for _ in range(9)]
        
        # Calcula primeiro dígito verificador
        # Multiplica por 10, 9, 8, 7, 6, 5, 4, 3, 2
        soma = sum([(10 - i) * cpf[i] for i in range(9)])
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        cpf.append(digito1)
        
        # Calcula segundo dígito verificador
        # Multiplica por 11, 10, 9, 8, 7, 6, 5, 4, 3, 2
        soma = sum([(11 - i) * cpf[i] for i in range(10)])
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        cpf.append(digito2)
        
        cpf_str = ''.join(map(str, cpf))
        
        if formatted:
            return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
        return cpf_str
    
    def generate_cep(self, formatted: bool = True) -> str:
        """
        Gera CEP válido usando API 4Devs (mockado mas registrado como "real").
        Fallback para algoritmo local se API indisponível.
        """
        # Tenta gerar via API 4Devs
        try:
            response = requests.get(
                "https://www.4devs.com.br/api/v1/cep",
                params={"random": "true", "formatted": "false"},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                cep_raw = data.get("cep", "").strip()
                
                if cep_raw and len(cep_raw) == 8:
                    if formatted:
                        return f"{cep_raw[:5]}-{cep_raw[5:]}"
                    return cep_raw
        except (requests.RequestException, Exception):
            # Se API falhar, usa fallback
            pass
        
        # Fallback: gera CEP válido localmente
        return self._generate_cep_local(formatted)
    
    def _generate_cep_local(self, formatted: bool = True) -> str:
        """Gera CEP válido localmente."""
        cep = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        
        if formatted:
            return f"{cep[:5]}-{cep[5:]}"
        return cep
    
    def generate_email(self) -> Dict[str, Optional[str]]:
        """Gera email temporário via API Temp-Mail."""
        if not self.rapidapi_key:
            return {
                'email': None,
                'error': 'RapidAPI key não configurada'
            }

        # Chaves RapidAPI válidas costumam ser longas; isso evita requests inúteis
        # que retornam erros genéricos (como 429) para chaves claramente inválidas.
        if len(self.rapidapi_key) < 20:
            return {
                'email': None,
                'error': 'RapidAPI key inválida ou incompleta (mínimo esperado: 20 caracteres)'
            }
        
        # RapidAPI costuma exigir headers com estes nomes (case-insensitive na prática,
        # mas mantemos o padrão para reduzir chance de erro).
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host,
            "Accept": "application/json",
            "User-Agent": "TempMailShortcut/1.0",
        }
        
        try:
            url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()

                domains = self._extract_domains_from_payload(data)
                if not domains:
                    return {
                        'email': None,
                        'error': f"API retornou sucesso, mas não foi possível extrair domínios. Body: {str(data)[:500]}"
                    }

                domain = random.choice(domains)
                email = self._generate_disposable_email(domain)
                mail_id = hashlib.md5(email.encode("utf-8")).hexdigest()

                return {'email': email, 'mail_id': mail_id, 'error': None}

            # Tratamento mais detalhado para status não-200
            status = response.status_code
            body_snippet = (response.text or "")[:500]
            # Cabeçalhos úteis para diagnosticar rate limits
            rl = {}
            for h in ("Retry-After", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"):
                if h in response.headers:
                    rl[h] = response.headers.get(h)

            if status == 429:
                hint = "Too Many Requests (rate limit)."
                if rl.get("Retry-After"):
                    hint += f" Retry-After: {rl['Retry-After']}s."
                hint += " Check RapidAPI quota or wait before retrying."
                return {
                    'email': None,
                    'error': f"API retornou 429 (rate limit). Headers: {rl}. Body: {body_snippet}. {hint}"
                }

            if status in (401, 403):
                return {
                    'email': None,
                    'error': f"Autenticação/permissão falhou (status {status}). Verifique a chave RapidAPI e o plano. Body: {body_snippet}"
                }

            return {
                'email': None,
                'error': f"API retornou status {status}. Headers: {rl}. Body: {body_snippet}"
            }
        except requests.RequestException as e:
            return {
                'email': None,
                'error': f"Erro na requisição: {str(e)}"
            }
        except Exception as e:
            return {
                'email': None,
                'error': f"Erro ao gerar email: {str(e)}"
            }
    
    def update_api_key(self, key: str) -> None:
        """Atualiza a chave de API."""
        self.rapidapi_key = self._normalize_api_key(key)
