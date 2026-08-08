import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface ScoreCardProps {
  title: string;
  score: number;
  subtitle: string;
  icon: LucideIcon;
  variant: 'blue' | 'indigo' | 'rose' | 'emerald' | 'amber';
  max?: number;
  unit?: string;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({
  title,
  score,
  subtitle,
  icon: Icon,
  variant,
  max = 100,
  unit = '',
}) => {
  const percentage = Math.min(Math.max((score / max) * 100, 0), 100);

  const getVariantStyles = () => {
    switch (variant) {
      case 'emerald':
        return {
          cardBg: 'bg-emerald-50/50 border-emerald-100',
          iconBg: 'bg-emerald-600 text-white',
          text: 'text-emerald-950',
          scoreText: 'text-emerald-700',
          bar: 'bg-emerald-500',
          ring: 'text-emerald-500',
        };
      case 'amber':
        return {
          cardBg: 'bg-amber-50/50 border-amber-100',
          iconBg: 'bg-amber-600 text-white',
          text: 'text-amber-950',
          scoreText: 'text-amber-700',
          bar: 'bg-amber-500',
          ring: 'text-amber-500',
        };
      case 'rose':
        return {
          cardBg: 'bg-rose-50/50 border-rose-100',
          iconBg: 'bg-rose-600 text-white',
          text: 'text-rose-950',
          scoreText: 'text-rose-700',
          bar: 'bg-rose-500',
          ring: 'text-rose-500',
        };
      case 'indigo':
        return {
          cardBg: 'bg-indigo-50/50 border-indigo-100',
          iconBg: 'bg-indigo-600 text-white',
          text: 'text-indigo-950',
          scoreText: 'text-indigo-700',
          bar: 'bg-indigo-600',
          ring: 'text-indigo-600',
        };
      case 'blue':
      default:
        return {
          cardBg: 'bg-blue-50/50 border-blue-100',
          iconBg: 'bg-blue-600 text-white',
          text: 'text-blue-950',
          scoreText: 'text-blue-700',
          bar: 'bg-blue-600',
          ring: 'text-blue-600',
        };
    }
  };

  const styles = getVariantStyles();

  // SVG Circular Gauge calculation
  const radius = 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className={`p-5 rounded-2xl border ${styles.cardBg} shadow-sm transition-all relative overflow-hidden`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className={`p-1.5 rounded-lg ${styles.iconBg}`}>
              <Icon className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-600">{title}</h3>
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-[140px]">{subtitle}</p>
        </div>

        {/* Circular Progress Indicator */}
        <div className="relative w-16 h-16 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="32"
              cy="32"
              r={radius}
              className="text-slate-200 stroke-current"
              strokeWidth="5"
              fill="transparent"
            />
            <circle
              cx="32"
              cy="32"
              r={radius}
              className={`${styles.ring} stroke-current transition-all duration-1000 ease-out`}
              strokeWidth="5"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
            />
          </svg>
          <span className={`absolute font-black text-sm ${styles.scoreText}`}>
            {Math.round(score)}{unit}
          </span>
        </div>
      </div>

      {/* Linear progress bar fallback / accent */}
      <div className="w-full bg-slate-200/80 h-1.5 rounded-full mt-4 overflow-hidden">
        <div
          className={`h-full ${styles.bar} transition-all duration-1000 ease-out rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
