import os
import json
from collections import OrderedDict
from app.models.schemas import LLMInput, LLMOutput
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

class CognitiveService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

        # LRU Cache: Store up to 100 recent analyses
        self._cache = OrderedDict()
        self._cache_size = 100

    def _get_cache_key(self, data: LLMInput) -> tuple:
        """Create a hashable key from LLMInput."""
        # Convert lists to sorted tuples for consistent hashing
        symptoms_tuple = tuple(sorted(data.symptoms))
        risk_factors_tuple = tuple(sorted(data.risk_factors))

        return (
            data.cancer_type,
            round(data.ml_confidence, 2), # Round for cache hit probability
            data.preliminary_cri,
            symptoms_tuple,
            data.age,
            risk_factors_tuple
        )

    def _update_cache(self, key, value):
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)

    async def analyze(self, data: LLMInput) -> LLMOutput:
        cache_key = self._get_cache_key(data)

        if cache_key in self._cache:
            # Move to end to mark as recently used
            self._cache.move_to_end(cache_key)
            # Return a copy to prevent mutation of cached object
            return self._cache[cache_key].model_copy()

        if not self.model:
            result = self._mock_response(data)
            self._update_cache(cache_key, result)
            return result

        system_prompt = """You are a medical triage decision-support assistant.

Your role is to assist in risk stratification for cancer-related cases.
You must NOT diagnose cancer or confirm medical conditions.
You must NOT provide treatment or medication advice.

You will analyze structured inputs including:
- Machine learning confidence scores
- Patient symptoms
- Risk factors

Your task is to:
1. Assess consistency between imaging confidence and symptoms
2. Assign a triage level (Low, Moderate, High, Critical)
3. Provide a conservative risk explanation
4. Recommend urgency of medical consultation

If uncertainty exists, you must choose the safer, more conservative option."""

        user_prompt = f"""
Analyze the following patient data:

{{
  "cancer_type": "{data.cancer_type}",
  "ml_confidence": {data.ml_confidence},
  "preliminary_cri": {data.preliminary_cri},
  "symptoms": {json.dumps(data.symptoms)},
  "age": {data.age},
  "risk_factors": {json.dumps(data.risk_factors)}
}}

Steps to follow:
1. Check if symptoms align with the given cancer type
2. Evaluate whether ML confidence and symptoms are consistent
3. Select ONE triage level: Low, Moderate, High, Critical
4. Suggest a small adjustment to the risk score (-10 to +10)
5. Provide a short explanation (2–3 sentences)
6. Recommend urgency of consultation

Do not use diagnostic language.
Do not exceed the scope of decision support.

Respond ONLY in valid JSON with this exact format:
{{
  "triage_level": "High",
  "risk_adjustment": 5,
  "explanation": "The imaging confidence is high and the reported symptoms are neurologically consistent, suggesting elevated risk that requires timely evaluation.",
  "recommendation": "Consult a specialist within 24–48 hours."
}}
"""

        try:
            # Async call to prevent blocking event loop
            response = await self.model.generate_content_async(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            content = response.text
            parsed = json.loads(content)
            result = LLMOutput(**parsed)

            self._update_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._mock_response(data)

    def _mock_response(self, data: LLMInput) -> LLMOutput:
        # Fallback if no API key or error
        # Simple logic to simulate LLM reasoning
        
        triage = "Moderate"
        adjustment = 0
        explanation = "Automated analysis based on preliminary risk score. Please consult a doctor."
        recommendation = "Schedule a routine checkup."

        if data.preliminary_cri > 75:
            triage = "Critical"
            adjustment = 5
            explanation = "High risk indicators detected from both ML confidence and symptoms."
            recommendation = "Immediate consultation recommended."
        elif data.preliminary_cri > 50:
            triage = "High"
            adjustment = 2
            explanation = "Elevated risk score detected."
            recommendation = "Consult a specialist soon."
        elif data.preliminary_cri < 25:
             triage = "Low"
             explanation = "Low risk indicators."

        return LLMOutput(
            triage_level=triage,
            risk_adjustment=adjustment,
            explanation=explanation,
            recommendation=recommendation
        )

cognitive_service = CognitiveService()
