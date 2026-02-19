import unittest
from unittest.mock import MagicMock, patch
from app.services.cognitive import CognitiveService
from app.models.schemas import LLMInput, LLMOutput

class TestCognitiveService(unittest.TestCase):
    def setUp(self):
        # Patch the GenerativeModel to prevent actual API calls
        self.genai_patcher = patch('app.services.cognitive.genai.GenerativeModel')
        self.MockGenerativeModel = self.genai_patcher.start()

        # Instantiate service with a fresh instance to avoid shared state
        # (Though CognitiveService in module is global, we create a new one for test)
        self.service = CognitiveService()
        self.service.model = self.MockGenerativeModel.return_value

        # Ensure cache is empty
        self.service._cache.clear()

    def tearDown(self):
        self.genai_patcher.stop()

    def test_caching(self):
        # Create a sample input
        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.9,
            preliminary_cri=80,
            symptoms=["cough", "chest pain"],
            age=65,
            risk_factors=["smoker"]
        )

        # Mock the generate_content method
        mock_response = MagicMock()
        mock_response.text = '{"triage_level": "Critical", "risk_adjustment": 5, "explanation": "Test explanation", "recommendation": "Test recommendation"}'
        self.service.model.generate_content.return_value = mock_response

        # First call: Should trigger API call
        result1 = self.service.analyze(input_data)

        # Verify API called once
        self.service.model.generate_content.assert_called_once()
        self.assertEqual(result1.triage_level, "Critical")

        # Second call: Should return cached result without API call
        result2 = self.service.analyze(input_data)

        # Verify API still called only once
        self.service.model.generate_content.assert_called_once()
        self.assertEqual(result1, result2)

    def test_cache_key_order_independence(self):
        # Input 1: Symptoms [A, B]
        input1 = LLMInput(
            cancer_type="lung",
            ml_confidence=0.9,
            preliminary_cri=80,
            symptoms=["A", "B"],
            age=65,
            risk_factors=["R1"]
        )

        # Input 2: Symptoms [B, A] (same content, different order)
        input2 = LLMInput(
            cancer_type="lung",
            ml_confidence=0.9,
            preliminary_cri=80,
            symptoms=["B", "A"],
            age=65,
            risk_factors=["R1"]
        )

        # Mock response
        mock_response = MagicMock()
        mock_response.text = '{"triage_level": "High", "risk_adjustment": 2, "explanation": "Test", "recommendation": "Test"}'
        self.service.model.generate_content.return_value = mock_response

        # Call with input1
        self.service.analyze(input1)
        self.service.model.generate_content.assert_called_once()

        # Call with input2 (should hit cache)
        self.service.analyze(input2)
        self.service.model.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
