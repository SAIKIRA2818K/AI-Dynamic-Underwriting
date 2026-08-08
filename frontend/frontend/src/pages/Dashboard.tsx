import React, { useState } from 'react';
import { Header } from '../components/Header';
import { ApplicationForm } from '../components/ApplicationForm';
import { ResultsDashboard } from '../components/ResultsDashboard';
import { analyzeApplication } from '../services/api';
import type { AnalyzePayload, AnalyzeResponseData } from '../services/api';
import { ErrorBoundary } from '../components/ErrorBoundary';

export const Dashboard: React.FC = () => {
  const [result, setResult] = useState<AnalyzeResponseData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<string>('en');

  const handleAnalyze = async (payload: AnalyzePayload) => {
    setIsLoading(true);
    setError(null);
    const start = Date.now();
    try {
      const data = await analyzeApplication(payload);
      const elapsed = Date.now() - start;
      if (elapsed < 3500) {
        await new Promise(resolve => setTimeout(resolve, 3500 - elapsed));
      }
      setResult(data);
    } catch (err: any) {
      console.error('Error analyzing application:', err);
      const elapsed = Date.now() - start;
      if (elapsed < 3500) {
        await new Promise(resolve => setTimeout(resolve, 3500 - elapsed));
      }
      let errMsg = 'Unable to connect to the underwriting service.';
      if (err.response) {
        if (err.response.status === 500) {
          errMsg = 'Unable to complete underwriting analysis. Please try again.';
        } else if (err.response.status === 400 || err.response.status === 422) {
          errMsg = err.response.data?.detail || 'Invalid application data provided.';
          if (Array.isArray(errMsg)) {
            errMsg = errMsg.map(e => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
          }
        }
      }
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Header language={language} setLanguage={setLanguage} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* LEFT PANEL: Loan Application Form */}
          <div className="lg:col-span-5 lg:sticky lg:top-20">
            <ApplicationForm onSubmit={handleAnalyze} isLoading={isLoading} />
          </div>

          {/* RIGHT PANEL: Results Dashboard */}
          <div className="lg:col-span-7">
            <ErrorBoundary>
              <ResultsDashboard data={result} isLoading={isLoading} error={error} language={language} setLanguage={setLanguage} />
            </ErrorBoundary>
          </div>
        </div>
      </main>
    </div>
  );
};
