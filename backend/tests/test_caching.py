import sys
import os
import unittest
from unittest.mock import MagicMock

# Add backend directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.perception import perception_service
from app.services.cognitive import cognitive_service, LLMInput

class TestOptimization(unittest.TestCase):
    def test_perception_determinism(self):
        print("\nTesting Perception Service Determinism...")
        image_data = b"fake_image_content_12345"

        # First call
        result1 = perception_service.predict(image_data, "lung")
        # Second call
        result2 = perception_service.predict(image_data, "lung")

        print(f"Run 1: {result1.confidence}, {result1.prediction}")
        print(f"Run 2: {result2.confidence}, {result2.prediction}")

        if result1.confidence != result2.confidence:
            print("FAIL: Perception results differ (Non-deterministic)")
        else:
            print("PASS: Perception results identical")

        self.assertEqual(result1.confidence, result2.confidence)
        self.assertEqual(result1.prediction, result2.prediction)

    def test_cognitive_caching(self):
        print("\nTesting Cognitive Service Caching...")

        # Setup inputs
        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=60,
            symptoms=["cough", "shortness of breath"],
            age=55,
            risk_factors=["smoker"]
        )

        # Reset any existing cache if possible (though services are singletons)
        if hasattr(cognitive_service, "_cache"):
            cognitive_service._cache.clear()

        # Mock the actual generation method to count calls
        # Since API key is missing, it falls back to _mock_response
        original_method = cognitive_service._mock_response
        mock_method = MagicMock(side_effect=original_method)
        cognitive_service._mock_response = mock_method

        # First call
        print("Calling analyze (1st time)...")
        result1 = cognitive_service.analyze(input_data)

        # Second call
        print("Calling analyze (2nd time)...")
        result2 = cognitive_service.analyze(input_data)

        call_count = mock_method.call_count
        print(f"Generation method called {call_count} times")

        # Restore original method
        cognitive_service._mock_response = original_method

        if call_count == 1:
             print("PASS: Caching works (Method called once)")
        else:
             print(f"FAIL: Method called {call_count} times (Expected 1)")

        self.assertEqual(call_count, 1)
        self.assertEqual(result1.triage_level, result2.triage_level)

if __name__ == '__main__':
    unittest.main()
