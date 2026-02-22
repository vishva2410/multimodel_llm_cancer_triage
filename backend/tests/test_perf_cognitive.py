import time
import json
import unittest
from unittest.mock import MagicMock, patch
from app.services.cognitive import CognitiveService
from app.models.schemas import LLMInput, LLMOutput

class TestCognitivePerformance(unittest.TestCase):
    def setUp(self):
        self.service = CognitiveService()
        # Mock the model to simulate network latency
        self.service.model = MagicMock()

        # Mock response structure
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "triage_level": "High",
            "risk_adjustment": 5,
            "explanation": "Test explanation",
            "recommendation": "Test recommendation"
        })

        def side_effect(*args, **kwargs):
            time.sleep(0.2) # Simulate 200ms API latency
            return mock_response

        self.service.model.generate_content.side_effect = side_effect

    def test_caching_performance(self):
        input_data = LLMInput(
            cancer_type="breast",
            ml_confidence=0.85,
            preliminary_cri=60,
            symptoms=["lump", "pain"],
            age=45,
            risk_factors=["smoking"]
        )

        print("\nRunning performance test...")

        # First call - should be slow (cache miss)
        start_time = time.time()
        self.service.analyze(input_data)
        first_call_time = time.time() - start_time
        print(f"First call time: {first_call_time:.4f}s")

        # Second call - should be fast if cached (cache hit)
        start_time = time.time()
        self.service.analyze(input_data)
        second_call_time = time.time() - start_time
        print(f"Second call time: {second_call_time:.4f}s")

        # Third call - same input
        start_time = time.time()
        self.service.analyze(input_data)
        third_call_time = time.time() - start_time
        print(f"Third call time: {third_call_time:.4f}s")

        # Verify performance improvement
        # Without caching, second_call_time will be ~0.2s
        # With caching, it should be < 0.05s

        self.assertLess(second_call_time, 0.05, "Caching failed: second call was too slow")
        print("✅ Caching is WORKING")

if __name__ == "__main__":
    unittest.main()
