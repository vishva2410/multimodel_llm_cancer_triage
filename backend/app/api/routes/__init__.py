from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.models.schemas import PatientInput, FinalResult, LLMInput
from app.services.perception import perception_service
from app.services.risk import risk_service
from app.services.cognitive import cognitive_service
from app.services.hospital import hospital_service
import json

router = APIRouter()

@router.post("/analyze", response_model=FinalResult)
async def analyze_case(
    cancer_type: str,
    age: int,
    symptoms: str, # JSON string
    risk_factors: str, # JSON string
    file: UploadFile = File(...)
):
    try:
        symptoms_list = json.loads(symptoms)
        risk_factors_list = json.loads(risk_factors)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for symptoms or risk_factors")

    input_data = PatientInput(
        cancer_type=cancer_type,
        age=age,
        symptoms=symptoms_list,
        risk_factors=risk_factors_list
    )

    # 1. Perception Layer
    perception = perception_service.predict(await file.read(), cancer_type)
    
    # 2. Risk Aggregation Layer
    preliminary_cri = risk_service.calculate_preliminary_cri(input_data, perception)
    
    # 3. Cognitive Layer
    llm_input = LLMInput(
        cancer_type=cancer_type,
        ml_confidence=perception.confidence,
        preliminary_cri=preliminary_cri,
        symptoms=symptoms_list,
        age=age,
        risk_factors=risk_factors_list
    )
    llm_output = await cognitive_service.analyze(llm_input)
    
    # 4. Final Calculation
    final_cri = max(0, min(100, preliminary_cri + llm_output.risk_adjustment))
    
    # 5. Hospital Recommendation
    hospital_rec = hospital_service.recommend(cancer_type)
    
    return FinalResult(
        cancer_type=cancer_type,
        ml_confidence=perception.confidence,
        preliminary_cri=preliminary_cri,
        final_cri=final_cri,
        triage_level=llm_output.triage_level,
        explanation=llm_output.explanation,
        recommendation=llm_output.recommendation,
        hospital_recommendation=hospital_rec
    )
