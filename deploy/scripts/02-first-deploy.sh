#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this script as root: sudo bash deploy/scripts/02-first-deploy.sh"
  exit 1
fi

APP_DIR="/opt/koy/app"
REPOSITORY_URL="${REPOSITORY_URL:-https://github.com/hushcut/KOY.git}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-integration}"

read -r -p "Public host (domain or IP, example: 1.201.116.192): " KOY_HOST
if [[ -z "${KOY_HOST}" || "${KOY_HOST}" == *"/"* || "${KOY_HOST}" == *" "* ]]; then
  echo "Enter a hostname or IP only, without http://, https://, or a path."
  exit 1
fi

read -r -s -p "OpenAI API key: " OPENAI_API_KEY
echo
if [[ -z "${OPENAI_API_KEY}" ]]; then
  echo "OpenAI API key is required."
  exit 1
fi

if [[ ! -d "${APP_DIR}/.git" ]]; then
  sudo -u koy git clone --branch "${DEPLOY_BRANCH}" --single-branch "${REPOSITORY_URL}" "${APP_DIR}"
else
  sudo -u koy git -C "${APP_DIR}" fetch origin "${DEPLOY_BRANCH}"
  sudo -u koy git -C "${APP_DIR}" checkout "${DEPLOY_BRANCH}"
  sudo -u koy git -C "${APP_DIR}" pull --ff-only origin "${DEPLOY_BRANCH}"
fi

DB_PASSWORD="$(openssl rand -hex 24)"

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='koy_user'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE ROLE koy_user LOGIN"
fi
sudo -u postgres psql -c "ALTER ROLE koy_user WITH PASSWORD '${DB_PASSWORD}'"

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='koy'" | grep -q 1; then
  sudo -u postgres createdb --owner=koy_user koy
fi

umask 077
cat > "${APP_DIR}/backend/.env" <<EOF
DATABASE_URL=postgresql+psycopg://koy_user:${DB_PASSWORD}@127.0.0.1:5432/koy
OPENAI_API_KEY=${OPENAI_API_KEY}
OPENAI_MODEL=gpt-5-mini
FRONTEND_ORIGIN=http://${KOY_HOST}
EOF

cat > "${APP_DIR}/frontend/.env.production" <<EOF
NEXT_PUBLIC_API_URL=/api
EOF

chown koy:koy "${APP_DIR}/backend/.env" "${APP_DIR}/frontend/.env.production"

sudo -u koy python3 -m venv "${APP_DIR}/backend/.venv"
sudo -u koy "${APP_DIR}/backend/.venv/bin/python" -m pip install --upgrade pip
sudo -u koy "${APP_DIR}/backend/.venv/bin/python" -m pip install -r "${APP_DIR}/backend/requirements.txt"

sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/alembic upgrade head"
sudo -u koy bash -c "cd '${APP_DIR}/backend' && .venv/bin/python -m app.seed"

sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm ci"
sudo -u koy bash -c "cd '${APP_DIR}/frontend' && npm run build"

install -m 0644 "${APP_DIR}/deploy/systemd/koy-backend.service" /etc/systemd/system/koy-backend.service
install -m 0644 "${APP_DIR}/deploy/systemd/koy-frontend.service" /etc/systemd/system/koy-frontend.service
sed "s/__DOMAIN__/${KOY_HOST}/g" "${APP_DIR}/deploy/nginx/koy.conf" > /etc/nginx/sites-available/koy
ln -sfn /etc/nginx/sites-available/koy /etc/nginx/sites-enabled/koy
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl daemon-reload
systemctl enable --now koy-backend koy-frontend
systemctl reload nginx

echo "HTTP deployment complete: http://${KOY_HOST}"
echo "If you connect a domain later, update FRONTEND_ORIGIN and enable HTTPS with certbot."
