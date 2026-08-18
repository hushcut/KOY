import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["OPENAI_API_KEY"] = ""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.models import HeritageContent, HeritageStatus, Product
from app.seed import PRODUCTS


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def test_database():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    for data in PRODUCTS:
        product = Product(
            qr_value=data["qr_value"],
            brand_name=data["brand_name"],
            product_name=data["product_name"],
            summary=data["summary"],
            image_url=data["image_url"],
        )
        db.add(product)
        db.flush()
        for item in data["heritage"]:
            db.add(
                HeritageContent(
                    product_id=product.id,
                    topic=item["topic"],
                    title=item["title"],
                    content=item["content"],
                    source_title=item["source_title"],
                    source_url=item["source_url"],
                    status=HeritageStatus.PUBLISHED,
                )
            )
    db.commit()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
