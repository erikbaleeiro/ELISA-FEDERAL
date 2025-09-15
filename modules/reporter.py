#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📄 ELISA-FEDERAL - Módulo Gerador de Relatórios
Sistema de geração de relatórios de segurança
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from rich.console import Console
from rich.table import Table

console = Console()

class ReportGenerator:
    """
    📄 Gerador de relatórios de segurança
    Cria relatórios em formatos Markdown e JSON
    """

    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, scan_results: Dict, target_url: str) -> str:
        """
        Gera relatório completo da análise

        Args:
            scan_results: Resultados do scan
            target_url: URL analisada

        Returns:
            Caminho do arquivo de relatório gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"elisa_report_{timestamp}"

        # Gerar relatório em Markdown
        markdown_path = self._generate_markdown_report(scan_results, target_url, report_id)

        # Gerar relatório em JSON
        json_path = self._generate_json_report(scan_results, target_url, report_id)

        console.print(f"📄 [green]Relatórios gerados:[/green]")
        console.print(f"   📝 Markdown: {markdown_path}")
        console.print(f"   📊 JSON: {json_path}")

        return markdown_path

    def _generate_markdown_report(self, results: Dict, target_url: str, report_id: str) -> str:
        """Gera relatório em formato Markdown"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{self.reports_dir}/{report_id}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self._create_markdown_content(results, target_url, timestamp))

        return filename

    def _generate_json_report(self, results: Dict, target_url: str, report_id: str) -> str:
        """Gera relatório em formato JSON"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{self.reports_dir}/{report_id}.json"

        # Preparar dados para JSON
        json_data = {
            'report_id': report_id,
            'generated_at': timestamp,
            'elisa_version': '1.0.0',
            'target_url': target_url,
            'scan_results': results,
            'metadata': {
                'generator': 'ELISA-FEDERAL',
                'format_version': '1.0',
                'legal_notice': 'Relatório gerado para análise de segurança de recursos públicos autorizados'
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return filename

    def _create_markdown_content(self, results: Dict, target_url: str, timestamp: str) -> str:
        """Cria conteúdo do relatório em Markdown"""

        content = f"""# 🛡️ ELISA-FEDERAL - Relatório de Segurança

## 📋 Informações Gerais

- **URL Analisada:** `{target_url}`
- **Data/Hora:** {timestamp}
- **Versão ELISA:** 1.0.0
- **Tipo de Scan:** {results.get('scan_type', 'N/A')}
- **Score de Segurança:** {results.get('score', 'N/A')}/100

---

## 🔒 Análise SSL/TLS

"""

        # Análise SSL
        ssl_analysis = results.get('ssl_analysis', {})
        content += self._format_ssl_section(ssl_analysis)

        # Análise de Headers
        content += "\n## 📋 Análise de Headers de Segurança\n\n"
        headers_analysis = results.get('headers_analysis', {})
        content += self._format_headers_section(headers_analysis)

        # Análise de Conteúdo
        if 'content_analysis' in results:
            content += "\n## 📄 Análise de Conteúdo\n\n"
            content_analysis = results['content_analysis']
            content += self._format_content_section(content_analysis)

        # Vulnerabilidades
        if results.get('vulnerabilities'):
            content += "\n## 🚨 Vulnerabilidades Detectadas\n\n"
            content += self._format_vulnerabilities_section(results['vulnerabilities'])

        # Recomendações
        content += "\n## 💡 Recomendações de Segurança\n\n"
        content += self._generate_recommendations(results)

        # Rodapé legal
        content += self._add_legal_footer()

        return content

    def _format_ssl_section(self, ssl_analysis: Dict) -> str:
        """Formata seção de análise SSL"""
        status = ssl_analysis.get('status', 'UNKNOWN')

        if status == 'NO_SSL':
            return """
❌ **Status:** Sem SSL/TLS
- O site não utiliza HTTPS
- **Risco:** ALTO - Dados transmitidos sem criptografia

"""
        elif status == 'OK':
            cert_valid = ssl_analysis.get('certificate_valid', False)
            protocol = ssl_analysis.get('protocol_version', 'N/A')
            expiry = ssl_analysis.get('expiry_date', 'N/A')

            return f"""
✅ **Status:** SSL Configurado
- **Certificado Válido:** {'Sim' if cert_valid else 'Não'}
- **Versão do Protocolo:** {protocol}
- **Data de Expiração:** {expiry}

"""
        else:
            issues = ssl_analysis.get('issues', [])
            issues_text = '\n'.join([f"- {issue}" for issue in issues])

            return f"""
⚠️ **Status:** Problemas Detectados
{issues_text}

"""

    def _format_headers_section(self, headers_analysis: Dict) -> str:
        """Formata seção de análise de headers"""
        security_headers = headers_analysis.get('security_headers', {})
        missing_headers = headers_analysis.get('missing_headers', [])

        content = "### Headers de Segurança Presentes\n\n"

        if security_headers:
            for header, value in security_headers.items():
                status = "✅" if value else "❌"
                content += f"- {status} **{header}:** `{value or 'Ausente'}`\n"

        if missing_headers:
            content += "\n### ⚠️ Headers de Segurança Ausentes\n\n"
            for header in missing_headers:
                content += f"- ❌ **{header}**\n"

        return content + "\n"

    def _format_content_section(self, content_analysis: Dict) -> str:
        """Formata seção de análise de conteúdo"""
        content = ""

        # Tecnologias detectadas
        technologies = content_analysis.get('technologies', [])
        if technologies:
            content += "### 🔧 Tecnologias Detectadas\n\n"
            for tech in technologies:
                content += f"- **{tech.get('type', 'Unknown')}:** {tech.get('name', 'Unknown')} _{tech.get('source', '')}_\n"
            content += "\n"

        # Informações sensíveis
        sensitive_info = content_analysis.get('sensitive_info', [])
        if sensitive_info:
            content += "### ⚠️ Informações Sensíveis Expostas\n\n"
            for info in sensitive_info:
                content += f"- **{info.get('type')}:** {info.get('count')} ocorrências encontradas\n"
            content += "\n"

        # Recursos externos
        external_resources = content_analysis.get('external_resources', [])
        if external_resources:
            content += "### 🌐 Recursos Externos\n\n"
            for resource in external_resources:
                risk_color = "🔴" if resource.get('risk') == 'HIGH' else "🟡" if resource.get('risk') == 'MEDIUM' else "🟢"
                content += f"- {risk_color} **{resource.get('type')}:** `{resource.get('url')}`\n"
            content += "\n"

        return content

    def _format_vulnerabilities_section(self, vulnerabilities: List[Dict]) -> str:
        """Formata seção de vulnerabilidades"""
        content = ""

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'Unknown')
            vuln_type = vuln.get('type', 'Unknown')
            description = vuln.get('description', 'No description')

            severity_icon = {
                'LOW': '🟢',
                'MEDIUM': '🟡',
                'HIGH': '🔴',
                'CRITICAL': '🚨'
            }.get(severity.upper(), '⚪')

            content += f"""
### {severity_icon} {vuln_type} - Severidade: {severity}

**Descrição:** {description}

"""

        return content

    def _generate_recommendations(self, results: Dict) -> str:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []

        # Recomendações SSL
        ssl_analysis = results.get('ssl_analysis', {})
        if ssl_analysis.get('status') == 'NO_SSL':
            recommendations.append("🔒 **Implementar HTTPS** - Configure certificado SSL/TLS válido")

        # Recomendações Headers
        headers_analysis = results.get('headers_analysis', {})
        missing_headers = headers_analysis.get('missing_headers', [])

        important_headers = {
            'X-Content-Type-Options': 'Adicionar `X-Content-Type-Options: nosniff`',
            'X-Frame-Options': 'Adicionar `X-Frame-Options: DENY` ou `SAMEORIGIN`',
            'Content-Security-Policy': 'Implementar Content Security Policy (CSP)',
            'Strict-Transport-Security': 'Adicionar HSTS para HTTPS obrigatório'
        }

        for header in missing_headers:
            if header in important_headers:
                recommendations.append(f"📋 **{header}** - {important_headers[header]}")

        # Recomendações de conteúdo
        content_analysis = results.get('content_analysis', {})
        sensitive_info = content_analysis.get('sensitive_info', [])

        if sensitive_info:
            recommendations.append("🔍 **Informações Sensíveis** - Revisar e remover dados expostos desnecessariamente")

        # Score baixo
        score = results.get('score', 100)
        if score < 70:
            recommendations.append("⚡ **Score Baixo** - Implementar melhorias urgentes de segurança")

        if not recommendations:
            recommendations.append("✅ **Parabéns!** - Nenhuma recomendação crítica identificada")

        return '\n'.join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)]) + "\n"

    def _add_legal_footer(self) -> str:
        """Adiciona rodapé legal ao relatório"""
        return """
---

## ⚖️ Aviso Legal

Este relatório foi gerado pela ferramenta **ELISA-FEDERAL** para análise de segurança de recursos públicos autorizados.

### Responsabilidades:
- ✅ Este scan foi realizado apenas em recursos **PÚBLICOS**
- ✅ Nenhuma exploração de vulnerabilidades foi realizada
- ✅ O objetivo é **preventivo e educacional**
- ❌ O uso inadequado desta ferramenta é de responsabilidade do usuário

### Sobre o ELISA-FEDERAL:
- **Projeto:** Open Source Brasileiro
- **GitHub:** https://github.com/erikbaleeiro/ELISA-FEDERAL
- **Licença:** MIT
- **Versão:** 1.0.0

---

*Relatório gerado automaticamente pelo ELISA-FEDERAL em {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    def list_reports(self) -> List[Dict]:
        """Lista todos os relatórios salvos"""
        reports = []

        if not os.path.exists(self.reports_dir):
            return reports

        for filename in os.listdir(self.reports_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.reports_dir, filename)
                stats = os.stat(filepath)

                reports.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stats.st_size,
                    'created': datetime.fromtimestamp(stats.st_ctime),
                    'modified': datetime.fromtimestamp(stats.st_mtime)
                })

        # Ordenar por data de modificação (mais recente primeiro)
        reports.sort(key=lambda x: x['modified'], reverse=True)

        return reports

    def display_reports_table(self):
        """Exibe tabela com relatórios salvos"""
        reports = self.list_reports()

        if not reports:
            console.print("📄 [yellow]Nenhum relatório encontrado[/yellow]")
            return

        table = Table(title="📄 Relatórios ELISA-FEDERAL")
        table.add_column("Arquivo", style="cyan")
        table.add_column("Tamanho", style="magenta")
        table.add_column("Criado", style="green")
        table.add_column("Modificado", style="yellow")

        for report in reports:
            size_kb = round(report['size'] / 1024, 1)
            table.add_row(
                report['filename'],
                f"{size_kb} KB",
                report['created'].strftime("%d/%m/%Y %H:%M"),
                report['modified'].strftime("%d/%m/%Y %H:%M")
            )

        console.print(table)

    def view_report(self, report_id: str):
        """Visualiza um relatório específico"""
        report_path = f"{self.reports_dir}/{report_id}.md"

        if not os.path.exists(report_path):
            console.print(f"❌ [red]Relatório não encontrado: {report_id}[/red]")
            return

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        console.print(content)