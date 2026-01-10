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
    local LOC_MODIFIER=$3 # Optional modifier like ^~
    
    # We grep for the path. We must be careful if modifier changes.
    # We check for "location .*PATH"
    echo "Checking for existing block for $BLOCK_PATH..."
    if docker exec $CONTAINER_NAME grep -q "location .*$BLOCK_PATH" $CUSTOM_CONF; then
        echo "Location $BLOCK_PATH already exists. Update or Manual check required? Assuming it's the old weak one and appending new one might duplicate but Nginx warns on dupes."
        # If we want to replace, we should probably delete the old one first?
        # Automating deletion is risky with simple sed.
        # But if we use ^~ it might conflict with the old one if it's there?
        # Nginx doesn't allow duplicate locations for same path prefix usually.
        # Let's try to remove the old one if it lacks the modifier?
        # For safety/simplicity in this context: 
        # Since I am just fixing it, I will assume the previous script runs added the weak ones.
        # I should probably clear the file or try to remove them.
        # BUT, the file might contain other stuff?
        # The file is `server_proxy.conf`. It contained `/cloud/` block initially.
        # Then I appended `/upload/` etc.
        # I should revert to .bak if it exists?
        # The script creates a .bak every time. So it might have overwritten the clean backup.
        # Let's just append. If duplicates occur, Nginx fails test, restores backup.
        # Wait, if Nginx fails, script exits.
        # So I need to be careful.
        
        # Heuristic: If grep finds it, we skip.
        # BUT I NEED TO CHANGE IT TO ^~
        # So I will skip if "location ^~ ...PATH" exists.
        if docker exec $CONTAINER_NAME grep -q "location \^~ $BLOCK_PATH" $CUSTOM_CONF; then
             echo "Priority Location $BLOCK_PATH already exists. Skipping..."
             return
        fi
        
        # If simple location exists but priority doesn't?
        # We should probably comment it out or just append the new one and see if Nginx complains?
        # Nginx complains about duplicate locations.
        echo "Found existing weak location for $BLOCK_PATH. Attempting to comment it out or just appending priority one..."
        # Let's just clear the file to the initial state? Risky.
        # Let's use sed to comment out lines starting with "location /upload/"?
        docker exec $CONTAINER_NAME sed -i "s|location $BLOCK_PATH|# location $BLOCK_PATH|g" $CUSTOM_CONF
    fi

    echo "Adding priority location $BLOCK_PATH..."
    # Expansion of variables inside heredoc
    docker exec -e BLOCK_PATH="$BLOCK_PATH" -e PROXY_URL="$PROXY_URL" -e LOC_MODIFIER="$LOC_MODIFIER" $CONTAINER_NAME sh -c 'cat >> $CUSTOM_CONF <<EOF

location $LOC_MODIFIER $BLOCK_PATH {
    proxy_pass $PROXY_URL;
    proxy_set_header Host \$host;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
}
EOF'
}

# 1. /upload/
add_location_block "/upload/" "http://uptime-kuma:3001/upload/" "^~"

# 2. /api/status-page/
add_location_block "/api/status-page/" "http://uptime-kuma:3001/api/status-page/" "^~"

# 3. /socket.io/
add_location_block "/socket.io/" "http://uptime-kuma:3001/socket.io/" "^~"


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
