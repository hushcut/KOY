# KOY 가비아 Ubuntu 배포 가이드

이 구성은 가비아 지원 서버 1대에서 Nginx, Next.js, FastAPI, PostgreSQL을 운영합니다.

## 1. 배포 전 준비

- Ubuntu 서버
- 공인 IP 1개
- 공인 IP를 가리키는 도메인 또는 서브도메인
- 보안그룹 TCP 22, 80, 443
- OpenAI API 키

외부에 3000, 8000, 5432 포트를 열지 않습니다.

## 2. 서버 접속

```bash
ssh -i key.pem ubuntu@PUBLIC_IP
```

가비아 브라우저 터미널에서는 안내받은 계정과 관리자 비밀번호를 사용합니다.

## 3. 저장소 내려받기

```bash
sudo apt-get update
sudo apt-get install -y git
git clone --branch integration https://github.com/hushcut/KOY.git
cd KOY
```

## 4. 서버 기본 프로그램 설치

```bash
sudo bash deploy/scripts/01-bootstrap-ubuntu.sh
```

설치 후 Node.js 20 이상, Python, PostgreSQL, Nginx가 표시되는지 확인합니다.

## 5. DNS 연결

도메인 DNS에 A 레코드를 추가합니다.

```text
호스트: 사용할 서브도메인
값: 가비아 서버 공인 IP
```

아래 명령이 공인 IP를 반환할 때까지 기다립니다.

```bash
getent hosts YOUR_DOMAIN
```

## 6. 최초 배포

```bash
sudo bash deploy/scripts/02-first-deploy.sh
```

스크립트가 도메인과 OpenAI API 키를 요청합니다. API 키는 화면에 표시되지 않으며 `/opt/koy/app/backend/.env`에 권한 600으로 저장됩니다.

스크립트가 자동으로 수행하는 작업:

- `/opt/koy/app`에 저장소 설치
- PostgreSQL 계정과 DB 생성
- 안전한 DB 비밀번호 자동 생성
- 백엔드 가상환경과 의존성 설치
- Alembic 마이그레이션과 시드
- 프런트 의존성 설치와 프로덕션 빌드
- systemd 서비스 설치
- Nginx 리버스 프록시 설치

## 7. HTTPS 적용

DNS 연결과 HTTP 접속을 확인한 다음 실행합니다.

```bash
sudo certbot --nginx -d YOUR_DOMAIN --redirect
sudo certbot renew --dry-run
```

HTTPS 적용 후 휴대전화에서 QR 카메라를 확인합니다.

## 8. 상태 확인

```bash
sudo systemctl status koy-backend --no-pager
sudo systemctl status koy-frontend --no-pager
sudo nginx -t
curl http://127.0.0.1:8000/health
curl -I http://127.0.0.1:3000
curl -I https://YOUR_DOMAIN
```

로그 확인:

```bash
sudo journalctl -u koy-backend -n 100 --no-pager
sudo journalctl -u koy-frontend -n 100 --no-pager
```

## 9. 이후 업데이트

```bash
sudo bash /opt/koy/app/deploy/scripts/03-update-app.sh
```

`NEXT_PUBLIC_API_URL`은 `npm run build` 시 번들에 포함됩니다. 도메인을 변경하면 `/opt/koy/app/frontend/.env.production`을 수정한 후 업데이트 스크립트를 다시 실행합니다.

## 10. 발표 전 확인

- 홈 화면 HTTPS 접속
- `https://YOUR_DOMAIN/api/health` 응답
- QR 스캔과 시연 제품 대체 버튼
- 제품 검색
- 세 관심 주제 스토리
- 근거 있는 질문과 출처
- 근거 부족 질문
- 서버 재부팅 후 자동 실행

## 11. 백업

```bash
sudo -u postgres pg_dump koy | gzip > "$HOME/koy-$(date +%Y%m%d).sql.gz"
```

가비아 지원 종료 전 DB 백업 파일과 최신 Git 커밋을 로컬에 보관합니다.
