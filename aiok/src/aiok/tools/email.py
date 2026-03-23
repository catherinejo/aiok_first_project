"""메일 처리 도구."""


def summarize_email(email_content: str) -> dict:
    """이메일 내용을 요약합니다.

    Args:
        email_content: 요약할 이메일 전문

    Returns:
        요약 지시사항
    """
    return {
        "content": email_content,
        "instruction": "이 이메일의 핵심 내용을 요약하고, 액션 아이템이 있다면 추출해주세요.",
    }


def generate_reply(
    email_content: str,
    tone: str = "formal",
    key_points: str | None = None,
) -> dict:
    """이메일 회신 초안을 생성합니다.

    Args:
        email_content: 원본 이메일 내용
        tone: 회신 톤 (formal, friendly, concise)
        key_points: 회신에 포함할 핵심 내용 (선택)

    Returns:
        회신 생성 지시사항
    """
    return {
        "original_email": email_content,
        "tone": tone,
        "key_points": key_points,
        "instruction": f"{tone} 톤으로 회신 초안을 작성해주세요.",
    }
