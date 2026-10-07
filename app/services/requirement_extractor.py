import re
from collections import defaultdict


def extract_requirements(text: str) -> dict:
    """
    Extract structured requirement data from raw text.
    Rule-based v1 implementation.
    """

    result = {
        "project_type": None,
        "units": {},
        "amenities": [],
        "sustainability": [],
        "accessibility": []
    }

    lower_text = text.lower()

    # -------- Project Type --------
    if "mixed-use" in lower_text:
        result["project_type"] = "Mixed-use"
    elif "residential" in lower_text:
        result["project_type"] = "Residential"
    elif "commercial" in lower_text:
        result["project_type"] = "Commercial"

    # -------- Unit Extraction --------
    unit_patterns = [
        r"(\d+)\s*studio",
        r"(\d+)\s*one[- ]bedroom",
        r"(\d+)\s*two[- ]bedroom",
        r"(\d+)\s*three[- ]bedroom"
    ]

    for pattern in unit_patterns:
        matches = re.findall(pattern, lower_text)
        if matches:
            key = pattern.split("\\s*")[1].replace("[- ]", "_").replace("(", "").replace(")", "")
            result["units"][key] = sum(int(m) for m in matches)

    # -------- Amenities --------
    amenities_keywords = [
        "rooftop garden",
        "gym",
        "multipurpose hall",
        "parking",
        "clubhouse"
    ]

    for keyword in amenities_keywords:
        if keyword in lower_text:
            result["amenities"].append(keyword)

    # -------- Sustainability --------
    sustainability_keywords = [
        "solar",
        "rainwater",
        "waste segregation",
        "energy-efficient",
        "green building"
    ]

    for keyword in sustainability_keywords:
        if keyword in lower_text:
            result["sustainability"].append(keyword)

    # -------- Accessibility --------
    accessibility_keywords = [
        "ramp",
        "elevator",
        "accessible",
        "wheelchair"
    ]

    for keyword in accessibility_keywords:
        if keyword in lower_text:
            result["accessibility"].append(keyword)

    return result
