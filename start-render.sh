#!/bin/bash
# Render launcher: auth proxy on $PORT (Render injects) → API on 8888.
# Delegates to the image's default start-all.sh (boots hindsight-api on
# $HINDSIGHT_API_PORT and skips CP).

/usr/bin/python3 /app/auth_proxy.py &
PROXY_PID=$!

trap 'kill $PROXY_PID 2>/dev/null; exit 0' TERM INT

exec /app/start-all.sh
