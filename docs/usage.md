# 📖 ELISA-FEDERAL - Guia de Uso Completo

## 🎯 Introdução

Este guia fornece instruções detalhadas sobre como usar todas as funcionalidades do ELISA-FEDERAL de forma eficaz e segura.

## 🚀 Primeiros Passos

### Verificação da Instalação

```bash
# Verificar se está funcionando
python3 elisa.py --version

# Exibir ajuda
python3 elisa.py --help
```

### Teste Básico

```bash
# Teste com site público
python3 elisa.py scan https://www.gov.br --quick
```

## 🔍 Módulo Scanner

### Tipos de Scan

#### Scan Rápido (Quick)
```bash
python3 elisa.py scan https://exemplo.gov.br --quick
```
- ⚡ **Mais rápido** (30-60 segundos)
- 🔍 **Verificações básicas:** SSL, headers principais
- 📊 **Ideal para:** Verificação rápida de status

#### Scan Básico (Default)
```bash
python3 elisa.py scan https://exemplo.gov.br
```
- ⚖️ **Balanceado** (2-5 minutos)
- 🔍 **Verificações:** SSL, headers, conteúdo básico
- 📊 **Ideal para:** Análise regular de segurança

#### Scan Completo (Full)
```bash
python3 elisa.py scan https://exemplo.gov.br --full
```
- 🔬 **Mais detalhado** (5-15 minutos)
- 🔍 **Verificações:** Tudo + diretórios, formulários
- 📊 **Ideal para:** Auditoria completa de segurança

### Interpretando Resultados

#### Score de Segurança
- **90-100:** 🟢 Excelente
- **70-89:** 🟡 Bom (pequenas melhorias)
- **50-69:** 🟠 Regular (atenção necessária)
- **0-49:** 🔴 Crítico (ação urgente)

#### Status SSL/TLS
- **OK:** ✅ Configurado corretamente
- **NO_SSL:** ❌ Sem HTTPS
- **SSL_ERROR:** ⚠️ Problemas de configuração

#### Headers de Segurança
- **X-Content-Type-Options:** Previne MIME sniffing
- **X-Frame-Options:** Proteção contra clickjacking
- **Content-Security-Policy:** Política de segurança de conteúdo
- **Strict-Transport-Security:** Força uso de HTTPS

## 👁️ Módulo Monitor

### Monitoramento Básico

```bash
# Monitorar um site (verifica a cada 5 minutos)
python3 elisa.py monitor https://exemplo.gov.br

# Intervalo personalizado (em segundos)
python3 elisa.py monitor https://exemplo.gov.br --interval 60
```

### Monitoramento Múltiplo

```bash
# Múltiplos sites separados por vírgula
python3 elisa.py monitor https://site1.gov.br,https://site2.gov.br,https://site3.gov.br
```

### Tipos de Mudanças Detectadas

- **Mudança de Status:** Código HTTP alterado
- **Mudança de Conteúdo:** Texto ou HTML modificado
- **Mudança de Certificado:** SSL/TLS alterado
- **Mudança de Headers:** Configuração de segurança modificada

### Interrompendo o Monitor

```bash
# Pressione Ctrl+C para parar o monitoramento
^C
```

## 📄 Módulo Relatórios

### Visualizar Relatórios

```bash
# Listar todos os relatórios
python3 elisa.py report --list

# Visualizar relatório específico
python3 elisa.py report --view elisa_report_20240914_143022
```

### Formatos de Relatório

#### Markdown (.md)
- 📖 **Legível por humanos**
- 🎨 **Formatação rica**
- 📤 **Fácil compartilhamento**

#### JSON (.json)
- 🤖 **Processável por máquinas**
- 📊 **Dados estruturados**
- 🔧 **Integração com outras ferramentas**

### Estrutura do Relatório

1. **Informações Gerais**
   - URL analisada
   - Data/hora do scan
   - Tipo de scan realizado
   - Score de segurança

2. **Análise SSL/TLS**
   - Status do certificado
   - Versão do protocolo
   - Data de expiração

3. **Headers de Segurança**
   - Headers presentes
   - Headers ausentes
   - Recomendações

4. **Análise de Conteúdo**
   - Tecnologias detectadas
   - Informações sensíveis expostas
   - Recursos externos

5. **Vulnerabilidades**
   - Lista de problemas encontrados
   - Severidade de cada item

6. **Recomendações**
   - Ações sugeridas
   - Prioridades de correção

## ⚙️ Configuração Avançada

### Arquivo de Configuração

```bash
# Copiar arquivo de exemplo
cp config/settings.example.json config/settings.json

# Editar configurações
nano config/settings.json
```

### Configurações Importantes

#### Scanner
```json
{
    "scanner": {
        "max_threads": 5,        // Threads simultâneas
        "deep_scan": false,      // Scan profundo
        "timeout": 10,           // Timeout por request
        "check_directories": false  // Verificar diretórios comuns
    }
}
```

#### Monitor
```json
{
    "monitor": {
        "default_interval": 300,  // Intervalo padrão (segundos)
        "max_targets": 10,       // Máximo de alvos simultâneos
        "save_baselines": true   // Salvar baselines
    }
}
```

#### Segurança
```json
{
    "security": {
        "respect_robots_txt": true,    // Respeitar robots.txt
        "max_request_rate": 10,        // Máximo requests/segundo
        "enable_rate_limiting": true   // Limitar taxa de requests
    }
}
```

## 🛡️ Boas Práticas de Uso

### Antes de Usar

1. **Autorização:** ✅ Confirme que tem permissão para analisar o alvo
2. **Legalidade:** ✅ Verifique conformidade com leis locais
3. **Ética:** ✅ Use apenas para fins legítimos de segurança

### Durante o Uso

1. **Rate Limiting:** 🐌 Não sobrecarregue o servidor alvo
2. **Horários:** 🕐 Evite horários de pico do sistema
3. **Monitoramento:** 👁️ Observe logs do seu próprio uso

### Após o Uso

1. **Relatórios:** 📄 Documente achados adequadamente
2. **Responsabilidade:** 📋 Reporte vulnerabilidades responsavelmente
3. **Limpeza:** 🧹 Limpe dados temporários se necessário

## 🚨 Cenários de Uso

### 1. Auditoria de Segurança Regular

```bash
# Scan mensal de sites corporativos
python3 elisa.py scan https://empresa.com.br --full
python3 elisa.py scan https://api.empresa.com.br --full
```

### 2. Monitoramento de Mudanças

```bash
# Monitorar sites críticos 24/7
python3 elisa.py monitor https://sistema-critico.gov.br --interval 300
```

### 3. Verificação Rápida

```bash
# Check rápido antes de deploy
python3 elisa.py scan https://staging.empresa.com.br --quick
```

### 4. Análise Comparativa

```bash
# Comparar diferentes ambientes
python3 elisa.py scan https://prod.empresa.com.br
python3 elisa.py scan https://staging.empresa.com.br
python3 elisa.py scan https://dev.empresa.com.br
```

## 🔧 Solução de Problemas

### Erros Comuns

#### Timeout de Conexão
```bash
# Aumentar timeout
python3 elisa.py scan URL --timeout 30
```

#### Muitos Requests
```bash
# Reduzir rate no config
{
    "security": {
        "max_request_rate": 5
    }
}
```

#### Certificado SSL Inválido
```bash
# Verificar manualmente
openssl s_client -connect domain.com:443
```

### Debug Mode

```bash
# Ativar logs detalhados
export ELISA_LOG_LEVEL="DEBUG"
python3 elisa.py scan URL

# Verificar logs
tail -f logs/elisa.log
```

## 📊 Casos de Uso Avançados

### Integração com CI/CD

```bash
#!/bin/bash
# Pipeline de segurança
python3 elisa.py scan $DEPLOY_URL --quick
if [ $? -eq 0 ]; then
    echo "✅ Verificação de segurança passou"
else
    echo "❌ Falha na verificação de segurança"
    exit 1
fi
```

### Scripts Automatizados

```bash
#!/bin/bash
# Scan automático de múltiplos sites
SITES=("https://site1.gov.br" "https://site2.gov.br" "https://site3.gov.br")

for site in "${SITES[@]}"; do
    echo "Analisando $site..."
    python3 elisa.py scan "$site" --full
    sleep 30  # Pausa entre scans
done
```

### Relatórios Customizados

```python
# Processar relatórios JSON
import json
import glob

reports = glob.glob("reports/*.json")
for report_file in reports:
    with open(report_file) as f:
        data = json.load(f)
        score = data['scan_results']['score']
        if score < 70:
            print(f"⚠️ {data['target_url']}: Score {score}")
```

## 📞 Suporte

### Documentação
- 📖 README.md - Documentação principal
- 📚 Wiki - Artigos detalhados
- 🎥 Tutoriais - Videos explicativos

### Comunidade
- 💬 GitHub Discussions - Perguntas gerais
- 🐛 GitHub Issues - Bugs e problemas
- 📧 Email - Suporte direto

### Recursos Adicionais
- 🔗 Links úteis de segurança
- 📚 Referências OWASP
- 🎓 Cursos de segurança recomendados

---

*Para mais informações, consulte a [documentação completa](https://github.com/erikbaleeiro/ELISA-FEDERAL) ou abra uma [issue](https://github.com/erikbaleeiro/ELISA-FEDERAL/issues).*