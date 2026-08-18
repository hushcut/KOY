from app.models.models import HeritageContent, HeritageStatus, HeritageTopic
from app.services import docent_service


def test_refusal_is_never_marked_grounded(monkeypatch):
    item = HeritageContent(
        id="heritage-1",
        product_id="product-1",
        topic=HeritageTopic.CRAFTSMANSHIP,
        title="공정",
        content="공식 자료",
        source_title="공식 출처",
        source_url="https://example.com",
        status=HeritageStatus.PUBLISHED,
    )
    monkeypatch.setattr(docent_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(
        docent_service,
        "_json_response",
        lambda instructions, prompt: {
            "answer": docent_service.UNGROUNDED_ANSWER,
            "grounded": True,
            "usedSourceIds": [item.id],
            "suggestedQuestions": ["후속 질문"],
        },
    )

    result = docent_service.answer_question("장인의 나이는?", [item], [])

    assert result.grounded is False
    assert result.answer == docent_service.UNGROUNDED_ANSWER
    assert result.used_source_ids == []
    assert result.suggested_questions == []
