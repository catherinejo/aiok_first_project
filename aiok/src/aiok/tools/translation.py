"""번역 도구."""


def translate_text(
    text: str,
    target_language: str,
    source_language: str = "auto",
    style: str = "business",
) -> dict:
    """텍스트를 다른 언어로 번역합니다.

    Args:
        text: 번역할 텍스트
        target_language: 목표 언어 (ko, en, ja, zh-CN, zh-TW)
        source_language: 원본 언어 (auto면 자동 감지)
        style: 번역 스타일 (formal, casual, business)

    Returns:
        번역 결과
    """
    return {
        "original": text,
        "target_language": target_language,
        "source_language": source_language,
        "style": style,
        "instruction": f"위 텍스트를 {target_language}로 {style} 스타일로 번역해주세요.",
    }
