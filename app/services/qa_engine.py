def answer_question(context: str,question: str) -> str:
    """
    Temporary rule-based QA.
    Replace with LLM Later.
    """

    # Basic demo Logic
    if "two bedroom" in question.lower():
        return "The project includes 20 two-bedroom aparments."
    
    if "amenities" in question.lower():
        return "Amenities include rooftop garden, gym, and multipurpose hall."
    
    return "Answer not found in document"