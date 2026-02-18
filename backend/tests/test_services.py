import unittest
from unittest.mock import MagicMock, patch
from app.services.perception import perception_service
from app.services.cognitive import cognitive_service
from app.models.schemas import LLMInput, LLMOutput
import json

class TestServices(unittest.TestCase):
    def test_perception_determinism(self):
        """Test that PerceptionService returns deterministic results for the same image data."""
        image_data = b"fake_image_content_for_testing_determinism"

        # First call
        output1 = perception_service.predict(image_data, "lung")

        # Second call
        output2 = perception_service.predict(image_data, "lung")

        self.assertEqual(output1.confidence, output2.confidence, "Confidence should be identical for same image")
        self.assertEqual(output1.prediction, output2.prediction, "Prediction should be identical for same image")

        # Different image
        image_data_diff = b"different_image_content"
        output3 = perception_service.predict(image_data_diff, "lung")

        # Note: There's a small chance output3 matches output1/2 by coincidence, but with floats it's unlikely
        # However, for correctness, we only strictly test determinism of same input.

    def test_cognitive_caching(self):
        """Test that CognitiveService caches results for identical inputs."""
        # Clear cache first just in case
        cognitive_service.cache.clear()

        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=60,
            symptoms=["cough", "shortness of breath"],
            age=55,
            risk_factors=["smoker"]
        )

        # First call
        result1 = cognitive_service.analyze(input_data)

        # Verify it's in cache
        cache_key = (
            input_data.cancer_type,
            input_data.ml_confidence,
            input_data.preliminary_cri,
            tuple(sorted(input_data.symptoms)),
            input_data.age,
            tuple(sorted(input_data.risk_factors))
        )
        self.assertIn(cache_key, cognitive_service.cache)
        self.assertEqual(cognitive_service.cache[cache_key], result1)

        # Second call
        # We patch both potential methods that generate responses to ensure neither is called
        with patch.object(cognitive_service, '_mock_response', side_effect=cognitive_service._mock_response) as mock_method:
             with patch.object(cognitive_service, '_call_llm', side_effect=cognitive_service._call_llm) as mock_llm:
                result2 = cognitive_service.analyze(input_data)

                # Check that result is same
                self.assertEqual(result1, result2)

                # Verify methods were NOT called because of cache hit
                mock_method.assert_not_called()
                mock_llm.assert_not_called()

    def test_cognitive_cache_eviction(self):
        """Test that cache respects size limit."""
        cognitive_service.cache.clear()
        original_size = cognitive_service.CACHE_SIZE
        cognitive_service.CACHE_SIZE = 2 # Set small size for testing

        try:
            # Add 3 items
            for i in range(3):
                data = LLMInput(
                    cancer_type="lung",
                    ml_confidence=0.8,
                    preliminary_cri=50 + i,
                    symptoms=["cough"],
                    age=50,
                    risk_factors=[]
                )
                cognitive_service.analyze(data)

            self.assertEqual(len(cognitive_service.cache), 2)

            # The first one (i=0) should be evicted
            # Note: symptoms and risk_factors are lists in input, but tuples in key
            first_key = ("lung", 0.8, 50, tuple(["cough"]), 50, tuple([]))
            self.assertNotIn(first_key, cognitive_service.cache)

            # The last one (i=2) should be present
            last_key = ("lung", 0.8, 52, tuple(["cough"]), 50, tuple([]))
            self.assertIn(last_key, cognitive_service.cache)

        finally:
            cognitive_service.CACHE_SIZE = original_size

if __name__ == '__main__':
    unittest.main()
