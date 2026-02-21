import time
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock
from app.models.schemas import LLMInput
from app.services.cognitive import CognitiveService

# Mock response object
class MockResponse:
    def __init__(self, text):
        self.text = text

class TestCognitivePerformance(unittest.TestCase):
    def setUp(self):
        self.service = CognitiveService()
        self.service.model = MagicMock()

        # Simulate a slow generate_content_async
        async def slow_generate_content(*args, **kwargs):
            await asyncio.sleep(1.0) # Simulate 1s latency
            return MockResponse('{"triage_level": "High", "risk_adjustment": 5, "explanation": "Test", "recommendation": "Test"}')

        self.service.model.generate_content_async = AsyncMock(side_effect=slow_generate_content)

    def test_analyze_performance_and_correctness(self):
        input_data = LLMInput(
            cancer_type="lung",
            ml_confidence=0.85,
            preliminary_cri=60,
            symptoms=["cough", "shortness of breath"],
            age=65,
            risk_factors=["smoker"]
        )

        async def run_test():
            start_time = time.time()

            # 1. First call (Cache Miss)
            result1 = await self.service.analyze(input_data)
            time1 = time.time()

            # 2. Second call (Cache Hit)
            result2 = await self.service.analyze(input_data)
            time2 = time.time()

            duration_total = time2 - start_time
            duration_second = time2 - time1

            print(f"\nFirst call took {time1 - start_time:.4f} seconds")
            print(f"Second call took {duration_second:.4f} seconds")

            # Verification
            # 1. Performance: Second call should be instant
            self.assertLess(duration_second, 0.1, "Cache hit should be instant")

            # 2. Correctness: Results should be identical in content
            self.assertEqual(result1.triage_level, result2.triage_level)
            self.assertEqual(result1.explanation, result2.explanation)

            # 3. Safety: Result should be a copy (not same object identity)
            self.assertIsNot(result1, result2, "Cached result should be a copy")

            # 4. Cache Key Logic: Permuted lists should still hit cache
            input_permuted = LLMInput(
                cancer_type="lung",
                ml_confidence=0.85,
                preliminary_cri=60,
                symptoms=["shortness of breath", "cough"], # Swapped order
                age=65,
                risk_factors=["smoker"]
            )

            start_permuted = time.time()
            result3 = await self.service.analyze(input_permuted)
            duration_permuted = time.time() - start_permuted

            print(f"Permuted input call took {duration_permuted:.4f} seconds")
            self.assertLess(duration_permuted, 0.1, "Permuted list input should hit cache")
            self.assertEqual(result1.explanation, result3.explanation)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
