import unittest
import sys
import os
import collections
from unittest.mock import MagicMock, patch

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.perception import perception_service, PerceptionService
from app.services.cognitive import cognitive_service, CognitiveService, LLMInput, LLMOutput

class TestServices(unittest.TestCase):
    def test_perception_determinism(self):
        # Image data as bytes
        image_data = b"test_image_data_for_determinism"

        # Call predict twice
        result1 = perception_service.predict(image_data, "lung")
        result2 = perception_service.predict(image_data, "lung")

        # Verify determinism
        # This will fail until we implement determinism
        self.assertEqual(result1.confidence, result2.confidence)
        self.assertEqual(result1.prediction, result2.prediction)

    def test_cognitive_caching(self):
        # Create a fresh service instance to avoid side effects
        service = CognitiveService()

        # Mock _mock_response to track calls (since model might be None)
        service._mock_response = MagicMock(return_value=LLMOutput(
            triage_level="Low",
            risk_adjustment=0,
            explanation="Mock explanation",
            recommendation="Mock recommendation"
        ))
        # Ensure model is None so it uses _mock_response
        service.model = None

        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=40,
            symptoms=["cough", "shortness of breath"],
            age=65,
            risk_factors=["smoker"]
        )

        # First call
        result1 = service.analyze(input_data)

        # Second call with same input
        result2 = service.analyze(input_data)

        # Verify result is same
        self.assertEqual(result1, result2)

        # Verify _mock_response was called only once if caching works
        # This will fail until we implement caching
        service._mock_response.assert_called_once()

    def test_cognitive_caching_order_independence(self):
        service = CognitiveService()
        service._mock_response = MagicMock(return_value=LLMOutput(
            triage_level="Low",
            risk_adjustment=0,
            explanation="Mock explanation",
            recommendation="Mock recommendation"
        ))
        service.model = None

        input_data1 = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=40,
            symptoms=["cough", "shortness of breath"], # order 1
            age=65,
            risk_factors=["smoker", "age"] # order 1
        )

        input_data2 = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=40,
            symptoms=["shortness of breath", "cough"], # order 2 (swapped)
            age=65,
            risk_factors=["age", "smoker"] # order 2 (swapped)
        )

        service.analyze(input_data1)
        service.analyze(input_data2)

        # Should be 1 call if order independence works
        # This will fail until we implement sorted keys
        service._mock_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()
