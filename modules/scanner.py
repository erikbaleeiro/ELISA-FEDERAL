#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ELISA-FEDERAL - Módulo Scanner de Vulnerabilidades
Sistema de análise de segurança para recursos públicos
"""

import requests
import ssl
import socket
from urllib.parse import urlparse, urljoin
from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

class VulnerabilityScanner:
    """
    🛡️ Scanner de vulnerabilidades para análise de segurança
    Foco em detecção de problemas comuns em aplicações web públicas
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ELISA-FEDERAL/1.0 (Security Scanner; +https://github.com/erikbaleeiro/ELISA-FEDERAL)'
        })
        self.timeout = 10

    def scan(self, url: str, scan_type: str = "basic") -> dict:
        """
        Executa scan de segurança na URL fornecida

        Args:
            url (str): URL para análise
            scan_type (str): Tipo de scan (basic, full, quick)

        Returns:
            dict: Resultados da análise
        """
        console.print(f"🔍 [blue]Iniciando scan {scan_type} em: {url}[/blue]")

        results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'scan_type': scan_type,
            'ssl_analysis': {},
            'headers_analysis': {},
            'content_analysis': {},
            'vulnerabilities': [],
            'score': 0
        }

        try:
            # Análise SSL/TLS
            results['ssl_analysis'] = self._analyze_ssl(url)

            # Análise de Headers HTTP
            results['headers_analysis'] = self._analyze_headers(url)

            # Análise de conteúdo (apenas para scan full)
            if scan_type in ['full', 'basic']:
                results['content_analysis'] = self._analyze_content(url)

            # Verificações específicas por tipo de scan
            if scan_type == 'full':
                results['directory_analysis'] = self._analyze_directories(url)
                results['form_analysis'] = self._analyze_forms(url)

            # Calcular score de segurança
            results['score'] = self._calculate_security_score(results)

            console.print(f"✅ [green]Scan concluído. Score: {results['score']}/100[/green]")

        except Exception as e:
            console.print(f"❌ [red]Erro durante scan: {str(e)}[/red]")
            results['error'] = str(e)

        return results

    def _analyze_ssl(self, url: str) -> dict:
        """Analisa configuração SSL/TLS"""
        console.print("🔒 Analisando SSL/TLS...")

        ssl_results = {
            'status': 'UNKNOWN',
            'certificate_valid': False,
            'protocol_version': None,
            'cipher_suite': None,
            'expiry_date': None,
            'issues': []
        }

        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme != 'https':
                ssl_results['status'] = 'NO_SSL'
                ssl_results['issues'].append('Site não usa HTTPS')
                return ssl_results

            hostname = parsed_url.hostname
            port = parsed_url.port or 443

            # Verificar certificado SSL
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_results['certificate_valid'] = True
                    ssl_results['protocol_version'] = ssock.version()
                    ssl_results['cipher_suite'] = ssock.cipher()

                    # Data de expiração
                    if cert and 'notAfter' in cert:
                        ssl_results['expiry_date'] = cert['notAfter']

            ssl_results['status'] = 'OK'

        except ssl.SSLError as e:
            ssl_results['status'] = 'SSL_ERROR'
            ssl_results['issues'].append(f'Erro SSL: {str(e)}')
        except Exception as e:
            ssl_results['status'] = 'ERROR'
            ssl_results['issues'].append(f'Erro de conexão: {str(e)}')

        return ssl_results

    def _analyze_headers(self, url: str) -> dict:
        """Analisa headers de segurança HTTP"""
        console.print("📋 Analisando headers de segurança...")

        headers_results = {
            'status': 'UNKNOWN',
            'security_headers': {},
            'missing_headers': [],
            'recommendations': []
        }

        # Headers de segurança importantes
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': None,
            'Content-Security-Policy': None,
            'Referrer-Policy': None,
            'Permissions-Policy': None
        }

        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)

            for header, expected in security_headers.items():
                value = response.headers.get(header)
                headers_results['security_headers'][header] = value

                if not value:
                    headers_results['missing_headers'].append(header)
                    headers_results['recommendations'].append(
                        f'Adicionar header {header} para melhor segurança'
                    )

            # Verificar headers perigosos
            dangerous_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in dangerous_headers:
                if response.headers.get(header):
                    headers_results['recommendations'].append(
                        f'Remover/ocultar header {header} para reduzir exposição'
                    )

            headers_results['status'] = 'OK'

        except Exception as e:
            headers_results['status'] = 'ERROR'
            headers_results['error'] = str(e)

        return headers_results

    def _analyze_content(self, url: str) -> dict:
        """Analisa conteúdo da página para problemas de segurança"""
        console.print("📄 Analisando conteúdo...")

        content_results = {
            'status': 'UNKNOWN',
            'technologies': [],
            'sensitive_info': [],
            'external_resources': [],
            'forms': [],
            'links': []
        }

        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Detectar tecnologias
            content_results['technologies'] = self._detect_technologies(response, soup)

            # Buscar informações sensíveis expostas
            content_results['sensitive_info'] = self._find_sensitive_info(response.text)

            # Analisar recursos externos
            content_results['external_resources'] = self._analyze_external_resources(soup, url)

            # Analisar formulários
            content_results['forms'] = self._analyze_page_forms(soup)

            content_results['status'] = 'OK'

        except Exception as e:
            content_results['status'] = 'ERROR'
            content_results['error'] = str(e)

        return content_results

    def _detect_technologies(self, response, soup) -> list:
        """Detecta tecnologias utilizadas"""
        technologies = []

        # Headers reveladores
        tech_headers = {
            'Server': 'Web Server',
            'X-Powered-By': 'Framework',
            'X-AspNet-Version': 'ASP.NET',
            'X-Generator': 'CMS'
        }

        for header, tech_type in tech_headers.items():
            value = response.headers.get(header)
            if value:
                technologies.append({
                    'type': tech_type,
                    'name': value,
                    'source': f'Header: {header}'
                })

        # Meta tags reveladores
        generator = soup.find('meta', {'name': 'generator'})
        if generator and generator.get('content'):
            technologies.append({
                'type': 'CMS/Framework',
                'name': generator.get('content'),
                'source': 'Meta tag'
            })

        return technologies

    def _find_sensitive_info(self, content: str) -> list:
        """Busca informações sensíveis expostas"""
        sensitive_patterns = {
            'Email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'CPF': r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b',
            'CNPJ': r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b',
            'Telefone': r'\b\(?[\d\s\-\+\(\)]{10,}\b',
            'API Key': r'[Aa][Pp][Ii][-_\s]*[Kk][Ee][Yy][-_\s]*[:=]\s*[\'"]?[\w\-]{16,}[\'"]?',
            'Token': r'[Tt][Oo][Kk][Ee][Nn][-_\s]*[:=]\s*[\'"]?[\w\-]{16,}[\'"]?'
        }

        sensitive_info = []
        for info_type, pattern in sensitive_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                sensitive_info.append({
                    'type': info_type,
                    'count': len(matches),
                    'samples': matches[:3]  # Apenas 3 exemplos
                })

        return sensitive_info

    def _analyze_external_resources(self, soup, base_url: str) -> list:
        """Analisa recursos externos carregados"""
        external_resources = []
        base_domain = urlparse(base_url).netloc

        # Scripts externos
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('/') and base_domain not in src:
                external_resources.append({
                    'type': 'script',
                    'url': src,
                    'risk': 'MEDIUM'
                })

        # CSS externos
        for link in soup.find_all('link', href=True):
            if link.get('rel') and 'stylesheet' in link.get('rel'):
                href = link.get('href')
                if href and not href.startswith('/') and base_domain not in href:
                    external_resources.append({
                        'type': 'stylesheet',
                        'url': href,
                        'risk': 'LOW'
                    })

        return external_resources

    def _analyze_page_forms(self, soup) -> list:
        """Analisa formulários da página"""
        forms_analysis = []

        for form in soup.find_all('form'):
            form_data = {
                'method': form.get('method', 'GET').upper(),
                'action': form.get('action', ''),
                'inputs': [],
                'security_issues': []
            }

            # Analisar inputs
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_type = input_tag.get('type', 'text')
                input_name = input_tag.get('name', '')

                form_data['inputs'].append({
                    'type': input_type,
                    'name': input_name
                })

                # Verificar campos sensíveis sem HTTPS
                if input_type in ['password', 'email'] and 'https' not in form.get('action', ''):
                    form_data['security_issues'].append(
                        f'Campo {input_type} sem HTTPS'
                    )

            forms_analysis.append(form_data)

        return forms_analysis

    def _analyze_directories(self, url: str) -> dict:
        """Analisa diretórios comuns (apenas para scan full)"""
        console.print("📁 Verificando diretórios comuns...")

        common_dirs = [
            'admin', 'administrator', 'wp-admin', 'phpmyadmin',
            'backup', 'backups', 'test', 'tests', 'dev',
            '.git', '.svn', 'config', 'database'
        ]

        found_dirs = []
        for directory in common_dirs:
            test_url = urljoin(url, directory)
            try:
                response = self.session.head(test_url, timeout=5)
                if response.status_code not in [404, 403]:
                    found_dirs.append({
                        'path': directory,
                        'status_code': response.status_code,
                        'risk': 'HIGH' if directory in ['admin', '.git', 'config'] else 'MEDIUM'
                    })
            except:
                continue

        return {
            'status': 'OK',
            'accessible_directories': found_dirs
        }

    def _analyze_forms(self, url: str) -> dict:
        """Análise detalhada de formulários"""
        console.print("📝 Analisando formulários...")

        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')

            forms = []
            for form in soup.find_all('form'):
                form_analysis = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET').upper(),
                    'has_csrf_token': bool(form.find('input', {'name': re.compile(r'csrf|token', re.I)})),
                    'password_fields': len(form.find_all('input', {'type': 'password'})),
                    'security_score': 0
                }

                # Calcular score de segurança do formulário
                if form_analysis['has_csrf_token']:
                    form_analysis['security_score'] += 30
                if form_analysis['method'] == 'POST':
                    form_analysis['security_score'] += 20
                if 'https' in url:
                    form_analysis['security_score'] += 30

                forms.append(form_analysis)

            return {
                'status': 'OK',
                'forms_found': len(forms),
                'forms_details': forms
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e)
            }

    def _calculate_security_score(self, results: dict) -> int:
        """Calcula score de segurança geral (0-100)"""
        score = 100

        # Penalidades SSL
        ssl_analysis = results.get('ssl_analysis', {})
        if ssl_analysis.get('status') == 'NO_SSL':
            score -= 30
        elif ssl_analysis.get('status') != 'OK':
            score -= 20

        # Penalidades Headers
        headers_analysis = results.get('headers_analysis', {})
        missing_headers = len(headers_analysis.get('missing_headers', []))
        score -= min(missing_headers * 5, 25)  # Máximo 25 pontos

        # Penalidades por informações sensíveis
        content_analysis = results.get('content_analysis', {})
        sensitive_info = content_analysis.get('sensitive_info', [])
        if sensitive_info:
            score -= min(len(sensitive_info) * 10, 20)  # Máximo 20 pontos

        # Penalidades por diretórios expostos
        directory_analysis = results.get('directory_analysis', {})
        accessible_dirs = directory_analysis.get('accessible_directories', [])
        high_risk_dirs = [d for d in accessible_dirs if d.get('risk') == 'HIGH']
        score -= len(high_risk_dirs) * 15

        return max(score, 0)  # Não permitir score negativo