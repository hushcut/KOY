import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------
# 1. Health Check
# ---------------------------------------------------------

def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


# ---------------------------------------------------------
# 2. QR 제품 조회 성공
# ---------------------------------------------------------

def test_product_by_qr(client):
    response = client.get(
        "/products/by-qr/KOY-001"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["qrValue"] == "KOY-001"
    assert data["brandName"] == "MCM"
    assert "id" in data
    assert "productName" in data


# ---------------------------------------------------------
# 3. 존재하지 않는 QR
# ---------------------------------------------------------

def test_product_not_found(client):
    response = client.get(
        "/products/by-qr/NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == (
        "PRODUCT_NOT_FOUND"
    )


# ---------------------------------------------------------
# 4. 제품 검색
# ---------------------------------------------------------

def test_search_products(client):
    response = client.get(
        "/products/search",
        params={
            "q": "MCM"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert len(data["items"]) >= 1
    assert "qrValue" in data["items"][0]


# ---------------------------------------------------------
# 5. 검색 결과 없음
# ---------------------------------------------------------

def test_search_no_results(client):
    response = client.get(
        "/products/search",
        params={
            "q": "THIS_PRODUCT_DOES_NOT_EXIST"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []


# ---------------------------------------------------------
# 6. 잘못된 interest
# ---------------------------------------------------------

def test_invalid_interest(client):
    product_response = client.get(
        "/products/by-qr/KOY-001"
    )

    product_id = (
        product_response.json()["id"]
    )

    response = client.post(
        "/docent/story",
        json={
            "productId": product_id,
            "interest": "history",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == (
        "INVALID_INTEREST"
    )


# ---------------------------------------------------------
# 7. 없는 세션
# ---------------------------------------------------------

def test_session_not_found(client):
    response = client.post(
        "/docent/sessions/"
        "not-existing-session/messages",
        json={
            "question": "이 제품의 소재는 무엇인가요?"
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == (
        "SESSION_NOT_FOUND"
    )


# ---------------------------------------------------------
# 8. 빈 질문
# ---------------------------------------------------------

def test_invalid_empty_question(client):
    product_response = client.get(
        "/products/by-qr/KOY-001"
    )

    product_id = (
        product_response.json()["id"]
    )

    story_response = client.post(
        "/docent/story",
        json={
            "productId": product_id,
            "interest": "material",
        },
    )

    assert story_response.status_code == 200

    session_id = (
        story_response.json()["sessionId"]
    )

    response = client.post(
        f"/docent/sessions/{session_id}/messages",
        json={
            "question": "   "
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["error"]["code"] == (
        "INVALID_REQUEST"
    )


# ---------------------------------------------------------
# 9. 근거 부족 질문
# ---------------------------------------------------------

def test_ungrounded_answer(client):
    product_response = client.get(
        "/products/by-qr/KOY-001"
    )

    product_id = (
        product_response.json()["id"]
    )

    story_response = client.post(
        "/docent/story",
        json={
            "productId": product_id,
            "interest": "craftsmanship",
        },
    )

    assert story_response.status_code == 200

    session_id = (
        story_response.json()["sessionId"]
    )

    response = client.post(
        f"/docent/sessions/{session_id}/messages",
        json={
            "question":
                "이 제품을 만든 사람은 몇 살인가요?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["grounded"] is False

    assert data["answer"] == (
        "현재 등록된 공식 자료만으로는 "
        "정확히 답변하기 어렵습니다."
    )

    assert data["sources"] == []
    assert data["suggestedQuestions"] == []
