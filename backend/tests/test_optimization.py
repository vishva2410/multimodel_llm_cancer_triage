import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import time
import collections

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.perception import perception_service
from app.services.cognitive import cognitive_service, CognitiveService
from app.models.schemas import LLMInput, LLMOutput

class TestOptimization(unittest.TestCase):
    def test_perception_determinism(self):
        print("\nTesting Perception Service Determinism...")
        image_data = b"fake_image_bytes_12345"

        # Call 1
        result1 = perception_service.predict(image_data, "lung")
        # Call 2
        result2 = perception_service.predict(image_data, "lung")

        print(f"Call 1: {result1.confidence}, {result1.prediction}")
        print(f"Call 2: {result2.confidence}, {result2.prediction}")

        if result1.confidence == result2.confidence and result1.prediction == result2.prediction:
             print("SUCCESS: Perception output is deterministic.")
        else:
             print("FAILURE: Perception output is NOT deterministic (Expected before optimization).")

    def test_cognitive_caching(self):
        print("\nTesting Cognitive Service Caching...")

        # Reset cache for test isolation (if implemented)
        if hasattr(cognitive_service, '_cache'):
            cognitive_service._cache.clear()
            print("Cache cleared.")
        else:
            print("Cache not implemented yet.")

        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=60,
            symptoms=["cough", "shortness of breath"],
            age=55,
            risk_factors=["smoker"]
        )

        # Patch the _mock_response (or API call) to be slow
        original_mock = cognitive_service._mock_response

        call_count = 0

        def slow_mock(data):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1) # Simulate 100ms latency
            return original_mock(data)

        # Temporarily replace method
        cognitive_service._mock_response = slow_mock
        # Also patch model to None to force mock path if API key is present
        original_model = cognitive_service.model
        cognitive_service.model = None

        try:
            # First call
            start = time.time()
            res1 = cognitive_service.analyze(input_data)
            duration1 = time.time() - start
            print(f"First call duration: {duration1:.4f}s")

            # Second call (same input)
            start = time.time()
            res2 = cognitive_service.analyze(input_data)
            duration2 = time.time() - start
            print(f"Second call duration: {duration2:.4f}s")

            if duration2 < 0.01 and call_count == 1:
                print("SUCCESS: Second call was instant and did not trigger processing (Cache Hit).")
            elif duration2 < duration1 * 0.5:
                 print("SUCCESS: Second call was significantly faster.")
            else:
                print("FAILURE: Second call was not faster (Cache Miss or No Cache).")

        finally:
            # Restore
            cognitive_service._mock_response = original_mock
            cognitive_service.model = original_model

if __name__ == "__main__":
    unittest.main()
