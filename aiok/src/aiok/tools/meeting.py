"""회의록 처리 도구."""


def summarize_meeting(
    meeting_content: str,
    meeting_type: str = "general",
    extract_action_items: bool = True,
) -> dict:
    """회의 내용을 요약하고 정리합니다.

    Args:
        meeting_content: 회의 녹취록 또는 메모
        meeting_type: 회의 유형 (standup, planning, review, general)
        extract_action_items: 액션 아이템 추출 여부

    Returns:
        회의 요약 지시사항
    """
    instruction = f"이 {meeting_type} 회의 내용을 요약해주세요."
    if extract_action_items:
        instruction += " 액션 아이템과 담당자, 기한도 추출해주세요."

    return {
        "content": meeting_content,
        "meeting_type": meeting_type,
        "instruction": instruction,
    }
