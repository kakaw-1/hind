# Hindsight on Hugging Face Spaces — full image
# Architecture: auth_proxy.py (Bearer gate) on :7860 → hindsight-api on :8888
# Why: Hindsight OSS API (0.8.x) has no built-in auth; HF Spaces expose the
# container publicly, so we front it with a tiny Bearer-auth reverse proxy.
# Hermes & the Control Plane both send `Authorization: Bearer <token>`, so
# this one token protects the whole API.
FROM ghcr.io/vectorize-io/hindsight:latest

# API stays on its default port; the proxy owns :7860 (HF health-check port).
ENV HINDSIGHT_API_PORT=8888
ENV HINDSIGHT_ENABLE_CP=false

# Bearer-auth reverse proxy (python3 stdlib, zero deps)
COPY --chown=1000:1000 auth_proxy.py /app/auth_proxy.py
# Runtime token: set HINDSIGHT_AUTH_TOKEN in the HF Space env (or build arg).
ENV HINDSIGHT_AUTH_TOKEN=change-me

COPY --chown=1000:1000 start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 7860
CMD ["/app/start.sh"]