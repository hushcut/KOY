from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

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
    allow_origins=[
        "http://localhost:3000",
    ],
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

    # OpenAI 연동 전 임시 구현
    story = " ".join(
        item.content
        for item in heritage_items
    )

    suggested_questions_map = {
        HeritageTopic.MATERIAL: [
            "이 소재의 특징은 무엇인가요?",
            "시간이 지나면 소재는 어떻게 변하나요?",
        ],
        HeritageTopic.CRAFTSMANSHIP: [
            "제작 과정에서 중요한 단계는 무엇인가요?",
            "장인의 작업 방식에는 어떤 특징이 있나요?",
        ],
        HeritageTopic.BRAND_HISTORY: [
            "이 브랜드는 어떻게 시작되었나요?",
            "브랜드가 중요하게 생각하는 가치는 무엇인가요?",
        ],
    }

    sources = [
        {
            "title": item.source_title,
            "url": item.source_url,
        }
        for item in heritage_items
    ]

    return {
        "sessionId": docent_session.id,
        "title": heritage_items[0].title,
        "story": story,
        "suggestedQuestions":
            suggested_questions_map[request.interest],
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

    question = request.question.lower()

    # OpenAI 연동 전 임시 키워드 방식
    keyword_map = {
        HeritageTopic.MATERIAL: [
            "소재",
            "재료",
            "가죽",
            "질감",
            "색",
            "표면",
            "변화",
        ],
        HeritageTopic.CRAFTSMANSHIP: [
            "제작",
            "공정",
            "장인",
            "작업",
            "마감",
            "만들",
        ],
        HeritageTopic.BRAND_HISTORY: [
            "브랜드",
            "역사",
            "시작",
            "철학",
            "가치",
            "유래",
        ],
    }

    matched_items = []

    for item in heritage_items:
        keywords = keyword_map.get(
            item.topic,
            [],
        )

        if any(
            keyword in question
            for keyword in keywords
        ):
            matched_items.append(item)

    # 근거 있음
    if matched_items:
        answer = " ".join(
            item.content
            for item in matched_items
        )

        grounded = True

        sources = [
            {
                "title": item.source_title,
                "url": item.source_url,
            }
            for item in matched_items
        ]

        suggested_questions = [
            "이 제품의 다른 헤리티지도 알려주세요."
        ]

    # 근거 없음
    else:
        answer = (
            "현재 등록된 공식 자료만으로는 "
            "정확히 답변하기 어렵습니다."
        )

        grounded = False
        sources = []
        suggested_questions = []

    # assistant 답변 저장
    assistant_message = DocentMessage(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=answer,
        grounded=grounded,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return {
        "messageId": assistant_message.id,
        "answer": answer,
        "grounded": grounded,
        "sources": sources,
        "suggestedQuestions": suggested_questions,
    }