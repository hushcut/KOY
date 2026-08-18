from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import (
    Product,
    HeritageContent,
    HeritageStatus,
    HeritageTopic,
    DocentSession,
    DocentMessage,
    MessageRole,
)
from app.services.docent_service import answer_question, generate_story


# =========================================================
# FastAPI
# =========================================================

app = FastAPI(
    title="KOY Backend API",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# 공통 오류
# =========================================================

class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message


@app.exception_handler(APIError)
async def api_error_handler(
    request: Request,
    exc: APIError,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = exc.errors()

    for error in errors:
        if "interest" in error.get("loc", []):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_INTEREST",
                        "message": (
                            "interest는 material, craftsmanship, "
                            "brand_history 중 하나여야 합니다."
                        ),
                    }
                },
            )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "잘못된 요청입니다.",
            }
        },
    )


@app.exception_handler(Exception)
async def internal_error_handler(
    request: Request,
    exc: Exception,
):
    print(f"Internal server error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            }
        },
    )


# =========================================================
# Request Schema
# =========================================================

class DocentStoryRequest(BaseModel):
    productId: str
    interest: HeritageTopic


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("질문을 입력해 주세요.")

        return value


# =========================================================
# 1. 상태 확인
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================================================
# 2. QR 제품 조회
# =========================================================

@app.get("/products/by-qr/{qr_value}")
def get_product_by_qr(
    qr_value: str,
    db: Session = Depends(get_db),
):
    product = db.scalar(
        select(Product).where(
            Product.qr_value == qr_value
        )
    )

    if product is None:
        raise APIError(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="제품을 찾을 수 없습니다.",
        )

    return {
        "id": product.id,
        "qrValue": product.qr_value,
        "brandName": product.brand_name,
        "productName": product.product_name,
        "summary": product.summary,
        "imageUrl": product.image_url,
    }


# =========================================================
# 3. 제품 검색
# =========================================================

@app.get("/products/search")
def search_products(
    q: str = Query(
        min_length=1,
        max_length=100,
    ),
    db: Session = Depends(get_db),
):
    search_query = q.strip()

    if not search_query:
        raise APIError(
            status_code=400,
            code="INVALID_REQUEST",
            message="검색어를 입력해 주세요.",
        )

    products = db.scalars(
        select(Product).where(
            or_(
                Product.brand_name.ilike(
                    f"%{search_query}%"
                ),
                Product.product_name.ilike(
                    f"%{search_query}%"
                ),
            )
        )
    ).all()

    return {
        "items": [
            {
                "id": product.id,
                "qrValue": product.qr_value,
                "brandName": product.brand_name,
                "productName": product.product_name,
                "summary": product.summary,
                "imageUrl": product.image_url,
            }
            for product in products
        ]
    }


# =========================================================
# 4. 제품 헤리티지 조회
# =========================================================

@app.get("/products/{product_id}/heritage")
def get_product_heritage(
    product_id: str,
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        product_id,
    )

    if product is None:
        raise APIError(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="제품을 찾을 수 없습니다.",
        )

    heritage_items = db.scalars(
        select(HeritageContent).where(
            HeritageContent.product_id == product_id,
            HeritageContent.status
            == HeritageStatus.PUBLISHED,
        )
    ).all()

    return {
        "productId": product.id,
        "items": [
            {
                "id": item.id,
                "topic": item.topic.value,
                "title": item.title,
                "content": item.content,
                "sourceTitle": item.source_title,
                "sourceUrl": item.source_url,
            }
            for item in heritage_items
        ],
    }


# =========================================================
# 5. 관심 주제 기반 도슨트 스토리
#
# OpenAI 연결 전 임시 구현
# =========================================================

@app.post("/docent/story")
def create_docent_story(
    request: DocentStoryRequest,
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        request.productId,
    )

    if product is None:
        raise APIError(
            status_code=404,
            code="PRODUCT_NOT_FOUND",
            message="제품을 찾을 수 없습니다.",
        )

    heritage_items = db.scalars(
        select(HeritageContent).where(
            HeritageContent.product_id
            == request.productId,
            HeritageContent.topic
            == request.interest,
            HeritageContent.status
            == HeritageStatus.PUBLISHED,
        )
    ).all()

    if not heritage_items:
        raise APIError(
            status_code=404,
            code="HERITAGE_NOT_FOUND",
            message=(
                "선택한 관심 주제의 "
                "헤리티지 자료가 없습니다."
            ),
        )

    docent_session = DocentSession(
        product_id=request.productId,
        interest=request.interest,
    )

    db.add(docent_session)
    db.commit()
    db.refresh(docent_session)

    try:
        generated = generate_story(
            product_name=product.product_name,
            interest=request.interest,
            items=heritage_items,
        )
    except Exception as exc:
        print(f"AI story generation failed: {exc}")
        raise APIError(
            status_code=503,
            code="AI_SERVICE_ERROR",
            message="도슨트 스토리를 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    sources = [
        {
            "title": item.source_title,
            "url": item.source_url,
        }
        for item in heritage_items
    ]

    return {
        "sessionId": docent_session.id,
        "title": generated.title,
        "story": generated.story,
        "suggestedQuestions": generated.suggested_questions,
        "sources": sources,
    }


# =========================================================
# 6. 세션 기반 누적 Q&A
#
# OpenAI 연결 전 임시 구현
# =========================================================

@app.post("/docent/sessions/{session_id}/messages")
def ask_docent(
    session_id: str,
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    docent_session = db.get(
        DocentSession,
        session_id,
    )

    if docent_session is None:
        raise APIError(
            status_code=404,
            code="SESSION_NOT_FOUND",
            message="세션을 찾을 수 없습니다.",
        )

    # 사용자 질문 저장
    user_message = DocentMessage(
        session_id=session_id,
        role=MessageRole.USER,
        content=request.question,
        grounded=None,
    )

    db.add(user_message)

    # PUBLISHED 공식 자료만 사용
    heritage_items = db.scalars(
        select(HeritageContent).where(
            HeritageContent.product_id
            == docent_session.product_id,
            HeritageContent.status
            == HeritageStatus.PUBLISHED,
        )
    ).all()

    db.flush()
    previous_messages = db.scalars(
        select(DocentMessage).where(
            DocentMessage.session_id == session_id,
        ).order_by(DocentMessage.created_at)
    ).all()

    try:
        generated = answer_question(
            question=request.question,
            items=heritage_items,
            history=[(message.role.value, message.content) for message in previous_messages],
        )
    except Exception as exc:
        db.rollback()
        print(f"AI answer generation failed: {exc}")
        raise APIError(
            status_code=503,
            code="AI_SERVICE_ERROR",
            message="도슨트 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc

    used_items = [item for item in heritage_items if item.id in generated.used_source_ids]
    sources = [
        {"title": item.source_title, "url": item.source_url}
        for item in used_items
    ]

    # assistant 답변 저장
    assistant_message = DocentMessage(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=generated.answer,
        grounded=generated.grounded,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return {
        "messageId": assistant_message.id,
        "answer": generated.answer,
        "grounded": generated.grounded,
        "sources": sources,
        "suggestedQuestions": generated.suggested_questions,
    }
