def process_content(content: str) -> str:
    """Очистка контента от служебных тегов"""
    return content.replace('<think>', '').replace('</think>', '')