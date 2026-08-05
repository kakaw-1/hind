# Hindsight on Hugging Face Spaces — full image, port adapted for HF health-check
# Root cause fix: Hindsight API defaults to port 8888, but HF Spaces requires the
# container to listen on 7860. So we point the API directly at 7860 (no proxy).
FROM ghcr.io/vectorize-io/hindsight:latest

# HF Spaces health-check expects 7860; Hindsight default is 8888 → override.
ENV HINDSIGHT_API_PORT=7860

# Only the API. We use external PostgreSQL (Aiven) for the database,
# so the embedded pg0 and the Node.js Control Plane are not needed.
ENV HINDSIGHT_ENABLE_CP=false

# Must be set at runtime (HF Space env var), or start-all.sh aborts on the
# embedded-pg0 writability check:
#   HINDSIGHT_API_DATABASE_URL=postgresql://user:pass@host:5432/dbname
ENV HINDSIGHT_ENABLE_API=true

# Keep the image's default CMD (/app/start-all.sh): it starts `hindsight-api`
# on $HINDSIGHT_API_PORT and skips the Control Plane when HINDSIGHT_ENABLE_CP=false.

EXPOSE 7860