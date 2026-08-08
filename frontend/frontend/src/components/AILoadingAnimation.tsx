import React, { useState, useEffect } from 'react';
import { CheckCircle2, Loader2 } from 'lucide-react';

const steps = [
  { id: 1, name: 'RiskLens AI', desc: 'Analyzing Financial Risk...' },
  { id: 2, name: 'TrustLens AI', desc: 'Evaluating Alternative Data...' },
  { id: 3, name: 'FraudShield AI', desc: 'Checking Fraud Probability...' },
  { id: 4, name: 'DecisionHub AI', desc: 'Generating Final Decision...' },
  { id: 5, name: 'Insight AI', desc: 'Generating Customer Explanation...' },
];

export const AILoadingAnimation: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [allDone, setAllDone] = useState(false);

  useEffect(() => {
    // 5 steps over ~3.5 seconds = 700ms per step
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev < steps.length - 1) return prev + 1;
        setAllDone(true);
        clearInterval(interval);
        return prev;
      });
    }, 700);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm h-full flex flex-col items-center justify-center space-y-6">
      <h3 className="text-xl font-bold text-slate-800 mb-2">AI Processing Pipeline</h3>
      <div className="w-full max-w-md space-y-4">
        {steps.map((step, index) => {
          const isCompleted = index < currentStepIndex || allDone;
          const isActive = index === currentStepIndex && !allDone;

          return (
            <div 
              key={step.id} 
              className={`flex flex-col p-4 rounded-xl border transition-all duration-500 ${
                isCompleted ? 'bg-emerald-50/50 border-emerald-200' :
                isActive ? 'bg-blue-50/50 border-blue-200 shadow-sm transform scale-[1.02]' :
                'bg-slate-50 border-slate-100 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className={`text-xs font-bold uppercase tracking-wider ${
                    isCompleted ? 'text-emerald-700' :
                    isActive ? 'text-blue-700' :
                    'text-slate-500'
                  }`}>
                    Step {step.id}: {step.name}
                  </span>
                  <p className={`text-sm mt-1 ${
                    isCompleted ? 'text-emerald-900' :
                    isActive ? 'text-blue-900 font-medium' :
                    'text-slate-600'
                  }`}>
                    {step.desc}
                  </p>
                </div>
                <div className="flex-shrink-0 ml-4 flex flex-col items-center justify-center min-w-[70px]">
                  {isCompleted ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 mb-1" />
                      <span className="text-[10px] text-emerald-600 font-bold whitespace-nowrap">✓ Completed</span>
                    </>
                  ) : isActive ? (
                    <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                  ) : (
                    <div className="w-6 h-6 rounded-full border-2 border-slate-200" />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
