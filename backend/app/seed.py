from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.models import (
    Product,
    HeritageContent,
    HeritageTopic,
    HeritageStatus,
)


PRODUCTS = [
    {
        "qr_value": "KOY-001",
        "brand_name": "KOY",
        "product_name": "Heritage Bag",
        "summary": "소재와 제작 공정의 이야기를 담은 헤리티지 백입니다.",
        "image_url": "/images/product-1.png",
        "heritage": [
            {
                "topic": HeritageTopic.MATERIAL,
                "title": "시간과 함께 깊어지는 소재",
                "content": "이 제품은 사용할수록 표면의 색과 질감이 자연스럽게 변화하도록 설계된 소재를 사용합니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-001-material",
            },
            {
                "topic": HeritageTopic.CRAFTSMANSHIP,
                "title": "손끝에서 완성되는 제작 과정",
                "content": "주요 조립 과정과 마감 단계는 숙련된 작업자의 손을 거쳐 순차적으로 진행됩니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-001-craft",
            },
            {
                "topic": HeritageTopic.BRAND_HISTORY,
                "title": "KOY가 시작된 이야기",
                "content": "KOY는 제품을 단순히 소비하는 것을 넘어 제작 배경과 이야기를 함께 전달하기 위해 시작되었습니다.",
                "source_title": "KOY 브랜드 스토리",
                "source_url": "https://example.com/koy-history",
            },
        ],
    },
    {
        "qr_value": "KOY-002",
        "brand_name": "KOY",
        "product_name": "Artisan Wallet",
        "summary": "장인의 세밀한 마감 과정을 강조한 지갑입니다.",
        "image_url": "/images/product-2.png",
        "heritage": [
            {
                "topic": HeritageTopic.MATERIAL,
                "title": "매일 손에 닿는 소재",
                "content": "표면의 촉감과 사용감을 고려하여 일상적인 사용에 적합한 소재를 선택했습니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-002-material",
            },
            {
                "topic": HeritageTopic.CRAFTSMANSHIP,
                "title": "세밀한 가장자리 마감",
                "content": "제품의 가장자리와 연결 부위는 여러 단계의 확인과 마감 작업을 거쳐 완성됩니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-002-craft",
            },
            {
                "topic": HeritageTopic.BRAND_HISTORY,
                "title": "오래 사용하는 제품에 대한 생각",
                "content": "KOY는 사용 시간이 제품의 경험을 완성한다는 관점을 제품 기획에 반영하고 있습니다.",
                "source_title": "KOY 브랜드 스토리",
                "source_url": "https://example.com/koy-history",
            },
        ],
    },
    {
        "qr_value": "KOY-003",
        "brand_name": "KOY",
        "product_name": "Signature Case",
        "summary": "소재와 형태의 균형을 강조한 시그니처 케이스입니다.",
        "image_url": "/images/product-3.png",
        "heritage": [
            {
                "topic": HeritageTopic.MATERIAL,
                "title": "형태를 유지하는 소재 선택",
                "content": "제품의 형태와 표면감을 안정적으로 유지할 수 있도록 소재의 특성을 고려해 선택했습니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-003-material",
            },
            {
                "topic": HeritageTopic.CRAFTSMANSHIP,
                "title": "균형을 만드는 조립 과정",
                "content": "각 부품의 위치와 형태가 일정하게 유지되도록 조립 과정에서 반복적인 확인 작업을 진행합니다.",
                "source_title": "KOY 공식 아카이브",
                "source_url": "https://example.com/koy-003-craft",
            },
            {
                "topic": HeritageTopic.BRAND_HISTORY,
                "title": "제품에 이야기를 연결하다",
                "content": "KOY는 QR을 통해 제품 제작 과정과 브랜드의 이야기를 방문객에게 전달하는 경험을 지향합니다.",
                "source_title": "KOY 브랜드 스토리",
                "source_url": "https://example.com/koy-history",
            },
        ],
    },
]


def seed():
    db = SessionLocal()

    try:
        for data in PRODUCTS:
            product = db.scalar(
                select(Product).where(
                    Product.qr_value == data["qr_value"]
                )
            )

            if product is None:
                product = Product(
                    qr_value=data["qr_value"],
                    brand_name=data["brand_name"],
                    product_name=data["product_name"],
                    summary=data["summary"],
                    image_url=data["image_url"],
                )

                db.add(product)
                db.flush()

            existing_titles = set(
                db.scalars(
                    select(HeritageContent.title).where(
                        HeritageContent.product_id == product.id
                    )
                ).all()
            )

            for item in data["heritage"]:
                if item["title"] in existing_titles:
                    continue

                heritage = HeritageContent(
                    product_id=product.id,
                    topic=item["topic"],
                    title=item["title"],
                    content=item["content"],
                    source_title=item["source_title"],
                    source_url=item["source_url"],
                    status=HeritageStatus.PUBLISHED,
                )

                db.add(heritage)

        db.commit()
        print("Seed completed successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()