import json
from dataclasses import dataclass

from openai import OpenAI

from app.core.config import settings
from app.models.models import HeritageContent, HeritageTopic


UNGROUNDED_ANSWER = "현재 등록된 공식 자료만으로는 정확히 답변하기 어렵습니다."


@dataclass
class StoryResult:
    title: str
    story: str
    suggested_questions: list[str]


@dataclass
class AnswerResult:
    answer: str
    grounded: bool
    suggested_questions: list[str]
    used_source_ids: list[str]


def _context(items: list[HeritageContent]) -> str:
    return "\n\n".join(
        f"[자료 ID: {item.id}]\n주제: {item.topic.value}\n제목: {item.title}\n본문: {item.content}\n출처: {item.source_title}"
        for item in items
    )


def _grounded_questions(items: list[HeritageContent], limit: int = 3) -> list[str]:
    questions_by_topic = {
        HeritageTopic.MATERIAL: [
            "이 제품의 소재에 대해 알려주세요.",
            "공식 자료에서 확인되는 소재 특징은 무엇인가요?",
        ],
        HeritageTopic.CRAFTSMANSHIP: [
            "이 제품의 제작과 구성 특징을 알려주세요.",
            "공식 자료에서 확인되는 제작·구성 정보는 무엇인가요?",
        ],
        HeritageTopic.BRAND_HISTORY: [
            "이 제품에 담긴 브랜드 이야기를 알려주세요.",
            "공식 자료에서 확인되는 디자인 배경은 무엇인가요?",
        ],
    }
    questions: list[str] = []
    for item in items:
        questions.extend(questions_by_topic[item.topic])
    return list(dict.fromkeys(questions))[:limit]


def _json_response(instructions: str, prompt: str, schema_name: str, schema: dict) -> dict:
    client = OpenAI(api_key=settings.openai_api_key)
    last_error: json.JSONDecodeError | None = None
    for max_output_tokens in (2400, 4000):
        response = client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
            max_output_tokens=max_output_tokens,
            reasoning={"effort": "low"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        text = response.output_text.strip()
        if text.startswith("```"):
            text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            last_error = exc

    assert last_error is not None
    raise last_error


def generate_story(
    product_name: str,
    interest: HeritageTopic,
    items: list[HeritageContent],
) -> StoryResult:
    if not settings.openai_api_key:
        return StoryResult(
            title=items[0].title,
            story=" ".join(item.content for item in items),
            suggested_questions=_fallback_questions(interest),
        )

    try:
        data = _json_response(
            """당신은 제품 헤리티지 도슨트입니다. 제공된 공식 자료만 사용해 한국어로 답하세요.
자료에 없는 사실은 추측하거나 추가하지 마세요. 모바일에서 읽기 쉬운 간결한 문장으로 작성하세요.
반드시 JSON만 반환하세요: {"title":"", "story":""}""",
            f"제품: {product_name}\n관심 주제: {interest.value}\n\n공식 자료:\n{_context(items)}",
            "docent_story",
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "story": {"type": "string"},
                },
                "required": ["title", "story"],
                "additionalProperties": False,
            },
        )
    except Exception as exc:
        print(f"AI story fallback used: {exc}")
        return StoryResult(
            title=items[0].title,
            story=" ".join(item.content for item in items),
            suggested_questions=_grounded_questions(items),
        )
    return StoryResult(
        title=str(data["title"]),
        story=str(data["story"]),
        suggested_questions=_grounded_questions(items),
    )


def answer_question(
    question: str,
    items: list[HeritageContent],
    history: list[tuple[str, str]],
) -> AnswerResult:
    if not settings.openai_api_key:
        return _fallback_answer(question, items)

    history_text = "\n".join(f"{role}: {content}" for role, content in history[-10:])
    try:
        data = _json_response(
            f"""당신은 제품 헤리티지 도슨트입니다. 공식 자료만 근거로 한국어로 답하세요.
자료에서 확인할 수 없는 내용은 추측하지 말고 정확히 '{UNGROUNDED_ANSWER}'라고 답하세요.
usedSourceIds에는 실제 답변 근거로 사용한 자료 ID만 넣으세요. 반드시 JSON만 반환하세요:
{{"answer":"", "grounded":true, "usedSourceIds":[""]}}""",
            f"공식 자료:\n{_context(items)}\n\n최근 대화:\n{history_text}\n\n현재 질문: {question}",
            "docent_answer",
            {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "grounded": {"type": "boolean"},
                    "usedSourceIds": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["answer", "grounded", "usedSourceIds"],
                "additionalProperties": False,
            },
        )
    except Exception as exc:
        print(f"AI answer fallback used: {exc}")
        return _fallback_answer(question, items)
    known_ids = {item.id for item in items}
    used_ids = [str(item_id) for item_id in data.get("usedSourceIds", []) if str(item_id) in known_ids]
    raw_answer = str(data.get("answer") or UNGROUNDED_ANSWER).strip()
    grounded = (
        bool(data.get("grounded"))
        and bool(used_ids)
        and UNGROUNDED_ANSWER not in raw_answer
    )
    return AnswerResult(
        answer=raw_answer if grounded else UNGROUNDED_ANSWER,
        grounded=grounded,
        suggested_questions=_grounded_questions(items) if grounded else [],
        used_source_ids=used_ids if grounded else [],
    )


def _fallback_questions(interest: HeritageTopic) -> list[str]:
    return {
        HeritageTopic.MATERIAL: ["이 제품의 소재에 대해 알려주세요.", "공식 자료에서 확인되는 소재 특징은 무엇인가요?"],
        HeritageTopic.CRAFTSMANSHIP: ["이 제품의 제작과 구성 특징을 알려주세요.", "공식 자료에서 확인되는 제작·구성 정보는 무엇인가요?"],
        HeritageTopic.BRAND_HISTORY: ["이 제품에 담긴 브랜드 이야기를 알려주세요.", "공식 자료에서 확인되는 디자인 배경은 무엇인가요?"],
    }[interest]


def _fallback_answer(question: str, items: list[HeritageContent]) -> AnswerResult:
    unsupported_details = [
        "몇 살",
        "나이",
        "이름",
        "누구",
        "가격",
        "얼마",
        "재고",
        "할인",
    ]
    normalized_question = question.lower()
    if any(detail in normalized_question for detail in unsupported_details):
        return AnswerResult(UNGROUNDED_ANSWER, False, [], [])

    keywords = {
        HeritageTopic.MATERIAL: ["소재", "재료", "가죽", "질감", "색", "표면", "변화"],
        HeritageTopic.CRAFTSMANSHIP: ["제작", "공정", "장인", "작업", "마감", "만들"],
        HeritageTopic.BRAND_HISTORY: ["브랜드", "역사", "시작", "철학", "가치", "유래"],
    }
    matched = [item for item in items if any(word in normalized_question for word in keywords.get(item.topic, []))]
    if not matched:
        return AnswerResult(UNGROUNDED_ANSWER, False, [], [])
    return AnswerResult(
        answer=" ".join(item.content for item in matched),
        grounded=True,
        suggested_questions=["이 제품의 다른 헤리티지도 알려주세요."],
        used_source_ids=[item.id for item in matched],
    )
