# 🛡️ ELISA-FEDERAL

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-yellow)
![Status](https://img.shields.io/badge/status-active-brightgreen)

**Extended Linguistic Intelligence for Security Analysis**

🇧🇷 Sistema Brasileiro de Análise de Segurança Digital

## 📋 Sobre o Projeto

ELISA-FEDERAL é uma ferramenta open-source brasileira desenvolvida para análise de segurança digital em recursos **PÚBLICOS autorizados**. O sistema foi projetado para ajudar organizações e pesquisadores a identificar vulnerabilidades de forma ética e legal.

### 🎯 Objetivos

- ✅ Detectar vulnerabilidades em APIs e sites públicos
- ✅ Monitorar endpoints expostos em tempo real
- ✅ Gerar relatórios detalhados de segurança
- ✅ Educar sobre boas práticas de segurança
- ✅ Promover a segurança digital no Brasil

### ⚖️ Princípios Éticos

- 🔒 **Apenas recursos PÚBLICOS** - Sem invasão de sistemas privados
- 📚 **Foco educacional** - Prevenção e conscientização
- 🚫 **Não exploração** - Detectar, não explorar vulnerabilidades
- 📖 **Transparência total** - Código 100% aberto e auditável
- 🇧🇷 **Conformidade legal** - Respeito às leis brasileiras

## 🚀 Instalação Rápida

### Pré-requisitos

```bash
# Python 3.9 ou superior
python3 --version

# Git
git --version
```

### Instalação Automática

```bash
# Clonar repositório
git clone https://github.com/erikbaleeiro/ELISA-FEDERAL.git
cd ELISA-FEDERAL

# Executar instalador
chmod +x install.sh
./install.sh
```

### Instalação Manual

```bash
# Instalar dependências
pip install -r requirements.txt

# Tornar executável
chmod +x elisa.py

# Teste básico
python3 elisa.py --help
```

## 💻 Como Usar

### Análise Básica

```bash
# Scan básico de segurança
python3 elisa.py scan https://exemplo.gov.br

# Scan completo
python3 elisa.py scan https://exemplo.gov.br --full

# Scan rápido
python3 elisa.py scan https://exemplo.gov.br --quick
```

### Monitoramento Contínuo

```bash
# Monitorar um site
python3 elisa.py monitor https://exemplo.gov.br

# Monitorar múltiplos sites
python3 elisa.py monitor https://site1.gov.br,https://site2.gov.br

# Intervalo personalizado (segundos)
python3 elisa.py monitor https://exemplo.gov.br --interval 60
```

### Relatórios

```bash
# Listar relatórios salvos
python3 elisa.py report --list

# Visualizar relatório específico
python3 elisa.py report --view elisa_report_20240914_143022
```

## 📊 Funcionalidades

### 🔍 Scanner de Vulnerabilidades

- **Análise SSL/TLS** - Verificação de certificados e configurações
- **Headers de Segurança** - Detecção de headers ausentes/mal configurados
- **Análise de Conteúdo** - Busca por informações sensíveis expostas
- **Detecção de Tecnologias** - Identificação de frameworks e CMS
- **Score de Segurança** - Pontuação geral (0-100)

### 👁️ Monitor em Tempo Real

- **Monitoramento Contínuo** - Verificação automática de mudanças
- **Detecção de Alterações** - Hash-based change detection
- **Alertas Inteligentes** - Notificações sobre mudanças relevantes
- **Múltiplos Alvos** - Monitoramento simultâneo

### 📄 Gerador de Relatórios

- **Formato Markdown** - Relatórios legíveis e estruturados
- **Formato JSON** - Dados estruturados para integração
- **Análise Detalhada** - Informações técnicas completas
- **Recomendações** - Sugestões de melhorias

## 📁 Estrutura do Projeto

```
ELISA-FEDERAL/
├── elisa.py              # 🎯 Arquivo principal
├── requirements.txt      # 📦 Dependências Python
├── install.sh           # 🚀 Instalador automático
├── README.md            # 📖 Esta documentação
├── LICENSE              # ⚖️ Licença MIT
├── .gitignore          # 🚫 Arquivos ignorados
├── modules/            # 🧩 Módulos do sistema
│   ├── scanner.py      # 🔍 Scanner de vulnerabilidades
│   ├── monitor.py      # 👁️ Monitor em tempo real
│   └── reporter.py     # 📄 Gerador de relatórios
├── config/             # ⚙️ Configurações
│   └── settings.example.json
├── scripts/            # 🛠️ Scripts auxiliares
│   └── auto-deploy.sh  # 🚀 Deploy automático
├── docs/               # 📚 Documentação
│   └── usage.md        # 📖 Guia de uso
├── logs/               # 📝 Arquivos de log
├── reports/            # 📄 Relatórios gerados
└── cache/              # 🗄️ Cache temporário
```

## 🔧 Configuração Avançada

### Arquivo de Configuração

Copie e edite o arquivo de exemplo:

```bash
cp config/settings.example.json config/settings.json
```

```json
{
    "scan_timeout": 10,
    "max_threads": 5,
    "user_agent": "ELISA-FEDERAL/1.0",
    "output_format": "markdown",
    "monitoring_interval": 300,
    "report_retention_days": 30
}
```

### Variáveis de Ambiente

```bash
# Configurações opcionais
export ELISA_CONFIG_PATH="/path/to/config.json"
export ELISA_REPORTS_DIR="/path/to/reports"
export ELISA_LOG_LEVEL="INFO"
```

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro de dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Erro de permissão:**
```bash
chmod +x elisa.py
chmod +x install.sh
```

**Timeout de conexão:**
```bash
# Aumentar timeout no config ou usar:
python3 elisa.py scan URL --timeout 30
```

### Logs de Debug

```bash
# Ativar logs detalhados
export ELISA_LOG_LEVEL="DEBUG"
python3 elisa.py scan URL

# Verificar logs
tail -f logs/elisa.log
```

## 🤝 Contribuindo

### Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork
3. **Crie** uma branch para sua feature
4. **Implemente** suas mudanças
5. **Teste** thoroughly
6. **Submit** um Pull Request

### Padrões de Código

- **Comentários em português** para código brasileiro
- **Docstrings detalhadas** em todas as funções
- **Type hints** sempre que possível
- **Testes unitários** para novas funcionalidades

### Reportar Bugs

Use o [GitHub Issues](https://github.com/erikbaleeiro/ELISA-FEDERAL/issues) com:

- 🐛 **Descrição clara** do problema
- 🔄 **Passos para reproduzir**
- 🖥️ **Ambiente** (OS, Python version, etc.)
- 📄 **Logs relevantes**

## 📜 Licença

Este projeto está licenciado sob a **Licença MIT** - veja o arquivo [LICENSE](LICENSE) para detalhes.

### Resumo da Licença

✅ **Uso comercial** permitido
✅ **Modificação** permitida
✅ **Distribuição** permitida
✅ **Uso privado** permitido
❗ **Sem garantia** - uso por sua conta e risco

## ⚖️ Aviso Legal

### 🚨 IMPORTANTE - LEIA ATENTAMENTE

Esta ferramenta é destinada **EXCLUSIVAMENTE** para:

- ✅ Análise de recursos **PÚBLICOS** com autorização
- ✅ Fins **educacionais** e de pesquisa
- ✅ Melhorias de **segurança preventiva**
- ✅ Conformidade com **leis brasileiras**

### 🚫 PROIBIDO

- ❌ Exploração de vulnerabilidades encontradas
- ❌ Acesso não autorizado a sistemas
- ❌ Coleta de dados privados/sensíveis
- ❌ Qualquer atividade ilegal

### 📋 Responsabilidades

O **usuário** é totalmente responsável por:
- Obter autorização adequada antes do uso
- Respeitar termos de serviço dos sites
- Cumprir todas as leis aplicáveis
- Usar a ferramenta de forma ética

Os **desenvolvedores** não se responsabilizam por uso inadequado.

## 👥 Equipe

### Desenvolvedor Principal

**Erik Baleeiro**
- 🐙 GitHub: [@erikbaleeiro](https://github.com/erikbaleeiro)
- 📧 Email: erik@baleeiro.dev
- 🌐 Site: https://erikbaleeiro.dev

### Colaboradores

Veja a lista completa de [contribuidores](https://github.com/erikbaleeiro/ELISA-FEDERAL/contributors).

## 🙏 Agradecimentos

- **Comunidade Python Brasil** 🐍🇧🇷
- **OWASP Foundation** para metodologias de segurança
- **Rich Library** para interface de terminal bonita
- **Requests Library** para HTTP simplificado
- **BeautifulSoup** para parsing HTML

## 📞 Suporte

### Documentação

- 📖 **Wiki:** [GitHub Wiki](https://github.com/erikbaleeiro/ELISA-FEDERAL/wiki)
- 📚 **Docs:** [Documentação Completa](docs/)
- 🎥 **Tutoriais:** [YouTube Playlist](#)

### Comunidade

- 💬 **Discord:** [Servidor ELISA-FEDERAL](#)
- 📱 **Telegram:** [Grupo Oficial](#)
- 🐦 **Twitter:** [@ElisaFederal](#)

### Suporte Técnico

- 🐛 **Issues:** [GitHub Issues](https://github.com/erikbaleeiro/ELISA-FEDERAL/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/erikbaleeiro/ELISA-FEDERAL/discussions)
- 📧 **Email:** suporte@elisa-federal.dev

---

## 📊 Status do Projeto

![GitHub stars](https://img.shields.io/github/stars/erikbaleeiro/ELISA-FEDERAL?style=social)
![GitHub forks](https://img.shields.io/github/forks/erikbaleeiro/ELISA-FEDERAL?style=social)
![GitHub issues](https://img.shields.io/github/issues/erikbaleeiro/ELISA-FEDERAL)
![GitHub last commit](https://img.shields.io/github/last-commit/erikbaleeiro/ELISA-FEDERAL)

**Feito com ❤️ no Brasil para a comunidade brasileira de segurança digital.**

---

*ELISA-FEDERAL v1.0.0 - Sistema Brasileiro de Análise de Segurança Digital*
