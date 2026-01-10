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

# 0. /cloud/
PATH_LOC="/cloud/"
PROXY="http://uptime-kuma:3001/"
if docker exec $CONTAINER_NAME grep -q "location .*$PATH_LOC" $CONF_FILE; then
    echo "Location $PATH_LOC exists. Updating proxy_pass..."
    # If it exists, we assume it might be the simple version, so we try to update it to include the subfolder fix
    # We replace the whole block start to try and inject headers if possible, or just the proxy_pass line
    # For safety/simplicity, let's just use the sed replace we had, but only if it exists
    docker exec $CONTAINER_NAME sed -i 's|location /cloud/ {|location /cloud/ {\n    proxy_set_header X-Real-IP $remote_addr;\n    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n    proxy_set_header Upgrade $http_upgrade;\n    proxy_set_header Connection "upgrade";\n    proxy_http_version 1.1;\n    proxy_pass http://uptime-kuma:3001/;|' $CONF_FILE
    # Also ensure trailing slash if passing to root
    docker exec $CONTAINER_NAME sed -i 's|proxy_pass http://uptime-kuma:3001;|proxy_pass http://uptime-kuma:3001/;|g' $CONF_FILE
else
    echo "Adding location $PATH_LOC..."
    docker exec $CONTAINER_NAME sed -i "\$i \\
  location $PATH_LOC {\\
    proxy_pass $PROXY;\\
    proxy_set_header Upgrade \$http_upgrade;\\
    proxy_set_header Connection \"upgrade\";\\
    proxy_http_version 1.1;\\
    proxy_set_header X-Real-IP \$remote_addr;\\
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
  }" $CONF_FILE
fi

echo "Adding extra location blocks for Uptime Kuma root support..."

echo "Adding extra location blocks for Uptime Kuma root support..."

# 1. /upload/
PATH_LOC="/upload/"
# grep for "location /upload" matches both /upload and /upload/
if docker exec $CONTAINER_NAME grep -q "location .*$PATH_LOC" $CONF_FILE; then
    echo "Location $PATH_LOC already exists. Skipping..."
else
    echo "Adding location $PATH_LOC..."
    PROXY="http://uptime-kuma:3001/upload/"
    docker exec $CONTAINER_NAME sed -i "\$i \\
  location $PATH_LOC {\\
    proxy_pass $PROXY;\\
    proxy_set_header Upgrade \$http_upgrade;\\
    proxy_set_header Connection \"upgrade\";\\
    proxy_http_version 1.1;\\
    proxy_set_header X-Real-IP \$remote_addr;\\
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
  }" $CONF_FILE
fi

# 2. /socket.io/
PATH_LOC="/socket.io/"
if docker exec $CONTAINER_NAME grep -q "location .*socket.io" $CONF_FILE; then
    echo "Location $PATH_LOC already exists. Skipping..."
else
    echo "Adding location $PATH_LOC..."
    PROXY="http://uptime-kuma:3001/socket.io/"
    docker exec $CONTAINER_NAME sed -i "\$i \\
  location $PATH_LOC {\\
    proxy_pass $PROXY;\\
    proxy_set_header Upgrade \$http_upgrade;\\
    proxy_set_header Connection \"upgrade\";\\
    proxy_http_version 1.1;\\
    proxy_set_header X-Real-IP \$remote_addr;\\
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
  }" $CONF_FILE
fi

# 3. /api/status-page/
PATH_LOC="/api/status-page/"
if docker exec $CONTAINER_NAME grep -q "location .*$PATH_LOC" $CONF_FILE; then
    echo "Location $PATH_LOC already exists. Skipping..."
else
    echo "Adding location $PATH_LOC..."
    PROXY="http://uptime-kuma:3001/api/status-page/"
    docker exec $CONTAINER_NAME sed -i "\$i \\
  location $PATH_LOC {\\
    proxy_pass $PROXY;\\
    proxy_set_header Upgrade \$http_upgrade;\\
    proxy_set_header Connection \"upgrade\";\\
    proxy_http_version 1.1;\\
    proxy_set_header X-Real-IP \$remote_addr;\\
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
  }" $CONF_FILE
fi

# Check syntax
echo "Checking Nginx configuration..."
if ! docker exec $CONTAINER_NAME nginx -t; then
    echo "ERROR: Nginx configuration test failed! Restoring backup..."
    docker exec $CONTAINER_NAME cp $CONF_FILE.bak $CONF_FILE
    docker exec $CONTAINER_NAME nginx -s reload
    exit 1
fi

# Reload Nginx
echo "Reloading Nginx..."
docker exec $CONTAINER_NAME nginx -s reload

echo "Done! Please verify access to https://$DOMAIN/cloud/"
