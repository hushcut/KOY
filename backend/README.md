# KOY Backend

KOY 제품 헤리티지 도슨트 서비스의 FastAPI 백엔드입니다.

## 기술 스택

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- pytest
- OpenAI Responses API

## 실행 방법

### 1. 가상환경 생성

```powershell
python -m venv .venv
```

### 2. 가상환경 활성화

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 패키지 설치

```powershell
pip install -r requirements.txt
```

## PostgreSQL 설정

PostgreSQL에 `koy` 데이터베이스를 생성합니다.

```sql
CREATE DATABASE koy;
```

프로젝트의 `.env.example`을 참고하여 `.env` 파일을 생성합니다.

예시:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/koy
OPENAI_API_KEY=
OPENAI_MODEL=
FRONTEND_ORIGIN=http://localhost:3000
```

실제 DB 사용자명과 비밀번호에 맞게 수정합니다.

PostgreSQL이 준비되지 않은 로컬 시연 환경에서는 `.env`를 만들지 않으면 `sqlite:///./koy.db`가 자동으로 사용됩니다.

`.env` 파일은 Git에 커밋하지 않습니다.

## DB 마이그레이션

Alembic migration을 PostgreSQL에 적용합니다.

```powershell
alembic upgrade head
```

모델 변경 후 새로운 migration이 필요한 경우:

```powershell
alembic revision --autogenerate -m "migration description"
alembic upgrade head
```

## 시연 데이터 생성

```powershell
python -m app.seed
```

시드 스크립트는 여러 번 실행해도 동일한 시연 제품이 중복 생성되지 않도록 구현되어 있습니다.

## 서버 실행

```powershell
uvicorn app.main:app --reload
```

서버 주소:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## 테스트

```powershell
python -m pytest
```

현재 주요 API와 오류 처리 테스트를 포함하고 있습니다.

## 주요 API

- `GET /health`
- `GET /products/by-qr/{qr_value}`
- `GET /products/search?q=`
- `GET /products/{product_id}/heritage`
- `POST /docent/story`
- `POST /docent/sessions/{session_id}/messages`

## 관심 주제

`interest`는 아래 세 값만 사용할 수 있습니다.

- `material`: 소재
- `craftsmanship`: 장인 공정
- `brand_history`: 브랜드 역사

## 오류 형식

공통 오류 응답은 아래 형식을 사용합니다.

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "제품을 찾을 수 없습니다."
  }
}
```

주요 오류 코드:

- `PRODUCT_NOT_FOUND`
- `SESSION_NOT_FOUND`
- `HERITAGE_NOT_FOUND`
- `INVALID_INTEREST`
- `INVALID_REQUEST`
- `INTERNAL_SERVER_ERROR`

OpenAI 연동 후 아래 오류 코드가 추가될 예정입니다.

- `AI_SERVICE_ERROR`

## 현재 구현 상태

현재 PostgreSQL과 Alembic 기반의 백엔드 MVP가 구현되어 있습니다.

제품 조회, 검색, 헤리티지 조회, 도슨트 세션 생성, 누적 Q&A, 근거 여부 판별 및 출처 반환이 구현되어 있습니다.

`OPENAI_API_KEY`가 설정되면 OpenAI Responses API를 사용하여 DB의 `PUBLISHED` 공식 헤리티지 콘텐츠와 최근 세션 대화만 기반으로 답변합니다. API 키가 없는 로컬 환경에서는 발표 및 테스트가 가능하도록 동일한 응답 계약의 근거 기반 로컬 로직으로 동작합니다.

`FRONTEND_ORIGIN`에는 쉼표로 구분한 여러 주소를 입력할 수 있습니다.

```env
FRONTEND_ORIGIN=http://localhost:3000,https://your-app.vercel.app
```
