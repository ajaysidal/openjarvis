#!/bin/bash
# Nginx Fix Script for silas.buildwithai.digital
# Run on your server with: sudo bash fix_nginx_silas.sh

set -e

DOMAIN="silas.buildwithai.digital"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"

echo "=== Nginx Fix for $DOMAIN ==="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Write nginx configuration
echo "Writing nginx configuration to $NGINX_SITES_AVAILABLE/silas..."
cat > "$NGINX_SITES_AVAILABLE/silas" << 'NGINX_CONF'
# HTTP - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name silas.buildwithai.digital www.silas.buildwithai.digital;
    
    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - main application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name silas.buildwithai.digital www.silas.buildwithai.digital;

    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/silas.buildwithai.digital/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/silas.buildwithai.digital/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Proxy to application (adjust port as needed)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:3000/health;
        access_log off;
    }
}
NGINX_CONF

# Enable site
echo "Enabling site..."
ln -sf "$NGINX_SITES_AVAILABLE/silas" "$NGINX_SITES_ENABLED/"

# Remove default site if exists
rm -f "$NGINX_SITES_ENABLED/default"

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Restart nginx
echo "Restarting nginx..."
systemctl restart nginx

# Test with curl
echo "Testing with curl..."
curl -I https://silas.buildwithai.digital

echo ""
echo "=== Complete ==="
