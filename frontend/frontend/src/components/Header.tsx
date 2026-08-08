import React, { useEffect, useState } from 'react';
import { Activity, Menu, Globe } from 'lucide-react';
import { checkHealth } from '../services/api';

interface HeaderProps {
  language: string;
  setLanguage: (lang: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ language, setLanguage }) => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const verifyHealth = async () => {
      try {
        const data = await checkHealth();
        setIsHealthy(data.status === 'healthy');
      } catch {
        setIsHealthy(false);
      }
    };
    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-white border-b border-slate-200 text-slate-900 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Navigation */}
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center text-blue-700">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M7 14l3-3 2.5 2.5 4.5-4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M17 9h-3m3 0v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div className="flex flex-col">
              <h1 className="font-extrabold text-xl tracking-tight text-slate-900 leading-tight">RiskLens</h1>
              <span className="text-[10px] font-medium text-slate-500 uppercase tracking-widest hidden sm:block leading-tight">
                AI-Powered Underwriting Platform
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-sm font-semibold text-blue-700 border-b-2 border-blue-700 py-5">
              Applications
            </a>
            <a href="#" className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors py-5">
              Analytics
            </a>
            <a href="#" className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors py-5">
              Reports
            </a>
          </nav>
        </div>

        {/* Status & Language */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 border border-slate-200 rounded-md bg-slate-50">
            <Globe className="w-4 h-4 text-slate-500" />
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-700 outline-none cursor-pointer"
            >
              <option value="en">English</option>
              <option value="te">తెలుగు</option>
              <option value="hi">हिन्दी</option>
            </select>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium border border-slate-200 rounded-md bg-slate-50 hidden sm:flex">
            {isHealthy === null ? (
              <span className="text-slate-500">System Checking...</span>
            ) : isHealthy ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-slate-700">System Online</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                <span className="text-slate-700">System Offline</span>
              </>
            )}
          </div>
          
          <button className="md:hidden text-slate-600 hover:text-slate-900">
            <Menu className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};
