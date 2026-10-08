#!/bin/bash
set -e

echo "=== Silas Deploy Started ==="

FRONTEND_DIR="/home/silas/OpenJarvis/frontend"

echo "=== Pulling latest code ==="
git pull

echo "=== Building frontend ==="
cd $FRONTEND_DIR
npm install
npm run build

echo "=== Restarting frontend ==="
pm2 restart silas-frontend

echo "=== Reloading PM2 (zero downtime) ==="
pm2 reload all

echo "=== Health Check ==="
curl -i https://silas.buildwithai.digital/health || true

echo "=== Silas Deploy Complete ==="
