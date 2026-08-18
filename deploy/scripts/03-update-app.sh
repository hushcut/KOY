#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root: sudo bash /opt/koy/app/deploy/scripts/03-update-app.sh"
  exit 1
fi

APP_DIR="/opt/koy/app"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-integration}"

sudo -u koy git -C "${APP_DIR}" fetch origin "${DEPLOY_BRANCH}"
sudo -u koy git -C "${APP_DIR}" checkout "${DEPLOY_BRANCH}"
sudo -u koy git -C "${APP_DIR}" pull --ff-only origin "${DEPLOY_BRANCH}"

sudo -u koy "${APP_DIR}/backend/.venv/bin/python" -m pip install -r "${APP_DIR}/backend/requirements.txt"
sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/alembic upgrade head"
sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/python -m app.seed"

sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm ci"
sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm run build"

systemctl restart koy-backend koy-frontend
systemctl reload nginx

curl --fail --silent http://127.0.0.1:8000/health
echo
echo "KOY update complete."
