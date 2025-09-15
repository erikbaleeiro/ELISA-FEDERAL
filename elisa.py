#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ ELISA-FEDERAL - Extended Linguistic Intelligence for Security Analysis
🇧🇷 Sistema Brasileiro de Análise de Segurança Digital

Versão: 1.0.0
Autor: Erik Baleeiro
Licença: MIT
GitHub: https://github.com/erikbaleeiro/ELISA-FEDERAL

⚖️ AVISO LEGAL:
Esta ferramenta é destinada EXCLUSIVAMENTE para análise de segurança em recursos
PÚBLICOS com autorização. O uso inadequado é de responsabilidade do usuário.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Console rico para output bonito
console = Console()

# Importar módulos do ELISA
try:
    from modules.scanner import VulnerabilityScanner
    from modules.monitor import SecurityMonitor
    from modules.reporter import ReportGenerator
except ImportError as e:
    console.print(f"❌ [red]Erro ao importar módulos: {e}[/red]")
    console.print("💡 [yellow]Execute: pip install -r requirements.txt[/yellow]")
    sys.exit(1)

class ElisaFederal:
    """
    🛡️ Classe principal do sistema ELISA-FEDERAL
    Sistema de análise de segurança digital brasileiro
    """

    def __init__(self):
        self.version = "1.0.0"
        self.scanner = VulnerabilityScanner()
        self.monitor = SecurityMonitor()
        self.reporter = ReportGenerator()

        # Criar diretórios necessários
        self._create_directories()

        # Banner de apresentação
        self._show_banner()

    def _create_directories(self):
        """Cria diretórios necessários para operação"""
        directories = ['logs', 'reports', 'cache', 'temp']

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _show_banner(self):
        """Exibe banner de apresentação do sistema"""
        banner = f"""
🛡️ ELISA-FEDERAL v{self.version}
Extended Linguistic Intelligence for Security Analysis

🇧🇷 Sistema Brasileiro de Análise de Segurança Digital
⚖️ Uso exclusivo para análise de recursos PÚBLICOS autorizados
        """

        console.print(Panel(banner, style="bold blue"))

    def _log_action(self, action: str, details: str = ""):
        """Registra ações do sistema em log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}"

        if details:
            log_entry += f" - {details}"

        # Salvar em arquivo de log
        with open("logs/elisa.log", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

        # Exibir no console
        console.print(f"📝 [dim]{log_entry}[/dim]")

    def scan_target(self, target_url: str, scan_type: str = "basic"):
        """
        Executa scan de segurança em um alvo

        Args:
            target_url (str): URL do alvo para análise
            scan_type (str): Tipo de scan (basic, full, quick)
        """
        console.print(f"\n🎯 [bold]Iniciando análise de: {target_url}[/bold]")

        self._log_action("SCAN_INITIATED", f"Target: {target_url}, Type: {scan_type}")

        try:
            # Executar scan usando o módulo scanner
            results = self.scanner.scan(target_url, scan_type)

            # Exibir resultados
            self._display_scan_results(results)

            # Gerar relatório
            report_path = self.reporter.generate_report(results, target_url)

            console.print(f"\n📄 [green]Relatório salvo em: {report_path}[/green]")

            self._log_action("SCAN_COMPLETED", f"Target: {target_url}")

            return results

        except Exception as e:
            error_msg = f"Erro durante scan: {str(e)}"
            console.print(f"❌ [red]{error_msg}[/red]")
            self._log_action("SCAN_ERROR", error_msg)
            return None

    def _display_scan_results(self, results: dict):
        """Exibe resultados do scan em formato tabular"""

        # Tabela de resumo
        summary_table = Table(title="📊 Resumo da Análise")
        summary_table.add_column("Categoria", style="cyan")
        summary_table.add_column("Status", style="magenta")
        summary_table.add_column("Detalhes", style="white")

        for category, data in results.items():
            if isinstance(data, dict) and 'status' in data:
                status_color = "green" if data['status'] == 'OK' else "red"
                summary_table.add_row(
                    category.title(),
                    f"[{status_color}]{data['status']}[/{status_color}]",
                    data.get('details', 'N/A')
                )

        console.print(summary_table)

        # Exibir vulnerabilidades encontradas
        if 'vulnerabilities' in results and results['vulnerabilities']:
            vuln_table = Table(title="🚨 Vulnerabilidades Detectadas")
            vuln_table.add_column("Severidade", style="red")
            vuln_table.add_column("Tipo", style="yellow")
            vuln_table.add_column("Descrição", style="white")

            for vuln in results['vulnerabilities']:
                vuln_table.add_row(
                    vuln.get('severity', 'Unknown'),
                    vuln.get('type', 'Unknown'),
                    vuln.get('description', 'No description')
                )

            console.print(vuln_table)

    def start_monitoring(self, targets: list, interval: int = 300):
        """
        Inicia monitoramento contínuo de alvos

        Args:
            targets (list): Lista de URLs para monitorar
            interval (int): Intervalo entre verificações em segundos
        """
        console.print(f"\n🔍 [bold]Iniciando monitoramento de {len(targets)} alvos[/bold]")
        console.print(f"⏱️ Intervalo: {interval} segundos")

        self._log_action("MONITORING_STARTED", f"Targets: {len(targets)}, Interval: {interval}s")

        try:
            self.monitor.start_monitoring(targets, interval, self._monitoring_callback)
        except KeyboardInterrupt:
            console.print("\n🛑 [yellow]Monitoramento interrompido pelo usuário[/yellow]")
            self._log_action("MONITORING_STOPPED", "User interrupt")
        except Exception as e:
            error_msg = f"Erro no monitoramento: {str(e)}"
            console.print(f"❌ [red]{error_msg}[/red]")
            self._log_action("MONITORING_ERROR", error_msg)

    def _monitoring_callback(self, target: str, status: dict):
        """Callback para eventos de monitoramento"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if status.get('changed', False):
            console.print(f"🚨 [{timestamp}] [red]Mudança detectada em: {target}[/red]")
        else:
            console.print(f"✅ [{timestamp}] [green]{target} - OK[/green]")

    def show_help(self):
        """Exibe ajuda do sistema"""
        help_text = """
🆘 ELISA-FEDERAL - Ajuda do Sistema

📋 COMANDOS DISPONÍVEIS:

🎯 ANÁLISE:
  elisa.py scan <URL>              - Scan básico de segurança
  elisa.py scan <URL> --full       - Scan completo
  elisa.py scan <URL> --quick      - Scan rápido

🔍 MONITORAMENTO:
  elisa.py monitor <URL1,URL2>     - Monitorar múltiplos alvos
  elisa.py monitor <URL> --interval 60  - Intervalo personalizado

📄 RELATÓRIOS:
  elisa.py report --list           - Listar relatórios salvos
  elisa.py report --view <ID>      - Visualizar relatório

🛠️ SISTEMA:
  elisa.py --version               - Versão do sistema
  elisa.py --help                  - Esta ajuda
  elisa.py --update                - Atualizar do GitHub

📧 SUPORTE:
  GitHub: https://github.com/erikbaleeiro/ELISA-FEDERAL
  Issues: https://github.com/erikbaleeiro/ELISA-FEDERAL/issues

⚖️ AVISO LEGAL:
Esta ferramenta é para análise de recursos PÚBLICOS autorizados apenas.
O uso inadequado é de responsabilidade exclusiva do usuário.
        """

        console.print(Panel(help_text, style="blue"))

def main():
    """Função principal do sistema"""
    parser = argparse.ArgumentParser(
        description="🛡️ ELISA-FEDERAL - Sistema de Análise de Segurança Digital",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('command', nargs='?', help='Comando a executar')
    parser.add_argument('target', nargs='?', help='URL alvo para análise')
    parser.add_argument('--full', action='store_true', help='Scan completo')
    parser.add_argument('--quick', action='store_true', help='Scan rápido')
    parser.add_argument('--interval', type=int, default=300, help='Intervalo de monitoramento')
    parser.add_argument('--version', action='store_true', help='Mostrar versão')
    parser.add_argument('--update', action='store_true', help='Atualizar sistema')

    args = parser.parse_args()

    # Inicializar ELISA
    elisa = ElisaFederal()

    # Processar argumentos
    if args.version:
        console.print(f"🛡️ ELISA-FEDERAL v{elisa.version}")
        return

    if args.update:
        console.print("🔄 [yellow]Funcionalidade de atualização em desenvolvimento[/yellow]")
        return

    if not args.command:
        elisa.show_help()
        return

    # Executar comandos
    if args.command == 'scan':
        if not args.target:
            console.print("❌ [red]URL alvo é obrigatória para scan[/red]")
            return

        scan_type = 'full' if args.full else 'quick' if args.quick else 'basic'
        elisa.scan_target(args.target, scan_type)

    elif args.command == 'monitor':
        if not args.target:
            console.print("❌ [red]URL(s) alvo são obrigatórias para monitoramento[/red]")
            return

        targets = [url.strip() for url in args.target.split(',')]
        elisa.start_monitoring(targets, args.interval)

    elif args.command == 'help':
        elisa.show_help()

    else:
        console.print(f"❌ [red]Comando desconhecido: {args.command}[/red]")
        elisa.show_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Sistema interrompido pelo usuário[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"💥 [red]Erro fatal: {str(e)}[/red]")
        sys.exit(1)