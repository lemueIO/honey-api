#!/bin/bash
# fix_uptime_kuma_display.sh
# Fixes the Uptime Kuma display issues by updating the CUSTOM Nginx Proxy Manager configuration.

CONTAINER_NAME="nginx-pm-app-1"
CUSTOM_CONF="/data/nginx/custom/server_proxy.conf"

echo "Checking custom config: $CUSTOM_CONF in container $CONTAINER_NAME..."

if ! docker exec $CONTAINER_NAME test -f $CUSTOM_CONF; then
    echo "Error: Custom configuration file $CUSTOM_CONF not found."
    exit 1
fi

echo "Found custom config. Backing up..."
docker exec $CONTAINER_NAME cp $CUSTOM_CONF $CUSTOM_CONF.bak

# Function to add location block
add_location_block() {
    local BLOCK_PATH=$1
    local PROXY_URL=$2
    
    echo "Checking for existing block for $BLOCK_PATH..."
    if docker exec $CONTAINER_NAME grep -q "location .*$BLOCK_PATH" $CUSTOM_CONF; then
        echo "Location $BLOCK_PATH already exists. Skipping..."
    else
        echo "Adding location $BLOCK_PATH..."
        # Use environment variables to pass dynamic values safely
        # Use single quotes for sh -c to prevent local expansion
        # Inside the single-quoted string, we write the HEREDOC
        # We use \ to escape $host etc. inside the HEREDOC, because the remote shell will process the HEREDOC.
        docker exec -e BLOCK_PATH="$BLOCK_PATH" -e PROXY_URL="$PROXY_URL" -e CUSTOM_CONF="$CUSTOM_CONF" $CONTAINER_NAME sh -c 'cat >> $CUSTOM_CONF <<EOF

location $BLOCK_PATH {
    proxy_pass $PROXY_URL;
    proxy_set_header Host \$host;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}
EOF'
    fi
}

# 1. /upload/
add_location_block "/upload/" "http://uptime-kuma:3001/upload/"

# 2. /api/status-page/
add_location_block "/api/status-page/" "http://uptime-kuma:3001/api/status-page/"

# 3. /socket.io/
add_location_block "/socket.io/" "http://uptime-kuma:3001/socket.io/"


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

echo "Done! Please verify access to https://api.sec.lemue.org/cloud/"
