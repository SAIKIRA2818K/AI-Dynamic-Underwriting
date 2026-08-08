import React from 'react';
import { 
  CheckCircle2, XCircle, AlertTriangle, ShieldCheck, 
  MessageSquare, Building2, Lightbulb, FileText, Activity, 
  TrendingUp, Sparkles, AlertCircle, Globe, Loader2
} from 'lucide-react';
import { translateText } from '../services/api';
import type { AnalyzeResponseData } from '../services/api';
import { ScoreCard } from './ScoreCard';
import { BreakdownChart } from './BreakdownChart';
import { AILoadingAnimation } from './AILoadingAnimation';

interface ResultsDashboardProps {
  data: AnalyzeResponseData | null;
  isLoading: boolean;
  error: string | null;
  language: string;
  setLanguage: (lang: string) => void;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ data, isLoading, error, language, setLanguage }) => {
  const safeNum = (val: any) => (typeof val === 'number' && Number.isFinite(val) ? val : 'N/A');
  
  const [translatedTexts, setTranslatedTexts] = React.useState<any>(null);
  const [isTranslating, setIsTranslating] = React.useState(false);

  const [translationError, setTranslationError] = React.useState(false);

  React.useEffect(() => {
    if (!data) return;
    setTranslationError(false);
    if (language === 'en') {
      setTranslatedTexts(null);
      return;
    }

    let isMounted = true;
    const fetchTranslation = async () => {
      setIsTranslating(true);
      try {
        const payload = {
          target_language: language,
          texts: {
            customer_message: data.customer_message,
            recommendations: data.recommendations,
            reasoning: data.reasoning,
          }
        };
        const res = await translateText(payload);
        if (isMounted) {
          setTranslatedTexts(res);
        }
      } catch (err) {
        console.error('Translation failed', err);
        if (isMounted) {
          setTranslationError(true);
          setTranslatedTexts(null);
        }
      } finally {
        if (isMounted) setIsTranslating(false);
      }
    };
    fetchTranslation();
    return () => { isMounted = false; };
  }, [language, data]);


  const displayTexts = translatedTexts || (data ? {
    customer_message: data.customer_message,
    recommendations: data.recommendations,
    reasoning: data.reasoning,
  } : null);
  if (isLoading) {
    return <AILoadingAnimation />;
  }

  if (error) {
    return (
      <div className="bg-rose-50/60 rounded-2xl border border-rose-200 p-8 shadow-sm h-full flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-rose-100 text-rose-600 rounded-full mb-3">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-rose-950">Underwriting Assessment Failed</h3>
        <p className="text-xs text-rose-700 max-w-md mt-1 mb-4">{error}</p>
        <p className="text-xs text-slate-500">
          Please check that your FastAPI backend is running on <code className="bg-slate-200 px-1 py-0.5 rounded">http://localhost:8000</code>.
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm h-full flex flex-col items-center justify-center text-center space-y-4">
        <div className="p-4 bg-blue-50 text-blue-600 rounded-full">
          <Sparkles className="w-10 h-10" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-800">Ready for Underwriting Evaluation</h3>
          <p className="text-xs text-slate-500 max-w-md mt-1">
            Fill in the applicant details on the left panel or click one of the quick presets, then press <strong>Analyze Application</strong> to run the multi-agent AI pipeline.
          </p>
        </div>
      </div>
    );
  }

  if (data.risk_score == null || !Number.isFinite(data.risk_score) || !data.decision) {
    return (
      <div className="bg-rose-50/60 rounded-2xl border border-rose-200 p-8 shadow-sm h-full flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-rose-100 text-rose-600 rounded-full mb-3">
          <AlertCircle className="w-8 h-8" />
        </div>
        <h3 className="text-base font-bold text-rose-950">Underwriting Assessment Failed</h3>
        <p className="text-xs text-rose-700 max-w-md mt-1 mb-4">Underwriting response was incomplete. Please try again.</p>
      </div>
    );
  }

  // Helper for Decision Badge
  const getDecisionBadge = () => {
    switch (data.decision) {
      case 'Approve':
        return {
          bg: 'bg-emerald-500 text-white shadow-emerald-500/30',
          icon: CheckCircle2,
          text: 'APPLICATION APPROVED',
          bannerBg: 'bg-emerald-50 border-emerald-200 text-emerald-950',
        };
      case 'Manual Review':
        return {
          bg: 'bg-amber-500 text-white shadow-amber-500/30',
          icon: AlertTriangle,
          text: 'MANUAL REVIEW REQUIRED',
          bannerBg: 'bg-amber-50 border-amber-200 text-amber-950',
        };
      case 'Reject':
      default:
        return {
          bg: 'bg-rose-600 text-white shadow-rose-600/30',
          icon: XCircle,
          text: 'APPLICATION REJECTED',
          bannerBg: 'bg-rose-50 border-rose-200 text-rose-950',
        };
    }
  };

  const decisionBadge = getDecisionBadge();
  const DecisionIcon = decisionBadge.icon;

  return (
    <div className="space-y-6">
      {/* DECISION AREA */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className={`p-6 border-b ${decisionBadge.bannerBg} flex flex-col md:flex-row md:items-center justify-between gap-4`}>
          <div>
            <span className="text-xs font-bold uppercase tracking-widest opacity-80 block mb-1">
              Underwriting Decision
            </span>
            <div className="flex items-center gap-3">
              <DecisionIcon className="w-6 h-6" />
              <h2 className="text-2xl font-extrabold tracking-tight">{decisionBadge.text}</h2>
            </div>
          </div>
          <div className="flex items-center gap-4 bg-white/50 px-4 py-2 rounded-md border border-black/5">
            <div className="text-center">
              <span className="block text-[10px] font-bold uppercase tracking-wider opacity-70">Confidence</span>
              <span className="text-lg font-bold">{safeNum(data.confidence)}%</span>
            </div>
          </div>
        </div>
        
        {/* Risk Assessment (Metric Cards without excessive decoration) */}
        <div className="p-6">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 mb-4">Risk Assessment</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="flex flex-col border-l-2 border-slate-200 pl-4">
              <span className="text-xs text-slate-500 font-medium mb-1">Financial Risk</span>
              <span className="text-xl font-bold text-slate-900">{safeNum(data.risk_score)} <span className="text-sm font-normal text-slate-500">/ 100</span></span>
              <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">{data.risk_label || 'Unknown'}</span>
            </div>
            <div className="flex flex-col border-l-2 border-slate-200 pl-4">
              <span className="text-xs text-slate-500 font-medium mb-1">Alternative Trust</span>
              <span className="text-xl font-bold text-slate-900">{safeNum(data.alternative_score)} <span className="text-sm font-normal text-slate-500">/ 100</span></span>
              <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">Non-traditional data</span>
            </div>
            <div className="flex flex-col border-l-2 border-slate-200 pl-4">
              <span className="text-xs text-slate-500 font-medium mb-1">Fraud Probability</span>
              <span className="text-xl font-bold text-slate-900">{safeNum(data.fraud_probability)}%</span>
              <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider">Anomaly Risk</span>
            </div>
          </div>
        </div>
      </div>

      {/* ALTERNATIVE DATA ASSESSMENT (Horizontal Visualization) */}
      {data.alternative_breakdown && data.alternative_breakdown.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 mb-4 border-b border-slate-100 pb-2">Alternative Data Assessment</h3>
          <div className="space-y-4 mt-4">
            {data.alternative_breakdown.map((item, idx) => {
              const percentage = (item && item.max_possible_impact > 0) 
                ? Math.round((item.score_impact / item.max_possible_impact) * 100) 
                : 0;
              const clamped = Math.max(0, Math.min(percentage || 0, 100));
              
              return (
                <div key={idx} className="flex items-center gap-4">
                  <div className="w-1/3 text-xs font-medium text-slate-700 truncate">{item?.feature || 'Unknown'}</div>
                  <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div 
                      className="bg-slate-700 h-full rounded-full" 
                      style={{ width: `${clamped}%` }}
                    />
                  </div>
                  <div className="w-12 text-right text-xs font-mono text-slate-500">{clamped}%</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* DECISION EXPLANATION */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col relative">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-4">
            <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900">Decision Explanation</h3>
            
            <div className="flex items-center gap-2">

              <div className="flex items-center gap-1.5 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-600 bg-slate-50 border border-slate-200 rounded">
                <Globe className="w-3.5 h-3.5" />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-transparent outline-none cursor-pointer"
                >
                  <option value="en">English</option>
                  <option value="te">తెలుగు</option>
                  <option value="hi">हिन्दी</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="flex-1 text-sm text-slate-700 leading-relaxed space-y-4 relative">
            {isTranslating && (
              <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center rounded">
                <Loader2 className="w-5 h-5 text-blue-500 animate-spin mb-2" />
                <span className="text-xs text-blue-700 font-medium">Translating explanation...</span>
              </div>
            )}
            {translationError && (
              <div className="mb-2 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded inline-block">
                Translation unavailable — showing English
              </div>
            )}
            <p>{displayTexts?.customer_message || "AI explanation is temporarily unavailable."}</p>
          </div>
        </div>

        {/* CREDIT ASSESSMENT SUMMARY (Memo Style) */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col font-serif">
          <div className="border-b-2 border-black pb-2 mb-4">
            <h3 className="font-bold text-sm uppercase tracking-widest text-black">Credit Assessment Summary</h3>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1 font-sans">Internal Underwriting Memo</p>
          </div>
          <div className="flex-1 text-sm text-black leading-relaxed relative">
            <p>{data.bank_summary || "Summary temporarily unavailable."}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* APPLICANT RECOMMENDATIONS */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 relative">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 mb-4 border-b border-slate-100 pb-2">Applicant Recommendations</h3>
          {isTranslating && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded">
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            </div>
          )}
          <ol className="list-decimal list-inside space-y-3">
            {(displayTexts?.recommendations || []).map((rec: string, idx: number) => (
              <li key={idx} className="text-sm text-slate-700 pl-2">{rec}</li>
            ))}
            {!(displayTexts?.recommendations?.length > 0) && (
              <li className="text-sm text-slate-500 italic pl-2">No recommendations available.</li>
            )}
          </ol>
        </div>

        {/* DECISION REASONING */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 relative">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 mb-4 border-b border-slate-100 pb-2">Decision Logic & Reasoning</h3>
          {isTranslating && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center rounded">
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            </div>
          )}
          <ul className="space-y-3">
            {(displayTexts?.reasoning || []).map((reason: string, idx: number) => (
              <li key={idx} className="flex gap-3 text-sm text-slate-700">
                <span className="text-slate-400 mt-0.5">•</span>
                <span>{reason}</span>
              </li>
            ))}
            {!(displayTexts?.reasoning?.length > 0) && (
              <li className="flex gap-3 text-sm text-slate-500 italic">
                <span className="text-slate-400 mt-0.5">•</span>
                <span>No reasoning available.</span>
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* AI PIPELINE VISIBILITY */}
      <details className="bg-slate-50 rounded-xl border border-slate-200 shadow-sm group">
        <summary className="p-4 text-xs font-semibold uppercase tracking-widest text-slate-600 cursor-pointer flex justify-between items-center list-none outline-none">
          <span>View Decision Pipeline</span>
          <span className="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
        </summary>
        <div className="p-6 pt-0 border-t border-slate-200 mt-2">
          <div className="flex flex-col md:flex-row items-center justify-between gap-2 text-xs font-medium text-slate-500 uppercase tracking-wider text-center mt-4">
            <div className="bg-white border border-slate-200 px-3 py-2 rounded shadow-sm w-full md:w-auto">Risk Assessment</div>
            <span className="text-slate-300 md:-rotate-90">↓</span>
            <div className="bg-white border border-slate-200 px-3 py-2 rounded shadow-sm w-full md:w-auto">Alternative Data</div>
            <span className="text-slate-300 md:-rotate-90">↓</span>
            <div className="bg-white border border-slate-200 px-3 py-2 rounded shadow-sm w-full md:w-auto">Fraud Detection</div>
            <span className="text-slate-300 md:-rotate-90">↓</span>
            <div className="bg-white border border-slate-200 px-3 py-2 rounded shadow-sm w-full md:w-auto">Decision Engine</div>
            <span className="text-slate-300 md:-rotate-90">↓</span>
            <div className="bg-white border border-slate-200 px-3 py-2 rounded shadow-sm w-full md:w-auto">Generative Explanation</div>
          </div>
        </div>
      </details>
    </div>
  );
};
