# Hindsight on Hugging Face Spaces — full image with local multilingual embeddings
# HF Spaces health-check expects the container to listen on port 7860.
# Hindsight API listens on 8000 by default → socat forwards 7860 → 8000.
FROM ghcr.io/vectorize-io/hindsight:latest

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 7860
CMD ["sh", "-c", "socat TCP-LISTEN:7860,fork,reuseaddr TCP:127.0.0.1:8000 & hindsight-api"]
