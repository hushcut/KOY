#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root: sudo bash /opt/koy/app/deploy/scripts/03-update-app.sh"
  exit 1
fi

APP_DIR="/opt/koy/app"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"

sudo -u koy git -C "${APP_DIR}" config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
sudo -u koy git -C "${APP_DIR}" fetch origin "${DEPLOY_BRANCH}"
if sudo -u koy git -C "${APP_DIR}" show-ref --verify --quiet "refs/heads/${DEPLOY_BRANCH}"; then
  sudo -u koy git -C "${APP_DIR}" checkout "${DEPLOY_BRANCH}"
else
  sudo -u koy git -C "${APP_DIR}" checkout -b "${DEPLOY_BRANCH}" --track "origin/${DEPLOY_BRANCH}"
fi
sudo -u koy git -C "${APP_DIR}" pull --ff-only origin "${DEPLOY_BRANCH}"

sudo -u koy "${APP_DIR}/backend/.venv/bin/python" -m pip install -r "${APP_DIR}/backend/requirements.txt"
sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/alembic upgrade head"
sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/python -m app.seed"

sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm ci"
sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm run build"

FRONTEND_ORIGIN="$(sed -n 's/^FRONTEND_ORIGIN=//p' "${APP_DIR}/backend/.env" | head -n 1)"
KOY_HOST="${FRONTEND_ORIGIN#*://}"
KOY_HOST="${KOY_HOST%%/*}"
if [[ -z "${KOY_HOST}" ]]; then
  echo "Could not determine the public host from backend/.env"
  exit 1
fi

install -d -m 0755 /var/www/certbot/.well-known/acme-challenge
CERTIFICATE_DIR="/etc/letsencrypt/live/${KOY_HOST}"
if [[ -f "${CERTIFICATE_DIR}/fullchain.pem" && -f "${CERTIFICATE_DIR}/privkey.pem" ]]; then
  sed -i "s|^FRONTEND_ORIGIN=.*$|FRONTEND_ORIGIN=https://${KOY_HOST}|" "${APP_DIR}/backend/.env"
  chown koy:koy "${APP_DIR}/backend/.env"
  sed "s/__DOMAIN__/${KOY_HOST}/g" "${APP_DIR}/deploy/nginx/koy-https.conf" > /etc/nginx/sites-available/koy
else
  sed "s/__DOMAIN__/${KOY_HOST}/g" "${APP_DIR}/deploy/nginx/koy.conf" > /etc/nginx/sites-available/koy
fi
nginx -t
systemctl restart koy-backend koy-frontend
systemctl reload nginx

curl --fail --silent http://127.0.0.1:8000/health
echo
echo "KOY update complete."
