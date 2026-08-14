ARG QUARTO_IMAGE=ghcr.io/quarto-dev/quarto:1.9.38
FROM ${QUARTO_IMAGE}

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends xz-utils \
    && rm -rf /var/lib/apt/lists/*

