#!/bin/bash
# ================================================================
# FarmTech Solutions — Fase 3
# Script de inicialização do repositório GitHub
#
# Uso:
#   chmod +x setup_github.sh
#   ./setup_github.sh SEU_USUARIO_GITHUB
# ================================================================

USUARIO="${1:-SEU_USUARIO_GITHUB}"
REPO="farmtech-fase3"
URL_REMOTA="https://github.com/${USUARIO}/${REPO}.git"

echo "════════════════════════════════════════════════════════"
echo "  FarmTech Solutions — Setup GitHub"
echo "  Repositório: ${URL_REMOTA}"
echo "════════════════════════════════════════════════════════"
echo ""

# 1. Inicializa repositório local
git init
git checkout -b main

# 2. Configura identidade (ajuste se necessário)
# git config user.name "Seu Nome"
# git config user.email "seu@email.com"

# 3. Adiciona todos os arquivos
git add .

# 4. Commit inicial
git commit -m "feat: FarmTech Fase 3 — Sistema de Gestão de Perdas na Colheita de Cana"

# 5. Branches de desenvolvimento
git checkout -b dev
git checkout main

# 6. Adiciona remote e faz push
echo ""
echo "Conectando ao GitHub..."
echo "URL: ${URL_REMOTA}"
echo ""
echo "ATENÇÃO: Crie o repositório '${REPO}' no GitHub ANTES de executar o push!"
echo "Acesse: https://github.com/new"
echo ""
read -p "Repositório criado no GitHub? Pressione ENTER para continuar..."

git remote add origin "${URL_REMOTA}"
git push -u origin main

echo ""
echo "✅ Repositório publicado com sucesso!"
echo "   Acesse: https://github.com/${USUARIO}/${REPO}"
