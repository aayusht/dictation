import re

def post_process(text: str) -> str:
    text = lowercasify_if_single_sentence(text)
    return text

def lowercasify_if_single_sentence(text: str) -> str:
    if not text:
        return text

    # Simple sentence splitting logic: look for sentence-ending punctuation followed by space or end of string
    # This is a heuristic; more complex NLP might be needed for perfect accuracy
    sentences = re.split(r'[.!?]+(?:\s+|$)', text.strip())
    # Filter out empty strings from the split
    sentences = [s for s in sentences if s.strip()]

    if len(sentences) < 2:
        # Lowercase the first letter
        if text:
            text = text[0].lower() + text[1:]
        
        # Remove ending punctuation
        text = text.rstrip('.!? ')
        
    return text
