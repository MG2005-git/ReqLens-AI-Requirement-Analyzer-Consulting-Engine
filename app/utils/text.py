import re

def normalize_text(text: str) -> str:
    """
        Basic text normalization:
        - remove excessive whitespace
        - normalize line breaks
        - strip leading/trailing spaces
    """

    # Replace multiple newline with single newline

    text = re.sub(r"\n+","\n", text)

    # Replace multiple spaces with single space

    text  = re.sub(r"[ \t]+"," ",text)


    return text.strip()


