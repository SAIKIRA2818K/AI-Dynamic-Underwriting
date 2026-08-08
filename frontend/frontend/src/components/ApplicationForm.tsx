import React, { useState, useEffect } from 'react';
import { User, DollarSign, Sparkles, Layers, Activity, ArrowRight } from 'lucide-react';
import type { AnalyzePayload } from '../services/api';

interface ApplicationFormProps {
  onSubmit: (payload: AnalyzePayload) => void;
  isLoading: boolean;
}

interface ValidationErrors {
  personAge?: string;
  personIncome?: string;
  loanAmnt?: string;
  empLength?: string;
  loanIntRate?: string;
  credHistLength?: string;
  empStabilityYears?: string;
  certificationsCount?: string;
}

export const ApplicationForm: React.FC<ApplicationFormProps> = ({ onSubmit, isLoading }) => {
  // Use string states to allow clearing inputs and smooth typing
  const [personAge, setPersonAge] = useState<string>('32');
  const [personIncome, setPersonIncome] = useState<string>('75000');
  const [loanAmnt, setLoanAmnt] = useState<string>('15000');
  const [loanIntent, setLoanIntent] = useState<string>('PERSONAL');
  const [homeOwnership, setHomeOwnership] = useState<string>('MORTGAGE');
  const [loanGrade, setLoanGrade] = useState<string>('B');
  const [empLength, setEmpLength] = useState<string>('5');
  const [loanIntRate, setLoanIntRate] = useState<string>('10.5');
  const [credHistLength, setCredHistLength] = useState<string>('8');
  const [defaultOnFile, setDefaultOnFile] = useState<string>('N');

  // Alternative Data State
  const [empStabilityYears, setEmpStabilityYears] = useState<string>('5');
  const [linkedinVerified, setLinkedinVerified] = useState<boolean>(true);
  const [certificationsCount, setCertificationsCount] = useState<string>('2');
  const [utilityConsistency, setUtilityConsistency] = useState<number>(92);
  const [digitalDiscipline, setDigitalDiscipline] = useState<number>(85);

  // Validation errors state
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isValid, setIsValid] = useState<boolean>(true);

  // Auto calculated Loan Percent Income
  const numIncome = parseFloat(personIncome) || 0;
  const numLoanAmnt = parseFloat(loanAmnt) || 0;
  const calculatedLoanPercentIncome = numIncome > 0 ? parseFloat((numLoanAmnt / numIncome).toFixed(2)) : 0;

  // Run validation on value changes
  useEffect(() => {
    const newErrors: ValidationErrors = {};

    // Age validation
    const age = parseFloat(personAge);
    if (personAge === '') {
      newErrors.personAge = 'Age is required';
    } else if (isNaN(age) || age < 18 || age > 100) {
      newErrors.personAge = 'Age must be between 18 and 100';
    }

    // Income validation
    const income = parseFloat(personIncome);
    if (personIncome === '') {
      newErrors.personIncome = 'Annual income is required';
    } else if (isNaN(income) || income <= 0) {
      newErrors.personIncome = 'Income must be greater than 0';
    }

    // Loan Amount validation
    const amount = parseFloat(loanAmnt);
    if (loanAmnt === '') {
      newErrors.loanAmnt = 'Loan amount is required';
    } else if (isNaN(amount) || amount <= 0) {
      newErrors.loanAmnt = 'Loan amount must be greater than 0';
    }

    // Employment Length validation
    const el = parseFloat(empLength);
    if (empLength === '') {
      newErrors.empLength = 'Employment length is required';
    } else if (isNaN(el) || el < 0 || el > 60) {
      newErrors.empLength = 'Must be between 0 and 60 years';
    }

    // Interest Rate validation
    const rate = parseFloat(loanIntRate);
    if (loanIntRate === '') {
      newErrors.loanIntRate = 'Interest rate is required';
    } else if (isNaN(rate) || rate < 0 || rate > 100) {
      newErrors.loanIntRate = 'Rate must be between 0% and 100%';
    }

    // Credit History length validation
    const hist = parseFloat(credHistLength);
    if (credHistLength === '') {
      newErrors.credHistLength = 'Credit history is required';
    } else if (isNaN(hist) || hist < 0) {
      newErrors.credHistLength = 'Must be 0 or greater';
    }

    // Employment Stability validation
    const stability = parseFloat(empStabilityYears);
    if (empStabilityYears === '') {
      newErrors.empStabilityYears = 'Job tenure is required';
    } else if (isNaN(stability) || stability < 0) {
      newErrors.empStabilityYears = 'Must be 0 or greater';
    }

    // Certifications validation
    const certs = parseFloat(certificationsCount);
    if (certificationsCount === '') {
      newErrors.certificationsCount = 'Certifications is required';
    } else if (isNaN(certs) || certs < 0) {
      newErrors.certificationsCount = 'Must be 0 or greater';
    }

    setErrors(newErrors);
    setIsValid(Object.keys(newErrors).length === 0);
  }, [
    personAge, personIncome, loanAmnt, empLength, 
    loanIntRate, credHistLength, empStabilityYears, certificationsCount
  ]);

  // Preset Loaders setting clean string representations
  const loadPreset = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const type = e.target.value;
    if (type === 'salaried') {
      setPersonAge('34');
      setPersonIncome('95000');
      setLoanAmnt('18000');
      setLoanIntent('PERSONAL');
      setHomeOwnership('MORTGAGE');
      setLoanGrade('A');
      setEmpLength('6');
      setLoanIntRate('7.5');
      setCredHistLength('10');
      setDefaultOnFile('N');
      setEmpStabilityYears('6');
      setLinkedinVerified(true);
      setCertificationsCount('3');
      setUtilityConsistency(96);
      setDigitalDiscipline(90);
    } else if (type === 'self_employed') {
      setPersonAge('42');
      setPersonIncome('120000');
      setLoanAmnt('50000');
      setLoanIntent('VENTURE');
      setHomeOwnership('OWN');
      setLoanGrade('B');
      setEmpLength('10');
      setLoanIntRate('9.2');
      setCredHistLength('15');
      setDefaultOnFile('N');
      setEmpStabilityYears('10');
      setLinkedinVerified(true);
      setCertificationsCount('1');
      setUtilityConsistency(85);
      setDigitalDiscipline(88);
    } else if (type === 'first_time') {
      setPersonAge('22');
      setPersonIncome('55000');
      setLoanAmnt('10000');
      setLoanIntent('EDUCATION');
      setHomeOwnership('RENT');
      setLoanGrade('C');
      setEmpLength('1');
      setLoanIntRate('12.5');
      setCredHistLength('1');
      setDefaultOnFile('N');
      setEmpStabilityYears('1');
      setLinkedinVerified(true);
      setCertificationsCount('0');
      setUtilityConsistency(80);
      setDigitalDiscipline(75);
    } else if (type === 'gig_worker') {
      setPersonAge('28');
      setPersonIncome('45000');
      setLoanAmnt('8000');
      setLoanIntent('PERSONAL');
      setHomeOwnership('RENT');
      setLoanGrade('D');
      setEmpLength('2');
      setLoanIntRate('14.0');
      setCredHistLength('4');
      setDefaultOnFile('N');
      setEmpStabilityYears('2');
      setLinkedinVerified(false);
      setCertificationsCount('1');
      setUtilityConsistency(70);
      setDigitalDiscipline(65);
    } else if (type === 'high_risk') {
      setPersonAge('30');
      setPersonIncome('38000');
      setLoanAmnt('15000');
      setLoanIntent('DEBTCONSOLIDATION');
      setHomeOwnership('RENT');
      setLoanGrade('E');
      setEmpLength('1');
      setLoanIntRate('18.5');
      setCredHistLength('3');
      setDefaultOnFile('Y');
      setEmpStabilityYears('0.5');
      setLinkedinVerified(false);
      setCertificationsCount('0');
      setUtilityConsistency(45);
      setDigitalDiscipline(35);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;

    const payload: AnalyzePayload = {
      traditional_data: {
        person_age: Number(personAge),
        person_income: Number(personIncome),
        person_home_ownership: homeOwnership,
        person_emp_length: Number(empLength),
        loan_intent: loanIntent,
        loan_grade: loanGrade,
        loan_amnt: Number(loanAmnt),
        loan_int_rate: Number(loanIntRate),
        loan_percent_income: calculatedLoanPercentIncome,
        cb_person_default_on_file: defaultOnFile,
        cb_person_cred_hist_length: Number(credHistLength),
      },
      alternative_data: {
        employment_stability_years: Number(empStabilityYears),
        linkedin_verified: linkedinVerified,
        professional_certifications_count: Number(certificationsCount),
        utility_bill_consistency_score: Number(utilityConsistency),
        digital_discipline_score: Number(digitalDiscipline),
      },
    };

    onSubmit(payload);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col h-full">
      {/* Form Header */}
      <div className="bg-white text-slate-900 p-5 border-b border-slate-200">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-bold text-lg tracking-tight">Loan Application Intake</h2>
          <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-mono border border-slate-200 uppercase tracking-widest">
            Form #2026-X
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Enter applicant metrics for automated underwriting and risk evaluation.
        </p>

        {/* Presets Bar */}
        <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-2">
          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider whitespace-nowrap">Load Profile:</span>
          <div className="flex-1 ml-4">
            <select
              onChange={loadPreset}
              defaultValue=""
              className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-md px-3 py-1.5 focus:ring-1 focus:ring-slate-400 focus:outline-none"
            >
              <option value="" disabled>Select Sample Applicant</option>
              <option value="salaried">Salaried Professional</option>
              <option value="self_employed">Self-Employed Business Owner</option>
              <option value="first_time">First-Time Borrower</option>
              <option value="gig_worker">Gig Economy Worker</option>
              <option value="high_risk">High-Risk Applicant</option>
            </select>
          </div>
        </div>
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit} className="p-5 overflow-y-auto space-y-8 flex-1">
        
        {/* SECTION 1: APPLICANT INFORMATION */}
        <div className="space-y-4">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 border-b border-slate-200 pb-2">
            1. Applicant Information
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Age */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Applicant Age (Years)</label>
              <input type="text" value={personAge} onChange={(e) => setPersonAge(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.personAge ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.personAge && <p className="text-[10px] text-rose-600 mt-1">{errors.personAge}</p>}
            </div>
            {/* Income */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Annual Income ($)</label>
              <input type="text" value={personIncome} onChange={(e) => setPersonIncome(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.personIncome ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.personIncome && <p className="text-[10px] text-rose-600 mt-1">{errors.personIncome}</p>}
            </div>
            {/* Home Ownership */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-600 mb-1">Home Ownership</label>
              <select value={homeOwnership} onChange={(e) => setHomeOwnership(e.target.value)}
                className="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all">
                <option value="RENT">Rent</option>
                <option value="MORTGAGE">Mortgage</option>
                <option value="OWN">Own Outright</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 2: LOAN INFORMATION */}
        <div className="space-y-4">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 border-b border-slate-200 pb-2">
            2. Loan Information
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Loan Amount */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Loan Amount Requested ($)</label>
              <input type="text" value={loanAmnt} onChange={(e) => setLoanAmnt(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.loanAmnt ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.loanAmnt && <p className="text-[10px] text-rose-600 mt-1">{errors.loanAmnt}</p>}
            </div>
            {/* Loan Intent */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Loan Purpose / Intent</label>
              <select value={loanIntent} onChange={(e) => setLoanIntent(e.target.value)}
                className="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all">
                <option value="PERSONAL">Personal Loan</option>
                <option value="EDUCATION">Education</option>
                <option value="MEDICAL">Medical Expense</option>
                <option value="VENTURE">Business / Venture</option>
                <option value="DEBTCONSOLIDATION">Debt Consolidation</option>
                <option value="HOMEIMPROVEMENT">Home Improvement</option>
              </select>
            </div>
          </div>
          <div className="bg-slate-50 p-3 rounded-md flex items-center justify-between text-xs text-slate-600 border border-slate-200">
            <span>Debt-to-Income Ratio:</span>
            <span className="font-semibold text-slate-900">{(calculatedLoanPercentIncome * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* SECTION 3: CREDIT PROFILE */}
        <div className="space-y-4">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 border-b border-slate-200 pb-2">
            3. Credit Profile
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Loan Grade */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Credit Rating / Grade</label>
              <select value={loanGrade} onChange={(e) => setLoanGrade(e.target.value)}
                className="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all font-medium">
                <option value="A">Grade A (Prime)</option>
                <option value="B">Grade B (Good)</option>
                <option value="C">Grade C (Fair)</option>
                <option value="D">Grade D (Moderate Risk)</option>
                <option value="E">Grade E (Subprime)</option>
                <option value="F">Grade F (High Risk)</option>
                <option value="G">Grade G (Deep Subprime)</option>
              </select>
            </div>
            {/* Employment Length */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Employment History (Years)</label>
              <input type="text" value={empLength} onChange={(e) => setEmpLength(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.empLength ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.empLength && <p className="text-[10px] text-rose-600 mt-1">{errors.empLength}</p>}
            </div>
            {/* Interest Rate */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Target Interest Rate (%)</label>
              <input type="text" value={loanIntRate} onChange={(e) => setLoanIntRate(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.loanIntRate ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.loanIntRate && <p className="text-[10px] text-rose-600 mt-1">{errors.loanIntRate}</p>}
            </div>
            {/* Credit History Length */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Credit History (Years)</label>
              <input type="text" value={credHistLength} onChange={(e) => setCredHistLength(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.credHistLength ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.credHistLength && <p className="text-[10px] text-rose-600 mt-1">{errors.credHistLength}</p>}
            </div>
            {/* Default on File */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-600 mb-1">Prior Default on Record</label>
              <select value={defaultOnFile} onChange={(e) => setDefaultOnFile(e.target.value)}
                className="w-full px-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all font-medium">
                <option value="N">No Prior Default</option>
                <option value="Y">Yes - Prior Default Recorded</option>
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 4: ALTERNATIVE SIGNALS */}
        <div className="space-y-4">
          <h3 className="font-semibold text-xs uppercase tracking-widest text-slate-900 border-b border-slate-200 pb-2">
            4. Alternative Signals
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Employment Stability */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Position Tenure (Years)</label>
              <input type="text" value={empStabilityYears} onChange={(e) => setEmpStabilityYears(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.empStabilityYears ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.empStabilityYears && <p className="text-[10px] text-rose-600 mt-1">{errors.empStabilityYears}</p>}
            </div>
            {/* Certifications */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Professional Certifications</label>
              <input type="text" value={certificationsCount} onChange={(e) => setCertificationsCount(e.target.value)}
                className={`w-full px-3 py-1.5 text-sm bg-slate-50 border rounded-md focus:ring-1 focus:ring-slate-400 focus:bg-white focus:outline-none transition-all ${errors.certificationsCount ? 'border-rose-300' : 'border-slate-200'}`} />
              {errors.certificationsCount && <p className="text-[10px] text-rose-600 mt-1">{errors.certificationsCount}</p>}
            </div>
          </div>
          
          <div className="flex items-center justify-between bg-slate-50 border border-slate-200 p-3 rounded-md">
            <div>
              <h4 className="text-xs font-semibold text-slate-700">LinkedIn Identity Verification</h4>
              <p className="text-[10px] text-slate-500">Confirms professional social footprint</p>
            </div>
            <button type="button" onClick={() => setLinkedinVerified(!linkedinVerified)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${linkedinVerified ? 'bg-slate-800' : 'bg-slate-300'}`}>
              <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${linkedinVerified ? 'translate-x-4' : 'translate-x-1'}`} />
            </button>
          </div>

          <div className="space-y-4 pt-2">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-600">Utility Payment Punctuality</label>
                <span className="text-xs font-mono font-medium text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">{utilityConsistency}/100</span>
              </div>
              <input type="range" min="0" max="100" value={utilityConsistency} onChange={(e) => setUtilityConsistency(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-800" />
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-slate-600">Digital Financial Discipline</label>
                <span className="text-xs font-mono font-medium text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">{digitalDiscipline}/100</span>
              </div>
              <input type="range" min="0" max="100" value={digitalDiscipline} onChange={(e) => setDigitalDiscipline(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-800" />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4 mt-8 border-t border-slate-200">
          <button
            type="submit"
            disabled={isLoading || !isValid}
            className="w-full py-2.5 px-4 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-md transition-colors flex items-center justify-center gap-2 group disabled:opacity-50 disabled:bg-slate-400 disabled:cursor-not-allowed text-sm"
          >
            {isLoading ? (
              <span>Analyzing Application...</span>
            ) : (
              <span>Analyze Application</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
