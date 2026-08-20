# Provenance

제품의 QR을 통해 검수된 공식 자료를 확인하고, 근거 기반 AI 도슨트와 대화하는 멋쟁이사자처럼 캡스톤 웹앱입니다.

## 배포 주소

- 웹앱: <http://1.201.116.192>
- 상태 확인: <http://1.201.116.192/api/health>

현재 가비아 Ubuntu 서버의 공인 IP로 운영합니다. HTTP 환경에서는 브라우저 카메라 정책상 QR 촬영이 제한될 수 있어 `카메라 없이 시연 제품 보기` 경로를 함께 제공합니다.

## 해결하려는 문제

제품 설명은 판매 정보에 치우치기 쉽고, 사용자는 소재·제작 방식·디자인 배경의 출처를 확인하기 어렵습니다. Provenance는 등록된 공식 아카이브만 AI의 근거로 제공하고, 자료에 없는 내용은 추측하지 않도록 설계했습니다.

## 핵심 기능

- QR 코드 또는 제품명으로 제품 식별
- 소재, 제작·구성, 브랜드 이야기별 공식 자료 조회
- 공식 자료를 바탕으로 한 AI 도슨트 스토리 생성
- 대화 맥락이 누적되는 후속 Q&A
- 답변에 사용한 출처 표시
- 자료에 없는 질문에 대한 근거 부족 안내
- AI 장애 시 DB 공식 자료 기반 폴백

## 시연 순서

1. 홈에서 `제품 스캔하기` 선택
2. HTTP 환경에서는 `카메라 없이 시연 제품 보기` 선택
3. 식별된 제품의 헤리티지 확인
4. `소재 / 장인 공정 / 브랜드 역사` 주제 전환
5. 도슨트 스토리와 추천 질문 실행
6. `가격이 얼마인가요?` 질문으로 근거 부족 안전장치 확인

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | Next.js 16, React, TypeScript, CSS |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL |
| AI | OpenAI Responses API, Structured Outputs |
| Infra | Ubuntu 24.04, Nginx, systemd, Gabia Cloud |

## 구조

```text
Browser
  └─ Nginx :80
      ├─ /      → Next.js :3000
      └─ /api/* → FastAPI :8000
                    ├─ PostgreSQL :5432
                    └─ OpenAI API
```

`3000`, `8000`, `5432` 포트는 외부에 공개하지 않고 Nginx와 서버 내부 통신에만 사용합니다.

## 저장소 구성

```text
frontend/   Next.js 방문객 웹앱
backend/    FastAPI API, DB 모델, 마이그레이션, 테스트
deploy/     Ubuntu 설치·배포·업데이트 스크립트와 Nginx/systemd 설정
```

## 로컬 실행

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

로컬 웹앱은 <http://localhost:3000>, API 문서는 <http://localhost:8000/docs>에서 확인합니다.

## 환경변수

Backend:

```env
DATABASE_URL=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
FRONTEND_ORIGIN=http://localhost:3000
```

Frontend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

실제 `.env` 파일과 API 키는 Git에 커밋하지 않습니다.

## 주요 API

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/health` | 서버 상태 확인 |
| GET | `/products/by-qr/{qr_value}` | QR 제품 조회 |
| GET | `/products/search?q=` | 제품 검색 |
| GET | `/products/{id}/heritage` | 공식 헤리티지 조회 |
| POST | `/docent/story` | 주제 기반 도슨트 스토리 생성 |
| POST | `/docent/sessions/{id}/messages` | 근거 기반 후속 질문 |

## 검증

```bash
cd backend && python -m pytest
cd frontend && npm run lint && npm run build
```

모바일 기준 화면은 `375 × 812`에서 검증합니다. 상세 디자인 검증 결과는 [`frontend/design-qa.md`](frontend/design-qa.md)에 기록되어 있습니다.

## 배포 및 업데이트

최초 배포와 운영 명령은 [`deploy/README.md`](deploy/README.md)를 참고합니다. `main`의 검증된 변경을 서버에 반영할 때는 다음을 실행합니다.

```bash
sudo bash /opt/koy/app/deploy/scripts/03-update-app.sh
```

평가 제출본과 운영 서버는 `main` 브랜치를 기준으로 유지합니다.

## 팀 역할

- 기획·디자인: 사용자 흐름, Figma, 콘텐츠 및 발표 시나리오
- 프런트엔드·백엔드: Next.js UI, API 연동, 통합 QA
- 백엔드: FastAPI, PostgreSQL, AI 근거 처리, 배포 운영
