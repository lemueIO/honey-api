#!/bin/bash
# fix_uptime_kuma_display.sh
# Fixes the Uptime Kuma display issues by updating the CUSTOM Nginx Proxy Manager configuration.

CONTAINER_NAME="nginx-pm-app-1"
CUSTOM_CONF="/data/nginx/custom/server_proxy.conf"

echo "Checking custom config: $CUSTOM_CONF in container $CONTAINER_NAME..."

# Check if the custom config exists (it should, based on investigation)
if ! docker exec $CONTAINER_NAME test -f $CUSTOM_CONF; then
    echo "Error: Custom configuration file $CUSTOM_CONF not found."
    exit 1
fi

echo "Found custom config. Backing up..."
docker exec $CONTAINER_NAME cp $CUSTOM_CONF $CUSTOM_CONF.bak

# Function to add location block if missing
# This avoids duplicates by checking grep first
add_location_block() {
    local BLOCK_PATH=$1
    local CONTENT=$2
    
    echo "Checking for existing block for $BLOCK_PATH..."
    if docker exec $CONTAINER_NAME grep -q "location .*$BLOCK_PATH" $CUSTOM_CONF; then
        echo "Location $BLOCK_PATH already exists. Skipping..."
    else
        echo "Adding location $BLOCK_PATH..."
        docker exec $CONTAINER_NAME sh -c "cat >> $CUSTOM_CONF <<EOF

$CONTENT
EOF"
    fi
}

# 1. /upload/ (Fixes logo/icon)
add_location_block "/upload/" "location /upload/ {
    proxy_pass http://uptime-kuma:3001/upload/;
    proxy_set_header Host \$host;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \"upgrade\";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}"

# 2. /api/status-page/ (Fixes manifest/status data)
add_location_block "/api/status-page/" "location /api/status-page/ {
    proxy_pass http://uptime-kuma:3001/api/status-page/;
    proxy_set_header Host \$host;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \"upgrade\";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}"

# 3. /socket.io/ (Check if it exists, if not add it. Existing one might be fine but let's be sure)
# Note: The existing conf seemed to have /socket.io/ but broken? Or maybe valid.
add_location_block "/socket.io/" "location /socket.io/ {
    proxy_pass http://uptime-kuma:3001/socket.io/;
    proxy_set_header Host \$host;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection \"upgrade\";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}"

# Check syntax
echo "Checking Nginx configuration..."
if ! docker exec $CONTAINER_NAME nginx -t; then
    echo "ERROR: Nginx configuration test failed! Restoring backup..."
    docker exec $CONTAINER_NAME cp $CUSTOM_CONF.bak $CUSTOM_CONF
    docker exec $CONTAINER_NAME nginx -s reload
    exit 1
fi

# Reload Nginx
echo "Reloading Nginx..."
docker exec $CONTAINER_NAME nginx -s reload

echo "Done! Please verify access to https://$DOMAIN/cloud/"
