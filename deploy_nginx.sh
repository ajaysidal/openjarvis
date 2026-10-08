#!/bin/bash
# Nginx Deployment Script
# Run this script on your server to deploy nginx configuration

set -e

# Configuration variables
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
DOMAIN="${DOMAIN:-example.com}"
APP_PORT="${APP_PORT:-3000}"
SSL_EMAIL="${SSL_EMAIL:-admin@example.com}"

echo "=== Nginx Deployment Script ==="
echo "Domain: $DOMAIN"
echo "App Port: $APP_PORT"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Update package list and install nginx
echo "Installing nginx..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Create nginx site configuration
echo "Creating nginx configuration for $DOMAIN..."
cat > "$NGINX_SITES_AVAILABLE/$DOMAIN" << NGINX_CONF
# HTTP - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;
    
    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS - main application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
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

    # Proxy to application
    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://localhost:$APP_PORT;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:$APP_PORT/health;
        access_log off;
    }
}
NGINX_CONF

# Enable site
echo "Enabling site..."
ln -sf "$NGINX_SITES_AVAILABLE/$DOMAIN" "$NGINX_SITES_ENABLED/"

# Remove default site
rm -f "$NGINX_SITES_ENABLED/default"

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "$SSL_EMAIL" --redirect

# Reload nginx
echo "Reloading nginx..."
systemctl reload nginx

# Enable nginx on boot
systemctl enable nginx

echo ""
echo "=== Deployment Complete ==="
echo "Your site is now available at: https://$DOMAIN"
echo ""
echo "Useful commands:"
echo "  - Check nginx status: systemctl status nginx"
echo "  - View nginx logs: journalctl -u nginx -f"
echo "  - Test config: nginx -t"
echo "  - Reload nginx: systemctl reload nginx"
echo "  - Renew SSL: certbot renew"
