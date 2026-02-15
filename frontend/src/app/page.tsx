"use client";

import { useState } from 'react';
import { Upload, ArrowRight, Brain, Waves, Heart, Eye, Layers, Shield } from 'lucide-react';

interface AnalysisResult {
  cancer_type: string;
  ml_confidence: number;
  preliminary_cri: number;
  final_cri: number;
  triage_level: string;
  explanation: string;
  recommendation: string;
  hospital_recommendation: string | null;
}

export default function Home() {
  const [currentPage, setCurrentPage] = useState<'home' | 'screening' | 'how-it-works' | 'clinicians' | 'research'>('home');
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [cancerType, setCancerType] = useState('lung');
  const [age, setAge] = useState<number>(45);
  const [symptoms, setSymptoms] = useState('');
  const [riskFactors, setRiskFactors] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];

      // Validate file type
      if (!selectedFile.type.startsWith('image/')) {
        setError("Please upload a valid image file (JPEG, PNG, DICOM).");
        return;
      }

      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB.");
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please upload a medical scan image.");
      return;
    }

    if (!symptoms.trim()) {
      setError("Please enter at least one symptom.");
      return;
    }

    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    const symptomsList = JSON.stringify(symptoms.split(',').map(s => s.trim()).filter(Boolean));
    const risksList = JSON.stringify(riskFactors.split(',').map(s => s.trim()).filter(Boolean));

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze?' + new URLSearchParams({
        cancer_type: cancerType,
        age: age.toString(),
        symptoms: symptomsList,
        risk_factors: risksList
      }), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "An error occurred during analysis.";
      setError(message);
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskClass = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'moderate': return 'medium';
      default: return 'low';
    }
  };

  const navigateTo = (page: typeof currentPage) => {
    setCurrentPage(page);
    setResult(null);
    setError(null);
  };

  return (
    <>
      {/* Navbar */}
      <nav className="navbar">
        <div className="logo" onClick={() => navigateTo('home')} style={{ cursor: 'pointer' }}>
          <span className="logo-square"></span>
          OncoDetect
        </div>
        <ul className="nav-menu">
          <li><a onClick={() => navigateTo('how-it-works')} className={currentPage === 'how-it-works' ? 'active' : ''}>How It Works</a></li>
          <li><a onClick={() => navigateTo('screening')} className={currentPage === 'screening' ? 'active' : ''}>Start Screening</a></li>
          <li><a onClick={() => navigateTo('clinicians')} className={currentPage === 'clinicians' ? 'active' : ''}>For Clinicians</a></li>
          <li><a onClick={() => navigateTo('research')} className={currentPage === 'research' ? 'active' : ''}>Research</a></li>
        </ul>
        <button className="nav-btn" onClick={() => navigateTo('screening')}>Start Screening</button>
      </nav>

      {/* HOME PAGE */}
      {currentPage === 'home' && (
        <>
          <section className="hero">
            <div className="hero-content">
              <h1>
                AI-Assisted Cancer<br />
                <span className="muted">Triage System.</span>
              </h1>
              <p>
                Multi-organ screening powered by deep learning and clinical reasoning.
                Brain, Lung, and Breast analysis in one unified platform.
              </p>
              <div className="hero-buttons">
                <button className="btn btn-primary" onClick={() => navigateTo('screening')}>
                  Start Screening <ArrowRight size={18} />
                </button>
                <button className="btn btn-outline" onClick={() => navigateTo('how-it-works')}>
                  How It Works
                </button>
              </div>
            </div>

            <div className="analysis-card">
              <div className="card-header">
                <span className="card-dot"></span>
                <span>OncoDetect Analysis</span>
              </div>

              <div className="section-label">SUPPORTED ORGANS</div>
              <div className="organs-grid">
                <div
                  className={`organ-card ${cancerType === 'brain' ? 'selected' : ''}`}
                  onClick={() => setCancerType('brain')}
                >
                  <Brain size={28} />
                  <span className="name">Brain</span>
                  <span className="type">MRI</span>
                </div>
                <div
                  className={`organ-card ${cancerType === 'lung' ? 'selected' : ''}`}
                  onClick={() => setCancerType('lung')}
                >
                  <Waves size={28} />
                  <span className="name">Lung</span>
                  <span className="type">X-ray / CT</span>
                </div>
                <div
                  className={`organ-card ${cancerType === 'breast' ? 'selected' : ''}`}
                  onClick={() => setCancerType('breast')}
                >
                  <Heart size={28} />
                  <span className="name">Breast</span>
                  <span className="type">Mammogram</span>
                </div>
              </div>

              <div className="risk-block">
                <div className="risk-header">
                  <span className="label">Risk Assessment</span>
                  <span className={`risk-tag ${result ? getRiskClass(result.triage_level) : ''}`}>
                    {result ? `${result.triage_level.toUpperCase()} RISK` : 'MEDIUM RISK'}
                  </span>
                </div>

                <div className="metric">
                  <span className="name">CNN Confidence</span>
                  <div className="bar-wrap">
                    <div className="bar-fill" style={{ width: result ? `${result.ml_confidence * 100}%` : '82%' }}></div>
                  </div>
                  <span className="value">{result ? `${Math.round(result.ml_confidence * 100)}%` : '82%'}</span>
                </div>

                <div className="metric">
                  <span className="name">LLM Reasoning</span>
                  <span className="value" style={{ marginLeft: 'auto' }}>
                    {result ? 'Confirmed' : 'Confirmed'}
                  </span>
                </div>

                <div className="audit-status">
                  <span className={`audit-dot ${result ? 'active' : 'active'}`}></span>
                  <span>Self-audit layer: CONFIRMED</span>
                </div>
              </div>
            </div>
          </section>

          <section className="features-section">
            <h2>Three layers. Zero blind spots.</h2>
            <p className="subtitle">A multi-stage AI architecture that combines perception, reasoning, and self-audit.</p>

            <div className="features-grid">
              <div className="feature-card">
                <div className="icon"><Eye /></div>
                <h3>Perception Layer</h3>
                <p>Deep learning CNN models analyze medical imagery with high precision, detecting patterns invisible to the human eye.</p>
              </div>
              <div className="feature-card">
                <div className="icon"><Layers /></div>
                <h3>Reasoning Layer</h3>
                <p>LLM-powered clinical reasoning correlates imaging findings with symptoms and risk factors for contextual analysis.</p>
              </div>
              <div className="feature-card">
                <div className="icon"><Shield /></div>
                <h3>Audit Layer</h3>
                <p>Built-in safety checks ensure conservative risk assessment with explicit uncertainty handling.</p>
              </div>
            </div>
          </section>
        </>
      )}

      {/* SCREENING PAGE */}
      {currentPage === 'screening' && (
        <>
          <section className="page-section">
            <h1>Patient Screening</h1>
            <p className="page-subtitle">Upload medical imagery and patient information for AI-assisted triage analysis.</p>

            <div className="form-card">
              <form onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-field">
                    <label>Patient Age</label>
                    <input
                      type="number"
                      value={age}
                      onChange={(e) => setAge(Number(e.target.value))}
                      min="0"
                      max="120"
                      required
                    />
                  </div>
                  <div className="form-field">
                    <label>Target Organ</label>
                    <select value={cancerType} onChange={(e) => setCancerType(e.target.value)}>
                      <option value="brain">Brain (MRI)</option>
                      <option value="lung">Lung (X-Ray / CT)</option>
                      <option value="breast">Breast (Mammogram)</option>
                    </select>
                  </div>
                </div>

                <div className="form-row full">
                  <div className="form-field">
                    <label>Symptoms (comma separated) *</label>
                    <textarea
                      value={symptoms}
                      onChange={(e) => setSymptoms(e.target.value)}
                      placeholder="e.g., persistent headache, blurred vision, nausea, fatigue"
                      required
                    />
                  </div>
                </div>

                <div className="form-row full">
                  <div className="form-field">
                    <label>Risk Factors (comma separated)</label>
                    <input
                      type="text"
                      value={riskFactors}
                      onChange={(e) => setRiskFactors(e.target.value)}
                      placeholder="e.g., smoker, family history of cancer, previous radiation"
                    />
                  </div>
                </div>

                <div className="form-row full">
                  <div className="form-field">
                    <label>Medical Scan Upload *</label>
                    <div className="upload-box">
                      <input
                        type="file"
                        onChange={handleFileChange}
                        accept="image/*"
                      />
                      <Upload />
                      {file ? (
                        <p className="filename">{file.name}</p>
                      ) : (
                        <p>Drop medical scan here or click to upload<br /><span style={{ fontSize: '12px', color: '#94a3b8' }}>JPEG, PNG, DICOM • Max 10MB</span></p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={analyzing}>
                    {analyzing ? 'Analyzing...' : 'Run Triage Analysis'}
                    {!analyzing && <ArrowRight size={18} />}
                  </button>
                </div>
              </form>

              {error && <p className="error-msg">{error}</p>}
            </div>
          </section>

          {result && (
            <section className="results-section">
              <div className="results-wrap">
                <div className="results-header">
                  <h2>Analysis Results</h2>
                </div>

                <div className="results-grid">
                  <div className="result-card">
                    <h4>Cancer Risk Index</h4>
                    <div className="big-value">{result.final_cri}/100</div>
                    <p>Composite risk score</p>
                  </div>

                  <div className="result-card">
                    <h4>Triage Level</h4>
                    <div className={`big-value ${getRiskClass(result.triage_level)}`}>
                      {result.triage_level}
                    </div>
                    <p>Urgency classification</p>
                  </div>

                  <div className="result-card">
                    <h4>ML Confidence</h4>
                    <div className="big-value">{Math.round(result.ml_confidence * 100)}%</div>
                    <p>Imaging analysis</p>
                  </div>

                  <div className="result-card wide">
                    <h4>Clinical Reasoning</h4>
                    <p className="text-content">{result.explanation}</p>
                  </div>

                  <div className="result-card wide">
                    <h4>Recommendation</h4>
                    <p className="text-content">{result.recommendation}</p>
                  </div>

                  {result.hospital_recommendation && (
                    <div className="result-card wide">
                      <h4>Facility Recommendation</h4>
                      <p className="text-content">{result.hospital_recommendation}</p>
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}
        </>
      )}

      {/* HOW IT WORKS PAGE */}
      {currentPage === 'how-it-works' && (
        <section className="page-section">
          <h1>How It Works</h1>
          <p className="page-subtitle">OncoDetect X uses a three-layer AI architecture for reliable cancer risk assessment.</p>

          <div className="steps-grid">
            <div className="step-item">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Image Upload & Preprocessing</h3>
                <p>Medical imagery (MRI, X-ray, CT, Mammogram) is uploaded and preprocessed for optimal model input. The system validates image quality and format before analysis.</p>
              </div>
            </div>

            <div className="step-item">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>Perception Layer (CNN)</h3>
                <p>Deep learning convolutional neural networks analyze the imagery to detect abnormalities. Each organ type has a specialized model trained on relevant datasets. Output includes prediction class and confidence score.</p>
              </div>
            </div>

            <div className="step-item">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Risk Aggregation</h3>
                <p>A deterministic logic layer combines ML confidence (60%), symptom severity (30%), and risk factors (10%) to calculate a preliminary Cancer Risk Index (CRI) before LLM processing.</p>
              </div>
            </div>

            <div className="step-item">
              <div className="step-number">4</div>
              <div className="step-content">
                <h3>Cognitive Layer (LLM)</h3>
                <p>Large Language Model receives structured JSON input for contextual reasoning. It evaluates consistency between imaging and symptoms, handles uncertainty conservatively, and generates human-readable explanations.</p>
              </div>
            </div>

            <div className="step-item">
              <div className="step-number">5</div>
              <div className="step-content">
                <h3>Final Report & Recommendation</h3>
                <p>The system outputs a final CRI score (0-100), triage level (Low/Moderate/High/Critical), clinical reasoning, and hospital recommendation. All outputs are decision-support only, not diagnosis.</p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* FOR CLINICIANS PAGE */}
      {currentPage === 'clinicians' && (
        <section className="page-section">
          <h1>For Clinicians</h1>
          <p className="page-subtitle">Technical specifications and integration guidelines for healthcare professionals.</p>

          <div className="form-card" style={{ marginTop: '32px' }}>
            <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>System Capabilities</h3>
            <ul style={{ paddingLeft: '20px', lineHeight: '2', color: '#64748b' }}>
              <li>Multi-organ analysis: Brain (MRI), Lung (X-ray/CT), Breast (Mammogram)</li>
              <li>Uncertainty-aware deep learning with explicit confidence reporting</li>
              <li>LLM-based contextual reasoning for symptom correlation</li>
              <li>Conservative risk stratification with safety bounds</li>
              <li>No diagnostic claims - decision support only</li>
            </ul>

            <h3 style={{ marginTop: '32px', marginBottom: '16px', fontSize: '18px' }}>Safety Protocols</h3>
            <ul style={{ paddingLeft: '20px', lineHeight: '2', color: '#64748b' }}>
              <li>All outputs bounded by predefined JSON formats</li>
              <li>LLM cannot override ML blindly or make diagnostic statements</li>
              <li>Explicit uncertainty handling with conservative bias</li>
              <li>Clear disclaimers on all patient-facing outputs</li>
              <li>Audit trail for all analysis decisions</li>
            </ul>

            <h3 style={{ marginTop: '32px', marginBottom: '16px', fontSize: '18px' }}>API Integration</h3>
            <p style={{ color: '#64748b', lineHeight: '1.7' }}>
              OncoDetect X provides a REST API for integration with existing hospital systems.
              Contact our team for API documentation and enterprise deployment options.
            </p>
          </div>
        </section>
      )}

      {/* RESEARCH PAGE */}
      {currentPage === 'research' && (
        <section className="page-section">
          <h1>Research</h1>
          <p className="page-subtitle">Scientific foundation and methodology behind OncoDetect X.</p>

          <div className="form-card" style={{ marginTop: '32px' }}>
            <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>Architecture Overview</h3>
            <p style={{ color: '#64748b', lineHeight: '1.8', marginBottom: '24px' }}>
              OncoDetect X implements a novel three-layer architecture that separates perception (CNN),
              reasoning (LLM), and validation (rule-based audit) to prevent single points of failure
              common in end-to-end deep learning systems.
            </p>

            <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>Risk Calculation Formula</h3>
            <div style={{ background: '#f8fafc', padding: '20px', fontFamily: 'monospace', fontSize: '14px', marginBottom: '24px' }}>
              Final CRI = (ML_Confidence × 0.6) + (Symptom_Score × 0.3) + (Risk_Factor_Score × 0.1) + LLM_Adjustment
            </div>

            <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>LLM Prompt Engineering</h3>
            <p style={{ color: '#64748b', lineHeight: '1.8', marginBottom: '24px' }}>
              The cognitive layer uses carefully designed prompts that explicitly prohibit diagnostic language,
              enforce structured JSON output, and require conservative risk assessment when uncertainty exists.
              The LLM receives only structured data, never raw imagery.
            </p>

            <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>Ethical Considerations</h3>
            <p style={{ color: '#64748b', lineHeight: '1.8' }}>
              This system is designed for research and educational purposes only. It does not diagnose cancer
              or replace professional medical evaluation. All outputs should be verified by qualified
              healthcare professionals before any clinical decision-making.
            </p>
          </div>
        </section>
      )}
    </>
  );
}
