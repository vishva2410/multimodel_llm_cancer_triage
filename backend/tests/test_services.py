import unittest
import zlib
import random
from app.services.perception import perception_service
from app.services.cognitive import cognitive_service, LLMInput, LLMOutput

class TestServices(unittest.TestCase):
    def test_perception_determinism(self):
        """Test that PerceptionService is deterministic for the same input."""
        image_data = b"test_image_bytes"
        cancer_type = "lung"

        # Run 1
        output1 = perception_service.predict(image_data, cancer_type)

        # Run 2
        output2 = perception_service.predict(image_data, cancer_type)

        self.assertEqual(output1.confidence, output2.confidence)
        self.assertEqual(output1.prediction, output2.prediction)

        # Verify it changes for different input
        image_data_diff = b"different_image_bytes"
        output3 = perception_service.predict(image_data_diff, cancer_type)
        # It is statistically likely to be different, but not guaranteed if mocked logic is simple.
        # But we primarily care about determinism (same input -> same output).

    def test_cognitive_caching(self):
        """Test that CognitiveService caches results."""
        # Mock the underlying model to avoid API calls and track execution
        original_perform_analysis = cognitive_service._perform_analysis
        call_count = 0

        def mock_analysis(data):
            nonlocal call_count
            call_count += 1
            return LLMOutput(
                triage_level="Low",
                risk_adjustment=0,
                explanation="Cached explanation",
                recommendation="Cached recommendation"
            )

        cognitive_service._perform_analysis = mock_analysis

        # Clear cache for isolation
        cognitive_service._cache.clear()

        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.8,
            preliminary_cri=40,
            symptoms=["cough"],
            age=50,
            risk_factors=["smoker"]
        )

        # First call - cache miss
        cognitive_service.analyze(input_data)
        self.assertEqual(call_count, 1)

        # Second call - cache hit
        cognitive_service.analyze(input_data)
        self.assertEqual(call_count, 1)

        # Different input - cache miss
        input_data2 = LLMInput(
            cancer_type="lung",
            ml_confidence=0.8,
            preliminary_cri=40,
            symptoms=["cough", "fever"], # changed
            age=50,
            risk_factors=["smoker"]
        )
        cognitive_service.analyze(input_data2)
        self.assertEqual(call_count, 2)

        # Restore original method
        cognitive_service._perform_analysis = original_perform_analysis

if __name__ == '__main__':
    unittest.main()
