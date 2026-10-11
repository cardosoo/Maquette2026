#!/bin/bash

# Script de démarrage pour l'application Maquettes API

echo "=========================================="
echo "  Maquettes API - Script de démarrage"
echo "=========================================="
echo ""

# Vérifier si uvloop est disponible (optionnel pour de meilleures performances)
if python -c "import uvloop" 2>/dev/null; then
    UVLOOP_OPT="--loop uvloop"
    echo "✓ uvloop détecté - utilisation pour de meilleures performances"
else
    UVLOOP_OPT=""
fi

# Vérifier si --reload est souhaité (mode développement)
if [ "$1" = "dev" ] || [ "$1" = "--dev" ] || [ "$1" = "-d" ]; then
    RELOAD_OPT="--reload"
    echo "✓ Mode développement activé (rechargement automatique)"
else
    RELOAD_OPT=""
fi

# Port par défaut
PORT=${2:-8000}

echo ""
echo "Démarrage du serveur FastAPI..."
echo "- Port: $PORT"
echo "- Documentation: http://localhost:$PORT/docs"
echo "- Health check: http://localhost:$PORT/health"
echo ""

# Démarrer l'application
uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    $UVLOOP_OPT \
    $RELOAD_OPT
