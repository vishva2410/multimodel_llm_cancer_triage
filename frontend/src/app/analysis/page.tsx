'use client';

import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';
import { Upload, FileText, AlertCircle, CheckCircle, Activity, Brain } from 'lucide-react';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface ChartData {
    cancer_types_probability?: Record<string, number>;
    risk_factors?: Record<string, number>;
}

interface AnalysisResult {
    is_relevant: boolean;
    reason: string;
    analysis?: string;
    chart_data?: ChartData;
}

export default function AnalysisPage() {
    const [file, setFile] = useState<File | null>(null);
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState('');
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            setPreviewUrl(URL.createObjectURL(selectedFile));
            setError('');
        }
    };

    const handleAnalyze = async () => {
        if (!file && !text) {
            setError('Please provide at least an image or text input.');
            return;
        }

        setLoading(true);
        setError('');
        setResult(null);

        const formData = new FormData();
        if (file) formData.append('file', file);
        if (text) formData.append('text', text);

        try {
            const response = await axios.post('http://localhost:8000/api/v1/ai-analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err: unknown) {
            console.error(err);
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail || 'An error occurred during analysis.');
            } else {
                setError('An unexpected error occurred.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Prepare chart data helpers
    const renderProbabilityChart = (data: ChartData) => {
        if (!data?.cancer_types_probability) return null;

        const probs = data.cancer_types_probability;
        const x = Object.keys(probs);
        const y: number[] = Object.values(probs).map((v) => (v) * 100);

        return (
            <Plot
                data={[
                    {
                        x: x,
                        y: y,
                        type: 'bar',
                        marker: { color: ['#10b981', '#ef4444', '#f59e0b', '#8b5cf6'] },
                    },
                ]}
                layout={{
                    title: { text: 'Malignancy Probability (%)' },
                    yaxis: { range: [0, 100] },
                    autosize: true,
                    margin: { l: 40, r: 20, t: 40, b: 40 },
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '300px' }}
            />
        );
    };

    const renderRiskChart = (data: ChartData) => {
        if (!data?.risk_factors) return null;

        const risks = data.risk_factors;
        const categories = Object.keys(risks);
        const values: number[] = Object.values(risks) as number[];

        return (
            <Plot
                data={[
                    {
                        type: 'scatterpolar',
                        r: values,
                        theta: categories,
                        fill: 'toself',
                        name: 'Risk Factors',
                    },
                ]}
                layout={{
                    polar: {
                        radialaxis: {
                            visible: true,
                            range: [0, 10],
                        },
                    },
                    title: { text: 'Risk Factor Analysis (0-10)' },
                    autosize: true,
                    margin: { l: 40, r: 40, t: 40, b: 40 },
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '300px' }}
            />
        );
    };

    return (
        <div className="min-h-screen bg-slate-50 pt-24 pb-12 px-4 sm:px-6 lg:px-8">
            <div className="max-width-1400 mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-extrabold text-slate-900 sm:text-5xl mb-4">
                        AI Oncologist <span className="text-blue-600">Analysis</span>
                    </h1>
                    <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                        Advanced multi-modal analysis for cancer detection and risk assessment using Gemini AI.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Input Section */}
                    <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                            <Upload className="w-6 h-6 text-blue-600" />
                            Case Input
                        </h2>

                        <div className="space-y-6">
                            {/* Image Upload */}
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">
                                    Medical Imaging (CT, MRI, X-Ray)
                                </label>
                                <div
                                    className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all ${previewUrl ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'
                                        }`}
                                >
                                    <input
                                        type="file"
                                        accept="image/*"
                                        onChange={handleFileChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    {previewUrl ? (
                                        // eslint-disable-next-line @next/next/no-img-element
                                        <img
                                            src={previewUrl}
                                            alt="Preview"
                                            className="max-h-64 mx-auto rounded-lg shadow-sm"
                                        />
                                    ) : (
                                        <div className="space-y-2">
                                            <div className="mx-auto w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                                                <Upload className="w-6 h-6" />
                                            </div>
                                            <p className="text-slate-600 font-medium">Click or drag inputs here</p>
                                            <p className="text-slate-400 text-sm">Supports JPG, PNG, DICOM</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Text Input */}
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">
                                    Clinical Notes / Symptoms
                                </label>
                                <div className="relative">
                                    <FileText className="absolute top-3 left-3 w-5 h-5 text-slate-400" />
                                    <textarea
                                        value={text}
                                        onChange={(e) => setText(e.target.value)}
                                        placeholder="Enter patient symptoms, history, or specific questions..."
                                        className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[150px] resize-y"
                                    />
                                </div>
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
                                    <AlertCircle className="w-5 h-5" />
                                    {error}
                                </div>
                            )}

                            {/* Action Button */}
                            <button
                                onClick={handleAnalyze}
                                disabled={loading}
                                className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transition-all transform hover:-translate-y-0.5 ${loading
                                    ? 'bg-slate-400 cursor-not-allowed'
                                    : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-200'
                                    }`}
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                        Analyzing Case...
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center gap-2">
                                        <Brain className="w-5 h-5" />
                                        Run AI Analysis
                                    </div>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Results Section */}
                    <div className="space-y-6">
                        {result ? (
                            <>
                                {/* Status Card */}
                                <div className={`p-6 rounded-2xl border ${result.is_relevant ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                                    }`}>
                                    <div className="flex items-center gap-3 mb-2">
                                        {result.is_relevant ? (
                                            <CheckCircle className="w-6 h-6 text-green-600" />
                                        ) : (
                                            <AlertCircle className="w-6 h-6 text-red-600" />
                                        )}
                                        <h3 className={`text-lg font-bold ${result.is_relevant ? 'text-green-800' : 'text-red-800'
                                            }`}>
                                            {result.is_relevant ? 'Analysis Complete' : 'Input Rejected'}
                                        </h3>
                                    </div>
                                    <p className={result.is_relevant ? 'text-green-700' : 'text-red-700'}>
                                        {result.reason}
                                    </p>
                                </div>

                                {result.is_relevant && (
                                    <>
                                        {/* Charts */}
                                        {result.chart_data && (
                                            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-6">
                                                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                                                    <Activity className="w-5 h-5 text-blue-600" />
                                                    Visual Analytics
                                                </h3>
                                                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                                                    <div className="bg-slate-50 rounded-xl p-2 border border-slate-100">
                                                        {renderProbabilityChart(result.chart_data)}
                                                    </div>
                                                    <div className="bg-slate-50 rounded-xl p-2 border border-slate-100">
                                                        {renderRiskChart(result.chart_data)}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Markdown Report */}
                                        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
                                            <h3 className="text-xl font-bold mb-6 border-b pb-4">Clinical Assesment</h3>
                                            <div className="prose prose-blue max-w-none">
                                                {/* Simple markdown rendering - for production use a library like react-markdown */}
                                                <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">
                                                    {result.analysis}
                                                </div>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </>
                        ) : (
                            // Empty State
                            <div className="h-full bg-slate-100 rounded-2xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-400 p-12 min-h-[400px]">
                                <Activity className="w-16 h-16 mb-4 opacity-50" />
                                <p className="text-lg font-medium">Awaiting analysis results...</p>
                                <p className="text-sm">Upload a scan or enter symptoms to begin</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
