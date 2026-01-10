#!/bin/bash
# fix_uptime_kuma_display.sh
# Fixes the Uptime Kuma display issues by rewriting the CUSTOM Nginx Proxy Manager configuration.

CONTAINER_NAME="nginx-pm-app-1"
CUSTOM_CONF="/data/nginx/custom/server_proxy.conf"

echo "Checking custom config: $CUSTOM_CONF in container $CONTAINER_NAME..."

echo "Found custom config. Backing up..."
# Backup current state (even if broken, good to have history)
docker exec $CONTAINER_NAME cp $CUSTOM_CONF $CUSTOM_CONF.broken_$(date +%s)

echo "Overwriting $CUSTOM_CONF with correct configuration..."

# We use cat -> file inside sh -c to ensure we write exactly what we want.
# We expect `proxy_pass http://uptime-kuma:3001` for the main cloud block.
# And `^~` blocks for the static assets.

# Note: We need to escape $host and other nginx variables so shell doesn't eat them.
# We do this by using a 'EOF' heredoc (quoted delimiter).

docker exec -i $CONTAINER_NAME sh -c "cat > $CUSTOM_CONF" <<'EOF'
location ^~ /cloud/ {
    rewrite ^/cloud/(.*) /$1 break;
    proxy_pass http://uptime-kuma:3001;
    proxy_redirect / /cloud/;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Fix subdirectory paths and routing
    # Enable filtering for JS, CSS, and JSON
    sub_filter_types text/html text/css application/javascript application/json;
    
    # Base tag for HTML
    sub_filter "<head>" "<head><base href=\"/cloud/\">";
    
    # Fix absolute asset paths in JS/HTML
    sub_filter "=\"/assets/" "=\"/cloud/assets/";
    sub_filter "=\"/manifest.json" "=\"/cloud/manifest.json";
    sub_filter "=\"/icon.svg" "=\"/cloud/icon.svg";
    sub_filter "=\"/apple-touch-icon.png" "=\"/cloud/apple-touch-icon.png";
    
    # Fix Vue Router Base Path
    # This patches the history initialization to use /cloud/ as the base
    # "history:ZG()" matches the minified code for this version
    sub_filter "history:ZG()" "history:ZG(\"/cloud/\")";
    
    # Remove previous route-specific hacks (they would cause double prefixing)
    # sub_filter "\"/dashboard\"" ... (REMOVED)
    
    # Fix API calls or other absolute paths if necessary
    # sub_filter "\"/api/\"" "\"/cloud/api/\"";
    
    sub_filter_once off;
}

location ^~ /cloud/socket.io/ {
    rewrite ^/cloud/(.*) /$1 break;
    proxy_pass http://uptime-kuma:3001;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
}

# Priority blocks to override assets.conf regexes
location ^~ /upload/ {
    proxy_pass http://uptime-kuma:3001/upload/;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

location ^~ /api/status-page/ {
    proxy_pass http://uptime-kuma:3001/api/status-page/;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

location ^~ /socket.io/ {
    proxy_pass http://uptime-kuma:3001/socket.io/;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_http_version 1.1;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
EOF

# Check syntax
echo "Checking Nginx configuration..."
if ! docker exec $CONTAINER_NAME nginx -t; then
    echo "ERROR: Nginx configuration test failed!"
    exit 1
fi

# Reload Nginx
echo "Reloading Nginx..."
docker exec $CONTAINER_NAME nginx -s reload

echo "Done! Please verify access to https://api.sec.lemue.org/cloud/"
