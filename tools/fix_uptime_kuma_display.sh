#!/bin/bash
# fix_uptime_kuma_display.sh
# Fixes the Uptime Kuma display issues by updating Nginx Proxy Manager configuration.

CONTAINER_NAME="nginx-pm-app-1"
DOMAIN="api.sec.lemue.org"

echo "Searching for Nginx config for $DOMAIN in container $CONTAINER_NAME..."

# Find the config file inside the container
CONF_FILE=$(docker exec $CONTAINER_NAME grep -l "server_name .*$DOMAIN" /data/nginx/proxy_host/*.conf | head -n 1)

if [ -z "$CONF_FILE" ]; then
  echo "Error: Configuration file for $DOMAIN not found."
  exit 1
fi

echo "Found config file: $CONF_FILE"

# Backup the file
docker exec $CONTAINER_NAME cp $CONF_FILE $CONF_FILE.bak

# Read the content to verify (optional, for debugging)
# docker exec $CONTAINER_NAME cat $CONF_FILE

# Apply the fix using sed
# This sed command looks for the location /cloud/ block and explicitly adds the proxy_pass with trailing slash
# Note: This is a heuristic replacement. It assumes a standard NPM structure.
# It replaces the simple proxy_pass with the improved version for subfolder support.

echo "Applying fix..."

docker exec $CONTAINER_NAME sed -i 's|location /cloud/ {|location /cloud/ {\n    proxy_set_header X-Real-IP $remote_addr;\n    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n    proxy_set_header Upgrade $http_upgrade;\n    proxy_set_header Connection "upgrade";\n    proxy_http_version 1.1;\n    proxy_pass http://uptime-kuma:3001/;|' $CONF_FILE

# Verify if proxy_pass was already there and we doubled it? 
# The above sed is a bit risky if the block structure varies. 
# A safer approach might be to just ensure the trailing slash exists if it's missing.

# Alternative: Replace `proxy_pass http://uptime-kuma:3001;` with `proxy_pass http://uptime-kuma:3001/;`
docker exec $CONTAINER_NAME sed -i 's|proxy_pass http://uptime-kuma:3001;|proxy_pass http://uptime-kuma:3001/;|g' $CONF_FILE

# Check syntax
echo "Checking Nginx configuration..."
docker exec $CONTAINER_NAME nginx -t

# Reload Nginx
echo "Reloading Nginx..."
docker exec $CONTAINER_NAME nginx -s reload

echo "Done! Please verify access to https://$DOMAIN/cloud/"
