import re


def get_reading_width_style(width_choice: str):
    return {
        "Narrow": "max-width: 640px;",
        "Normal": "max-width: 780px;",
        "Wide": "max-width: 100%;",
    }.get(width_choice, "max-width: 780px;")


def apply_chunking(text: str, mode: str):
    if mode != "Shorter Paragraphs":
        return text

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks = []
    current = []

    for sentence in sentences:
        current.append(sentence)
        if len(current) == 2:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return "\n\n".join(chunks)


def get_font_family(font_style: str):
    return {
        "Simple": "Arial, sans-serif",
        "Rounded": "'Trebuchet MS', sans-serif",
        "Open and Clear": "Verdana, sans-serif",
    }.get(font_style, "Arial, sans-serif")