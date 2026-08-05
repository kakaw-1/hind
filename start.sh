#!/bin/bash
# Start the Bearer-auth proxy, then delegate to the image's default start-all.sh
# (which boots hindsight-api on $HINDSIGHT_API_PORT and skips CP).

/usr/bin/python3 /app/auth_proxy.py &
PROXY_PID=$!

# On shutdown, stop the proxy too (start-all.sh handles its own children).
trap 'kill $PROXY_PID 2>/dev/null; exit 0' TERM INT

# Use the default launcher so pg0 / external-DB / trap behavior is preserved.
exec /app/start-all.sh