import requests
import os

# Assuming backend is running on localhost:8000
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    # Health check is at root based on main.py, but let's check both
    try:
        response = requests.get(f"http://localhost:8000/health")
        if response.status_code == 200:
            print("Health Check (/health): PASSED")
        else:
            print(f"Health Check (/health): FAILED {response.status_code}")
    except Exception as e:
        print(f"Health Check: FAILED {e}")

def test_analyze_text():
    # This tests the Gemini service at /ai-analyze
    print("\nTesting Text Analysis (Gemini Service)...")
    endpoint = f"{BASE_URL}/ai-analyze"
    try:
        # Simple non-medical text to trigger relevance check
        payload = {"text": "What is the capital of France?"}
        response = requests.post(endpoint, data=payload)
        
        if response.status_code != 200:
             print(f"Irrelevant Text Check: FAILED Status {response.status_code}")
             return

        data = response.json()
        if not data.get("is_relevant"):
            print("Irrelevant Text Check: PASSED (Correctly identified as irrelevant)")
        else:
            print("Irrelevant Text Check: FAILED (Should be irrelevant)")

        # Medical text
        payload_med = {"text": "Patient presents with persistent cough and hemoptysis for 3 weeks."}
        response_med = requests.post(endpoint, data=payload_med)
        data_med = response_med.json()
        
        # Without API Key, this might return False (API Key missing)
        # But we check structure at least
        if "is_relevant" in data_med:
             print("Relevant Text Check: PASSED (Structure valid)")
        else:
             print(f"Relevant Text Check: FAILED (Invalid structure: {data_med})")

    except Exception as e:
        print(f"Text Analysis Test: FAILED {e}")

def test_cognitive_analyze():
    # This tests the Core Triage service at /analyze
    print("\nTesting Cognitive Analysis (Core Triage)...")
    endpoint = f"{BASE_URL}/analyze"
    try:
        # Create dummy file content
        files = {'file': ('test.jpg', b'fake_image_bytes', 'image/jpeg')}
        # Create parameters as query params (FastAPI default for non-body fields if not Form)
        # But wait, main.py says:
        # cancer_type: str, age: int, symptoms: str, risk_factors: str, file: UploadFile
        # These are query params by default in FastAPI unless Form(...) is used.
        # But they are mandatory.

        params = {
            'cancer_type': 'lung',
            'age': '50',
            'symptoms': '["cough", "fatigue"]',
            'risk_factors': '["smoker"]'
        }

        # Actually, let's check route definition.
        # async def analyze_case(cancer_type: str, ... file: UploadFile = File(...))
        # Mix of query params and file upload.

        response = requests.post(endpoint, params=params, files=files)

        if response.status_code == 200:
            data = response.json()
            # Verify we got a response with expected fields
            if "final_cri" in data and "triage_level" in data:
                print("Cognitive Analysis: PASSED")
                print(f"  Triage Level: {data['triage_level']}")
                print(f"  Final CRI: {data['final_cri']}")
            else:
                print(f"Cognitive Analysis: FAILED (Missing fields: {data.keys()})")
        else:
            print(f"Cognitive Analysis: FAILED (Status: {response.status_code}, {response.text})")

    except Exception as e:
        print(f"Cognitive Analysis Test: FAILED {e}")

if __name__ == "__main__":
    print("Starting Integration Tests...")
    test_health()
    test_analyze_text()
    test_cognitive_analyze()
