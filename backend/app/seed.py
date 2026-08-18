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
        "brand_name": "MCM",
        "product_name": "Ella Boston Bag in Visetos",
        "summary": "뮌헨 여행 문화의 황금기와 트렁크 실루엣에서 영감을 받은 비세토스 보스턴백입니다.",
        "image_url": "/figma-product-2.png",
        "heritage": [
            {
                "topic": HeritageTopic.MATERIAL,
                "title": "비세토스 캔버스와 가죽 디테일",
                "content": "제품의 바디에는 비세토스 모노그램 캔버스를 사용하고 가죽 트리밍과 24K 금도금 황동 하드웨어를 더했습니다. 내부는 스웨이드 마감의 마이크로파이버 안감으로 구성됩니다.",
                "source_title": "MCM 공식 제품 페이지",
                "source_url": "https://us.mcmworldwide.com/en_US/women/bags/top-handle-bags/ella-boston-bag-in-visetos/MWBFAEA01CO001.html",
            },
            {
                "topic": HeritageTopic.CRAFTSMANSHIP,
                "title": "사용성과 수납을 고려한 구성",
                "content": "가죽 상단 손잡이와 탈착 및 길이 조절이 가능한 가죽 스트랩, 양방향 지퍼 여밈을 갖췄습니다. 내부에는 포켓과 카드 슬롯이 있으며 바이에른 다이아몬드 가죽 참은 분리할 수 있습니다.",
                "source_title": "MCM 공식 제품 페이지",
                "source_url": "https://us.mcmworldwide.com/en_US/women/bags/top-handle-bags/ella-boston-bag-in-visetos/MWBFAEA01CO001.html",
            },
            {
                "topic": HeritageTopic.BRAND_HISTORY,
                "title": "뮌헨 황금기 여행 문화에서 온 디자인",
                "content": "Ella Boston Bag은 뮌헨 황금기의 여행용 트렁크를 본떠 디자인했습니다. 로고가 음각된 탈착식 가죽 참은 바이에른 다이아몬드에서 영감을 받았습니다.",
                "source_title": "MCM 공식 제품 페이지",
                "source_url": "https://us.mcmworldwide.com/en_US/women/bags/top-handle-bags/ella-boston-bag-in-visetos/MWBFAEA01CO001.html",
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
            else:
                product.brand_name = data["brand_name"]
                product.product_name = data["product_name"]
                product.summary = data["summary"]
                product.image_url = data["image_url"]

            existing_by_topic = {
                heritage.topic: heritage
                for heritage in db.scalars(
                    select(HeritageContent).where(HeritageContent.product_id == product.id)
                ).all()
            }

            for item in data["heritage"]:
                heritage = existing_by_topic.get(item["topic"])
                if heritage is not None:
                    heritage.title = item["title"]
                    heritage.content = item["content"]
                    heritage.source_title = item["source_title"]
                    heritage.source_url = item["source_url"]
                    heritage.status = HeritageStatus.PUBLISHED
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
