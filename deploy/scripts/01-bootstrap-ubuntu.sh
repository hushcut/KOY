#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root: sudo bash deploy/scripts/01-bootstrap-ubuntu.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  ca-certificates \
  curl \
  git \
  nginx \
  openssl \
  postgresql \
  postgresql-contrib \
  python3 \
  python3-pip \
  python3-venv \
  python3-certbot-nginx

if ! command -v node >/dev/null 2>&1 || [[ "$(node -p 'Number(process.versions.node.split(`.`)[0])')" -lt 20 ]]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  apt-get install -y nodejs
fi

if ! id koy >/dev/null 2>&1; then
  useradd --create-home --home-dir /opt/koy --shell /bin/bash koy
fi

install -d -o koy -g koy -m 0755 /opt/koy

systemctl enable --now nginx
systemctl enable --now postgresql

echo "Bootstrap complete. Node: $(node --version), npm: $(npm --version), Python: $(python3 --version)"
