# Hindsight Control Plane UI — separate HF Space (Space B)
# Connects to the API in Space A via HINDSIGHT_CP_DATAPLANE_API_URL.
# UI login is protected by HINDSIGHT_CP_ACCESS_KEY (built-in CP auth).
FROM ghcr.io/vectorize-io/hindsight:latest

# Only the Control Plane; no API, no embedded DB.
ENV HINDSIGHT_ENABLE_API=false
ENV HINDSIGHT_ENABLE_CP=true
ENV HINDSIGHT_CP_PORT=7860

# --- Set these in the HF Space B env (never hardcode secrets) ---
# HINDSIGHT_CP_DATAPLANE_API_URL=https://<space-a>.hf.space
# HINDSIGHT_CP_DATAPLANE_API_KEY=<same Bearer token as Space A>
# HINDSIGHT_CP_ACCESS_KEY=<UI login key>

EXPOSE 7860
# Default CMD (/app/start-all.sh) starts CP on $HINDSIGHT_CP_PORT.
