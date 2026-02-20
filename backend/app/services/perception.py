import random
import zlib
from app.models.schemas import PerceptionOutput

class PerceptionService:
    def predict(self, image_data: bytes, cancer_type: str) -> PerceptionOutput:
        # Mock logic to simulate CNN inference
        # In a real scenario, this would load a model and run inference
        
        # Seed random with image content checksum for determinism
        checksum = zlib.adler32(image_data)
        rng = random.Random(checksum)

        # Simulate high confidence for demo purposes if specific keywords in filename or mocking
        # For now, return a random but generally high confidence for "suspected" cases
        
        confidence = round(rng.uniform(0.7, 0.99), 2)
        prediction = "suspected"
        
        # Occasional low confidence or negative result simulation
        if rng.random() < 0.1:
            prediction = "normal"
            confidence = round(rng.uniform(0.8, 0.95), 2)
        elif rng.random() < 0.15:
            confidence = round(rng.uniform(0.4, 0.6), 2)
            prediction = "inconclusive"

        return PerceptionOutput(prediction=prediction, confidence=confidence)

perception_service = PerceptionService()
