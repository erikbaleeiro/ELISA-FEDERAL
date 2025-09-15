#!/bin/bash

# 🚀 ELISA-FEDERAL - Script de Deploy Automático
# Automatiza commit e push para GitHub

echo "🚀 ELISA-FEDERAL - Deploy Automático"
echo "===================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Verificar se está no diretório do projeto
if [ ! -f "elisa.py" ]; then
    log_error "Execute este script no diretório do ELISA-FEDERAL"
    exit 1
fi

# Verificar se git está inicializado
if [ ! -d ".git" ]; then
    log_warning "Git não inicializado. Inicializando..."
    git init
    git remote add origin https://github.com/erikbaleeiro/ELISA-FEDERAL.git
fi

# Parâmetros opcionais
COMMIT_MSG="$1"
BRANCH="${2:-main}"

# Se mensagem de commit não foi fornecida, solicitar
if [ -z "$COMMIT_MSG" ]; then
    echo "📝 Digite a mensagem do commit:"
    read -r COMMIT_MSG
fi

# Se ainda estiver vazia, usar mensagem padrão
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="🔄 Atualização automática - $(date '+%Y-%m-%d %H:%M:%S')"
fi

log_info "Verificando status do repositório..."

# Verificar se há mudanças
if git diff-index --quiet HEAD --; then
    log_warning "Nenhuma mudança detectada"
    read -p "Continuar mesmo assim? [y/N]: " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        log_info "Deploy cancelado"
        exit 0
    fi
fi

# Mostrar status
log_info "Status atual do repositório:"
git status --short

echo ""
read -p "🤔 Continuar com o deploy? [Y/n]: " confirm
confirm=${confirm:-Y}

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    log_info "Deploy cancelado pelo usuário"
    exit 0
fi

# Adicionar arquivos
log_info "Adicionando arquivos..."
git add .

# Verificar se há arquivos para commit
if git diff-index --quiet --cached HEAD --; then
    log_warning "Nenhuma mudança para commit"
    exit 0
fi

# Fazer commit
log_info "Fazendo commit: \"$COMMIT_MSG\""
git commit -m "$COMMIT_MSG"

if [ $? -ne 0 ]; then
    log_error "Falha no commit"
    exit 1
fi

log_success "Commit realizado com sucesso"

# Push para GitHub
log_info "Enviando para GitHub (branch: $BRANCH)..."
git push origin $BRANCH

if [ $? -eq 0 ]; then
    log_success "Push realizado com sucesso!"
    echo ""
    echo "🌐 Acesse: https://github.com/erikbaleeiro/ELISA-FEDERAL"
else
    log_error "Falha no push"
    echo ""
    echo "💡 Possíveis soluções:"
    echo "   1. Verificar credenciais do GitHub"
    echo "   2. Verificar conectividade de internet"
    echo "   3. Verificar se o repositório existe"
    echo "   4. Executar: git remote -v"
    exit 1
fi

# Mostrar informações do último commit
echo ""
log_info "Informações do último commit:"
git log --oneline -1

# Mostrar estatísticas
echo ""
log_info "Estatísticas do repositório:"
echo "   📊 Total de commits: $(git rev-list --all --count)"
echo "   📁 Arquivos rastreados: $(git ls-files | wc -l)"
echo "   👥 Contribuidores: $(git shortlog -sn | wc -l)"

echo ""
log_success "Deploy concluído com sucesso! 🚀"