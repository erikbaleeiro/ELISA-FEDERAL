#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👁️ ELISA-FEDERAL - Módulo Monitor de Segurança
Sistema de monitoramento contínuo de recursos públicos
"""

import time
import asyncio
import aiohttp
import hashlib
from datetime import datetime
from typing import List, Callable, Dict
from rich.console import Console

console = Console()

class SecurityMonitor:
    """
    👁️ Monitor de segurança para vigilância contínua
    Monitora mudanças em sites e APIs públicas
    """

    def __init__(self):
        self.monitoring = False
        self.targets = []
        self.baseline_hashes = {}
        self.last_check = {}

    def start_monitoring(self, targets: List[str], interval: int, callback: Callable):
        """
        Inicia monitoramento contínuo dos alvos

        Args:
            targets: Lista de URLs para monitorar
            interval: Intervalo entre verificações (segundos)
            callback: Função chamada quando mudanças são detectadas
        """
        self.targets = targets
        self.monitoring = True

        console.print(f"👁️ [blue]Iniciando monitoramento de {len(targets)} alvos[/blue]")

        # Estabelecer baseline inicial
        self._establish_baseline()

        # Loop de monitoramento
        try:
            while self.monitoring:
                self._check_all_targets(callback)
                time.sleep(interval)

        except KeyboardInterrupt:
            self.monitoring = False
            console.print("\n🛑 [yellow]Monitoramento interrompido[/yellow]")

    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        console.print("🛑 [red]Monitoramento parado[/red]")

    def _establish_baseline(self):
        """Estabelece baseline inicial para comparação"""
        console.print("📊 Estabelecendo baseline inicial...")

        for target in self.targets:
            try:
                baseline = self._get_target_signature(target)
                self.baseline_hashes[target] = baseline
                self.last_check[target] = datetime.now()
                console.print(f"✅ [green]Baseline estabelecido para: {target}[/green]")

            except Exception as e:
                console.print(f"❌ [red]Erro ao estabelecer baseline para {target}: {e}[/red]")
                self.baseline_hashes[target] = None

    def _check_all_targets(self, callback: Callable):
        """Verifica todos os alvos por mudanças"""
        for target in self.targets:
            try:
                status = self._check_target_changes(target)
                callback(target, status)
                self.last_check[target] = datetime.now()

            except Exception as e:
                error_status = {
                    'status': 'ERROR',
                    'error': str(e),
                    'changed': False,
                    'timestamp': datetime.now().isoformat()
                }
                callback(target, error_status)

    def _check_target_changes(self, target: str) -> Dict:
        """
        Verifica mudanças em um alvo específico

        Returns:
            Dict com status da verificação
        """
        try:
            current_signature = self._get_target_signature(target)
            baseline = self.baseline_hashes.get(target)

            if baseline is None:
                return {
                    'status': 'NO_BASELINE',
                    'changed': False,
                    'timestamp': datetime.now().isoformat()
                }

            changed = current_signature != baseline

            status = {
                'status': 'OK',
                'changed': changed,
                'timestamp': datetime.now().isoformat(),
                'current_hash': current_signature,
                'baseline_hash': baseline
            }

            if changed:
                status['change_detected'] = True
                # Atualizar baseline com nova assinatura
                self.baseline_hashes[target] = current_signature

                # Detectar tipo de mudança
                change_details = self._analyze_changes(target, baseline, current_signature)
                status.update(change_details)

            return status

        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'changed': False,
                'timestamp': datetime.now().isoformat()
            }

    def _get_target_signature(self, target: str) -> str:
        """
        Gera assinatura única do alvo para detectar mudanças

        Returns:
            String hash representando o estado atual
        """
        import requests

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'ELISA-FEDERAL-Monitor/1.0'
        })

        try:
            response = session.get(target, timeout=10, allow_redirects=True)

            # Combinar diferentes aspectos para criar assinatura
            signature_components = [
                str(response.status_code),
                str(len(response.content)),
                response.headers.get('Content-Type', ''),
                response.headers.get('Last-Modified', ''),
                response.headers.get('ETag', ''),
            ]

            # Para HTML, incluir hash do conteúdo processado
            if 'text/html' in response.headers.get('Content-Type', ''):
                # Extrair apenas texto relevante, ignorando timestamps dinâmicos
                content_hash = self._get_content_hash(response.text)
                signature_components.append(content_hash)
            else:
                # Para outros tipos, usar hash do conteúdo completo
                content_hash = hashlib.md5(response.content).hexdigest()
                signature_components.append(content_hash)

            # Criar hash final da assinatura
            signature_string = '|'.join(signature_components)
            return hashlib.sha256(signature_string.encode()).hexdigest()

        except Exception as e:
            raise Exception(f"Erro ao obter assinatura de {target}: {e}")

    def _get_content_hash(self, html_content: str) -> str:
        """
        Gera hash do conteúdo HTML ignorando elementos dinâmicos
        """
        from bs4 import BeautifulSoup
        import re

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remover elementos que mudam frequentemente
            for element in soup.find_all(['script', 'style']):
                element.decompose()

            # Remover comentários
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()

            # Extrair apenas texto estrutural
            text_content = soup.get_text(separator=' ', strip=True)

            # Normalizar espaços e quebras
            normalized = re.sub(r'\s+', ' ', text_content)

            # Remover timestamps e datas comuns
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
                r'\d{4}-\d{2}-\d{2}',      # YYYY-MM-DD
                r'\d{1,2}:\d{2}:\d{2}',    # HH:MM:SS
            ]

            for pattern in date_patterns:
                normalized = re.sub(pattern, '[DATE]', normalized)

            return hashlib.md5(normalized.encode()).hexdigest()

        except Exception:
            # Se falhar, usar hash simples do conteúdo
            return hashlib.md5(html_content.encode()).hexdigest()

    def _analyze_changes(self, target: str, old_hash: str, new_hash: str) -> Dict:
        """
        Analisa detalhes das mudanças detectadas
        """
        import requests

        try:
            # Fazer nova requisição para análise detalhada
            response = requests.get(target, timeout=10)

            analysis = {
                'change_type': 'CONTENT_MODIFIED',
                'severity': 'INFO',
                'details': []
            }

            # Verificar se é mudança no status code
            if response.status_code != 200:
                analysis['change_type'] = 'STATUS_CHANGED'
                analysis['severity'] = 'HIGH'
                analysis['details'].append(f'Status code: {response.status_code}')

            # Verificar headers de segurança
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'Content-Security-Policy',
                'Strict-Transport-Security'
            ]

            missing_headers = []
            for header in security_headers:
                if not response.headers.get(header):
                    missing_headers.append(header)

            if missing_headers:
                analysis['details'].append(f'Headers ausentes: {", ".join(missing_headers)}')
                analysis['severity'] = 'MEDIUM'

            # Verificar mudanças de certificado (para HTTPS)
            if target.startswith('https://'):
                cert_changes = self._check_certificate_changes(target)
                if cert_changes:
                    analysis['details'].extend(cert_changes)
                    analysis['severity'] = 'HIGH'

            return analysis

        except Exception as e:
            return {
                'change_type': 'ANALYSIS_ERROR',
                'severity': 'LOW',
                'details': [f'Erro na análise: {str(e)}']
            }

    def _check_certificate_changes(self, target: str) -> List[str]:
        """
        Verifica mudanças no certificado SSL
        """
        import ssl
        import socket
        from urllib.parse import urlparse

        changes = []

        try:
            parsed_url = urlparse(target)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443

            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Verificar data de expiração
                    if cert and 'notAfter' in cert:
                        expiry = cert['notAfter']
                        # Converter e verificar se está próximo do vencimento
                        from datetime import datetime
                        expiry_date = datetime.strptime(expiry, '%b %d %H:%M:%S %Y %Z')
                        days_to_expiry = (expiry_date - datetime.now()).days

                        if days_to_expiry < 30:
                            changes.append(f'Certificado expira em {days_to_expiry} dias')

                    # Verificar emissor
                    if cert and 'issuer' in cert:
                        issuer = dict(cert['issuer'])
                        if 'self-signed' in str(issuer).lower():
                            changes.append('Certificado auto-assinado detectado')

        except Exception:
            # Ignorar erros de certificado para esta análise
            pass

        return changes

    async def async_monitor(self, targets: List[str], interval: int, callback: Callable):
        """
        Versão assíncrona do monitoramento (para melhor performance)
        """
        console.print(f"⚡ [blue]Iniciando monitoramento assíncrono de {len(targets)} alvos[/blue]")

        async with aiohttp.ClientSession() as session:
            while self.monitoring:
                tasks = []
                for target in targets:
                    task = self._async_check_target(session, target, callback)
                    tasks.append(task)

                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(interval)

    async def _async_check_target(self, session: aiohttp.ClientSession, target: str, callback: Callable):
        """
        Verificação assíncrona de um alvo
        """
        try:
            async with session.get(target, timeout=10) as response:
                status = {
                    'status': 'OK',
                    'status_code': response.status,
                    'content_length': response.headers.get('Content-Length', 'Unknown'),
                    'timestamp': datetime.now().isoformat(),
                    'changed': False  # Implementar lógica de comparação
                }

                callback(target, status)

        except Exception as e:
            error_status = {
                'status': 'ERROR',
                'error': str(e),
                'changed': False,
                'timestamp': datetime.now().isoformat()
            }
            callback(target, error_status)