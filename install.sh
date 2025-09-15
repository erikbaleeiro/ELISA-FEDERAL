#!/bin/bash

# 🛡️ ELISA-FEDERAL - Instalador Automático
# Sistema Brasileiro de Análise de Segurança Digital
# Versão: 1.0.0

echo "🛡️ ELISA-FEDERAL - Instalador Automático"
echo "=========================================="
echo "🇧🇷 Sistema Brasileiro de Análise de Segurança Digital"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs coloridos
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está rodando no diretório correto
if [ ! -f "elisa.py" ]; then
    log_error "Execute este script no diretório do ELISA-FEDERAL"
    exit 1
fi

# 1. Verificar Python
log_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 não encontrado. Instale Python 3.9+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]]; then
    log_success "Python $PYTHON_VERSION encontrado"
else
    log_error "Python $PYTHON_VERSION encontrado, mas é necessário 3.9+"
    exit 1
fi

# 2. Verificar pip
log_info "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    log_error "pip3 não encontrado. Instale pip primeiro."
    exit 1
fi
log_success "pip3 encontrado"

# 3. Criar ambiente virtual (opcional)
read -p "🐍 Criar ambiente virtual? (recomendado) [Y/n]: " create_venv
create_venv=${create_venv:-Y}

if [[ $create_venv =~ ^[Yy]$ ]]; then
    log_info "Criando ambiente virtual..."
    python3 -m venv elisa_env

    log_info "Ativando ambiente virtual..."
    source elisa_env/bin/activate

    log_success "Ambiente virtual criado e ativado"

    # Criar script de ativação
    echo '#!/bin/bash' > activate_elisa.sh
    echo 'cd "$(dirname "$0")"' >> activate_elisa.sh
    echo 'source elisa_env/bin/activate' >> activate_elisa.sh
    echo 'echo "🛡️ ELISA-FEDERAL ambiente ativado"' >> activate_elisa.sh
    chmod +x activate_elisa.sh

    log_success "Script de ativação criado: ./activate_elisa.sh"
fi

# 4. Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip

# 5. Instalar dependências
log_info "Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        log_success "Dependências instaladas com sucesso"
    else
        log_error "Falha ao instalar dependências"
        exit 1
    fi
else
    log_error "Arquivo requirements.txt não encontrado"
    exit 1
fi

# 6. Criar diretórios necessários
log_info "Criando diretórios necessários..."
mkdir -p logs reports cache temp
log_success "Diretórios criados"

# 7. Tornar executável
log_info "Configurando permissões..."
chmod +x elisa.py
chmod +x scripts/*.sh 2>/dev/null || true
log_success "Permissões configuradas"

# 8. Configurar arquivo de config
log_info "Configurando arquivo de configuração..."
if [ ! -f "config/settings.json" ]; then
    cp config/settings.example.json config/settings.json
    log_success "Arquivo de configuração criado"
else
    log_warning "Arquivo de configuração já existe"
fi

# 9. Teste básico
log_info "Executando teste básico..."
python3 elisa.py --version
if [ $? -eq 0 ]; then
    log_success "Teste básico passou"
else
    log_error "Teste básico falhou"
    exit 1
fi

# 10. Verificar dependências específicas
log_info "Verificando dependências específicas..."

# Verificar requests
python3 -c "import requests" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "requests - OK"
else
    log_error "requests - FALHA"
fi

# Verificar beautifulsoup4
python3 -c "import bs4" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "beautifulsoup4 - OK"
else
    log_error "beautifulsoup4 - FALHA"
fi

# Verificar rich
python3 -c "import rich" 2>/dev/null
if [ $? -eq 0 ]; then
    log_success "rich - OK"
else
    log_error "rich - FALHA"
fi

# 11. Criar scripts de conveniência
log_info "Criando scripts de conveniência..."

# Script de execução fácil
cat > elisa << 'EOF'
#!/bin/bash
# Script de conveniência para ELISA-FEDERAL
cd "$(dirname "$0")"
if [ -d "elisa_env" ]; then
    source elisa_env/bin/activate
fi
python3 elisa.py "$@"
EOF
chmod +x elisa

# Script de atualização
cat > update.sh << 'EOF'
#!/bin/bash
# Script de atualização ELISA-FEDERAL
echo "🔄 Atualizando ELISA-FEDERAL..."
git pull origin main
if [ -d "elisa_env" ]; then
    source elisa_env/bin/activate
fi
pip install -r requirements.txt --upgrade
echo "✅ Atualização concluída"
EOF
chmod +x update.sh

log_success "Scripts de conveniência criados"

# 12. Informações finais
echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo ""
log_success "ELISA-FEDERAL está pronto para uso!"
echo ""
echo "📋 COMO USAR:"
echo ""

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "   🐍 Ativar ambiente virtual:"
    echo "      ./activate_elisa.sh"
    echo ""
fi

echo "   🎯 Executar ELISA:"
echo "      ./elisa --help                    # Ver ajuda"
echo "      ./elisa scan https://exemplo.gov.br   # Scan básico"
echo "      python3 elisa.py --help          # Forma alternativa"
echo ""
echo "   📄 Relatórios:"
echo "      ./elisa report --list             # Listar relatórios"
echo ""
echo "   👁️  Monitoramento:"
echo "      ./elisa monitor https://exemplo.gov.br"
echo ""
echo "   🔄 Atualizar:"
echo "      ./update.sh"
echo ""

echo "📚 DOCUMENTAÇÃO:"
echo "   📖 README.md       - Documentação principal"
echo "   📚 docs/usage.md   - Guia detalhado de uso"
echo "   ⚙️  config/         - Arquivos de configuração"
echo ""

echo "🛡️ LEMBRE-SE:"
echo "   ⚖️  Use apenas em recursos PÚBLICOS autorizados"
echo "   📋 Obtenha permissão adequada antes do uso"
echo "   🇧🇷 Respeite as leis brasileiras"
echo ""

echo "💬 SUPORTE:"
echo "   🐙 GitHub: https://github.com/erikbaleeiro/ELISA-FEDERAL"
echo "   🐛 Issues: https://github.com/erikbaleeiro/ELISA-FEDERAL/issues"
echo ""

log_success "Instalação finalizada! Bom uso do ELISA-FEDERAL! 🛡️🇧🇷"