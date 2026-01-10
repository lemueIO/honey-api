#!/bin/bash
# fix_uptime_kuma_display.sh
# Fixes the Uptime Kuma display issues by updating Nginx Proxy Manager configuration.

CONTAINER_NAME="nginx-pm-app-1"
DOMAIN="api.sec.lemue.org"

echo "Searching for Nginx config for $DOMAIN in container $CONTAINER_NAME..."

# Find the config file inside the container
# We use sh -c to ensure the glob expansion happens inside the container
CONF_FILE=$(docker exec $CONTAINER_NAME sh -c "grep -l 'server_name .*$DOMAIN' /data/nginx/proxy_host/*.conf" | head -n 1)

if [ -z "$CONF_FILE" ]; then
  # Try checking just the directory listing to debug if needed
  # docker exec $CONTAINER_NAME ls -la /data/nginx/proxy_host/
  echo "Error: Configuration file for $DOMAIN not found. (Glob expansion failed to match)"
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

# Alternative: Replace `proxy_pass http://uptime-kuma:3001;` with `proxy_pass http://uptime-kuma:3001/;`
docker exec $CONTAINER_NAME sed -i 's|proxy_pass http://uptime-kuma:3001;|proxy_pass http://uptime-kuma:3001/;|g' $CONF_FILE

echo "Adding extra location blocks for Uptime Kuma root support..."

# Function to add location block if missing
add_location_block() {
    local PATH=$1
    local PROXY_PASS=$2
    
    # Check if location block already exists to avoid duplication
    if docker exec $CONTAINER_NAME grep -q "location $PATH" $CONF_FILE; then
        echo "Location $PATH already exists. Skipping..."
    else
        echo "Adding location $PATH..."
        # Insert before the last closing brace (assuming it ends the server block)
        # We search for the last line consisting of just "}" or similar, simplifying by appending to file end but before last }
        # Actually, let's use a specialized sed to insert before the very last line
        docker exec $CONTAINER_NAME sed -i "\$i \\
  location $PATH {\\
    proxy_pass $PROXY_PASS;\\
    proxy_set_header Upgrade \$http_upgrade;\\
    proxy_set_header Connection \"upgrade\";\\
    proxy_http_version 1.1;\\
    proxy_set_header X-Real-IP \$remote_addr;\\
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
  }" $CONF_FILE
    fi
}

add_location_block "/upload/" "http://uptime-kuma:3001/upload/"
add_location_block "/socket.io/" "http://uptime-kuma:3001/socket.io/"
add_location_block "/api/status-page/" "http://uptime-kuma:3001/api/status-page/"

# Check syntax
echo "Checking Nginx configuration..."
docker exec $CONTAINER_NAME nginx -t

# Reload Nginx
echo "Reloading Nginx..."
docker exec $CONTAINER_NAME nginx -s reload

echo "Done! Please verify access to https://$DOMAIN/cloud/"
