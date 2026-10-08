#!/bin/bash
# Fix 403 error in nginx config for silas.buildwithai.digital
# Ensures proper location block ordering and proxy configuration

set -e

NGINX_SITE="/etc/nginx/sites-available/silas"
BACKUP_SITE="/etc/nginx/sites-available/silas.backup.$(date +%Y%m%d_%H%M%S)"

echo "=== Checking current nginx config ==="
nginx -t 2>&1 || true

echo ""
echo "=== Backing up current config ==="
cp "$NGINX_SITE" "$BACKUP_SITE"
echo "Backup saved to: $BACKUP_SITE"

echo ""
echo "=== Creating fixed nginx config ==="
cat > "$NGINX_SITE" << 'NGINX_CONF'
# ============================
# HTTPS SERVER (Frontend + API)
# ============================
server {
    listen 443 ssl;
    server_name silas.buildwithai.digital www.silas.buildwithai.digital;

    ssl_certificate /etc/letsencrypt/live/silas.buildwithai.digital/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/silas.buildwithai.digital/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ============================
    # FRONTEND (Vite Preview via PM2) - MUST BE FIRST
    # ============================
    location / {
        proxy_pass http://127.0.0.1:4173;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cache bypass for upgrades
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # ============================
    # BACKEND API (Python/Node) - MUST BE SECOND
    # ============================
    location ~ ^/(api|generate|v1|health) {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Cache bypass for upgrades
        proxy_cache_bypass $http_upgrade;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;

        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Optional: Serve static files directly if frontend is built
    # Uncomment below if you run `npm run build` and want nginx to serve static files
    # location / {
    #     root /home/silas/OpenJarvis/frontend/dist;
    #     try_files $uri $uri/ /index.html;
    #     
    #     # Cache static assets
    #     location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    #         expires 1y;
    #         add_header Cache-Control "public, immutable";
    #     }
    # }
}

# ============================
# HTTP -> HTTPS REDIRECT
# ============================
server {
    listen 80;
    server_name silas.buildwithai.digital www.silas.buildwithai.digital;
    
    # Allow Let's Encrypt ACME challenges
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    return 301 https://$host$request_uri;
}
NGINX_CONF

echo "=== Testing new nginx config ==="
nginx -t

echo ""
echo "=== Reloading nginx ==="
systemctl reload nginx

echo ""
echo "=== Verification ==="
echo "Config test passed. Nginx reloaded."
echo ""
echo "To verify the fix:"
echo "  curl -I https://silas.buildwithai.digital/"
echo "  curl -I https://silas.buildwithai.digital/api/health"
echo ""
echo "If SSL cert permission issues persist, run:"
echo "  sudo chmod 755 /etc/letsencrypt/live/ /etc/letsencrypt/archive/"
echo "  sudo chmod 644 /etc/letsencrypt/live/silas.buildwithai.digital/*"
echo "  sudo chmod 644 /etc/letsencrypt/archive/silas.buildwithai.digital/*"
