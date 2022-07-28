#!/usr/bin/env bash
set -e

cd /app

ENVIRONMENT=${ENVIRONMENT:-"local"}

if [[ "local" = $ENVIRONMENT* ]]; then
    gosu django uvicorn lukis.main:app --reload --host 0.0.0.0
else
    gosu django gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 lukis.main:app
fi
