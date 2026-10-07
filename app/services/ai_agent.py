from app.services.requirement_extractor import extract_requirements
import requests
from typing import Dict
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    DEFAULT_LLM_URL = os.getenv("LLM_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
else:
    DEFAULT_LLM_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
    DEFAULT_MODEL_NAME = os.getenv("LLM_MODEL", "mistralai/mistral-small-3.2")

# --- prompt templates -----------------------------------------------------
MASTER_PROMPT = (
    "You are an advanced domain-aware consulting intelligence engine.\n\n"
    "You must internally analyze client requirements using a structured multi-stage reasoning framework.\n\n"
    "Follow this internal reasoning process:\n"
    "Stage 1: Requirement Clarification\n"
    "- Extract explicit statements.\n"
    "- Identify ambiguous phrases.\n"
    "- Detect assumptions needed.\n\n"
    "Stage 2: Intent Inference\n"
    "- Identify primary project objective.\n"
    "- Identify secondary goals.\n"
    "- Infer unstated but logically necessary elements.\n\n"
    "Stage 3: Requirement Decomposition\n"
    "- Break into functional requirements.\n"
    "- Break into non-functional requirements.\n"
    "- Identify business or structural constraints.\n\n"
    "Stage 4: Missing Requirement Identification\n"
    "- Determine what critical information is not provided.\n"
    "- Categorize missing requirements into logical groups.\n"
    "- Only include items that are necessary for project execution.\n\n"
    "Stage 5: Gap Severity Classification\n"
    "- Classify missing requirements by impact level:\n"
    "  Critical / Moderate / Minor.\n\n"
    "Stage 6: Risk Analysis\n"
    "- Identify risks caused by missing or unclear requirements.\n"
    "- Classify risk type and impact.\n\n"
    "Stage 7: Structured Consolidation\n"
    "- Convert findings into structured JSON output.\n"
    "- Maintain professional consulting tone.\n"
    "- Do NOT reveal internal reasoning stages.\n"
    "- Output must strictly follow schema.\n\n"
    "Rules:\n"
    "- Do NOT fabricate data.\n"
    "- Clearly state \"Not Specified\" when needed.\n"
    "- Only include realistic missing requirements.\n"
)

SOFTWARE_PROMPT = (
    "Domain: Software Architecture\n\n"
    "Client Requirement:\n"
    "<USER_INPUT>\n\n"
    "Apply the internal reasoning framework.\n\n"
    "Return output in this exact JSON structure:\n\n"
    "{\n"
    "  \"executive_summary\": {\n"
    "    \"primary_objective\": \"\",\n"
    "    \"secondary_objectives\": [],\n"
    "    \"business_context\": \"\"\n"
    "  },\n"
    "  \"requirement_breakdown\": {\n"
    "    \"functional_requirements\": [],\n"
    "    \"non_functional_requirements\": [],\n"
    "    \"constraints_identified\": []\n"
    "  },\n"
    "  \"missing_requirements\": {\n"
    "    \"business_information_missing\": [],\n"
    "    \"functional_details_missing\": [],\n"
    "    \"technical_details_missing\": [],\n"
    "    \"operational_details_missing\": []\n"
    "  },\n"
    "  \"gap_severity_analysis\": {\n"
    "    \"critical_gaps\": [],\n"
    "    \"moderate_gaps\": [],\n"
    "    \"minor_gaps\": []\n"
    "  },\n"
    "  \"risk_matrix\": [\n"
    "    {\n"
    "      \"risk_category\": \"\",\n"
    "      \"risk_description\": \"\",\n"
    "      \"impact_level\": \"\",\n"
    "      \"probability_estimate\": \"\",\n"
    "      \"justification\": \"\"\n"
    "    }\n"
    "  ],\n"
    "  \"architecture_implications\": {\n"
    "    \"recommended_architecture_pattern\": \"\",\n"
    "    \"integration_complexity\": \"\",\n"
    "    \"data_management_considerations\": []\n"
    "  },\n"
    "  \"completeness_score\": 0,\n"
    "  \"strategic_recommendations\": []\n"
    "}\n"
)

ARCHITECT_PROMPT = (
    "Domain: Architectural Planning\n\n"
    "Client Requirement:\n"
    "<USER_INPUT>\n\n"
    "Apply the internal reasoning framework.\n\n"
    "Return output in this exact JSON structure:\n\n"
    "{\n"
    "  \"executive_summary\": {\n"
    "    \"project_intent\": \"\",\n"
    "    \"usage_type\": \"\",\n"
    "    \"development_scale\": \"\"\n"
    "  },\n"
    "  \"requirement_breakdown\": {\n"
    "    \"spatial_requirements\": [],\n"
    "    \"functional_zones\": [],\n"
    "    \"site_constraints_identified\": []\n"
    "  },\n"
    "  \"missing_requirements\": {\n"
    "    \"site_information_missing\": [],\n"
    "    \"design_details_missing\": [],\n"
    "    \"regulatory_information_missing\": [],\n"
    "    \"budgetary_information_missing\": []\n"
    "  },\n"
    "  \"gap_severity_analysis\": {\n"
    "    \"critical_gaps\": [],\n"
    "    \"moderate_gaps\": [],\n"
    "    \"minor_gaps\": []\n"
    "  },\n"
    "  \"risk_matrix\": [\n"
    "    {\n"
    "      \"risk_category\": \"\",\n"
    "      \"risk_description\": \"\",\n"
    "      \"impact_level\": \"\",\n"
    "      \"probability_estimate\": \"\",\n"
    "      \"justification\": \"\"\n"
    "    }\n"
    "  ],\n"
    "  \"design_implications\": {\n"
    "    \"structural_considerations\": [],\n"
    "    \"material_considerations\": [],\n"
    "    \"approval_complexity\": \"\"\n"
    "  },\n"
    "  \"completeness_score\": 0,\n"
    "  \"design_recommendations\": []\n"
    "}\n"
)


class LLMRequirementRefiner:
    def __init__(self, domain: str = "architecture"):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.url = os.getenv("LLM_API_URL", "https://api.groq.com/openai/v1/chat/completions")
            self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        else:
            self.url = os.getenv("LLM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
            self.model = os.getenv("LLM_MODEL", "mistralai/mistral-small-3.2")
        self.domain = domain

    # --- internal helpers --------------------------------------------------
    def _select_domain_template(self, user_input: str) -> str:
        if self.domain.lower() == "software":
            return SOFTWARE_PROMPT.replace("<USER_INPUT>", user_input)
        else:
            return ARCHITECT_PROMPT.replace("<USER_INPUT>", user_input)

    def _call_llm(self, messages: list, temperature: float = 0.2, timeout: int = 600) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        response = requests.post(self.url, json=payload, headers=headers, timeout=timeout)
        # for debugging, preserve status and raw text if problems arise
        print("STATUS:", response.status_code)
        if response.status_code != 200:
            print("RAW RESPONSE:", response.text)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    # --- public API --------------------------------------------------------
    def analyze(self, raw_text: str) -> dict:
        """Run the multi-stage reasoning framework and return parsed JSON.

        The LLM is instructed to return strictly-formatted JSON, but in practice
        it sometimes adds explanatory text or otherwise breaks strict parsing.
        This method attempts a best-effort extraction of the JSON payload.
        """
        prompt = MASTER_PROMPT + "\n\n" + self._select_domain_template(raw_text)
        messages = [
            {"role": "system", "content": prompt},
        ]
        result_str = self._call_llm(messages)

        # first try straight parsing
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            # attempt to extract JSON object from within the human text
            match = re.search(r"\{.*\}", result_str, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

            # if we still don't have a JSON object, ask the model to retry more cleanly
            retry_msg = (
                "The previous response could not be parsed as JSON. "
                "Please reply again with *only* the JSON object matching the schema, "
                "and do not include any explanatory text."
            )
            messages.append({"role": "user", "content": retry_msg})
            result_str2 = self._call_llm(messages)
            try:
                return json.loads(result_str2)
            except json.JSONDecodeError as e2:
                raise ValueError(
                    "Failed to obtain valid JSON from the LLM. "
                    "Raw outputs were:\n"
                    f"First attempt:\n{result_str}\n"
                    f"Retry attempt:\n{result_str2}"
                ) from e2

    def rewrite(self, raw_text: str) -> str:
        """Produce a cleaned, professional version of the requirements document."""
        role_description = (
            "You are a senior software engineering consultant."
            if self.domain.lower() == "software"
            else "You are a senior architectural consultant."
        )
        system_prompt = (
            f"{role_description}\n\n"
            "You will receive messy client requirements.\n"
            "Your task:\n"
            "1. Rewrite them professionally\n"
            "2. Organize into sections:\n"
            "   - Project Overview\n"
            "   - Functional Requirements\n"
            "   - Design Preferences\n"
            "   - Timeline Expectations\n"
            "   - Missing Clarifications\n"
            "3. Do NOT hallucinate information\n"
            "4. Be concise, clear, and professional\n"
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ]
        return self._call_llm(messages)

    def answer_question(self, context: str, question: str) -> str:
        """Given a context (e.g. chunks) and a user question, answer using only that context."""
        system_prompt = (
            "You are a domain-aware consulting intelligence engine. "
            "Answer the user's question using only the provided context. "
            "If the information is not present, reply 'Insufficient information'."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion:\n{question}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self._call_llm(messages)

    def refine(self, raw_text: str) -> str:
        return self.rewrite(raw_text)


class DocumentAI:
    def __init__(self, domain: str = "architecture"):
        self.domain = domain
        self.refiner = LLMRequirementRefiner(domain=domain)

    # approximate maximum characters to send to LLM in one shot
    _MAX_CHARS = 12000

    def _merge_dicts(self, a: dict, b: dict) -> dict:
        """Recursively merge two analysis dictionaries.
        Lists are concatenated with duplicates removed; scalars from `b` override.
        """
        out = a.copy()
        for k, v in b.items():
            if k in out:
                if isinstance(out[k], list) and isinstance(v, list):
                    combined = out[k] + v
                    seen = set()
                    uniq = []
                    for item in combined:
                        tup = tuple(item) if isinstance(item, list) else item
                        if tup not in seen:
                            seen.add(tup)
                            uniq.append(item)
                    out[k] = uniq
                elif isinstance(out[k], dict) and isinstance(v, dict):
                    out[k] = self._merge_dicts(out[k], v)
                else:
                    out[k] = v
            else:
                out[k] = v
        return out

    def analyze_document(self, full_text: str) -> dict:
        """
        Main intelligence entry point.
        Runs the multi-stage LLM analysis and also produces a cleaned text
        representation. Keeps the rule-based extractor as a fallback.

        If the text is very large we split it into multiple chunks and analyze
        each separately to avoid exceeding token limits; results are merged.
        """
        if not full_text or not full_text.strip():
            raise ValueError("Empty document text")

        if len(full_text) > self._MAX_CHARS:
            parts = [
                full_text[i : i + self._MAX_CHARS]
                for i in range(0, len(full_text), self._MAX_CHARS)
            ]
            merged = None
            for part in parts:
                part_analysis = self.refiner.analyze(part)
                if merged is None:
                    merged = part_analysis
                else:
                    merged = self._merge_dicts(merged, part_analysis)
            analysis = merged or {}
        else:
            analysis = self.refiner.analyze(full_text)

        clean_text = self.refiner.rewrite(full_text)
        structured = extract_requirements(full_text)

        return {
            "structured_data": analysis,
            "refine_text": clean_text,
            "legacy_structured": structured,
        }





def analyze_requirements_with_ai(text: str) -> dict:
    """
        Mock AI reasoning function.
        This simulates what an LLM would do.
    """

    missing_info = []
    conflicts = []

    text_lower = text.lower()

    if "budget" not in text_lower:
        missing_info.append("Budget not clearly specified")
    
    if "floor" not in text_lower:
        missing_info.append("Number of floors not specified")
    
    if "regulation" not in text_lower and "bylaw" not in text_lower:
        missing_info.append("Local regulation not mentioned")
    if "budget" in text_lower and "luxury" in text_lower:
        conflicts.append("Luxury expectations may conflict with stated budget")

    return {
        "ai_summery" : "This is a preliminary requirement analysis.",
        "missing_information": missing_info,
        "potential_conflicts": conflicts,
        "design_readiness_score" : 70 - (len(missing_info) * 10)
    }