import React from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';
import type { AlternativeBreakdownItem } from '../services/api';

interface BreakdownChartProps {
  data: AlternativeBreakdownItem[];
}

export const BreakdownChart: React.FC<BreakdownChartProps> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const chartData = data.map((item) => ({
    name: item.feature.replace('Professional ', '').replace('Utility Bill ', ''),
    score: item.score_impact,
    max: item.max_possible_impact,
    value: item.value,
    increaseReason: item.trust_increase_reason,
    decreaseReason: item.trust_decrease_reason,
  }));

  const colors = ['#2563eb', '#4f46e5', '#7c3aed', '#059669', '#d97706'];

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-bold text-sm text-slate-800 uppercase tracking-wider">
            Alternative Trust Feature Breakdown
          </h3>
          <p className="text-xs text-slate-500">
            Weighted point contribution towards the 100-point Alternative Trust Score
          </p>
        </div>
        <span className="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full border border-indigo-100">
          5 Signal Streams
        </span>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 11, fill: '#64748b' }} 
              interval={0}
              angle={-10}
              textAnchor="end"
            />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} domain={[0, 30]} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const dataItem = payload[0].payload;
                  return (
                    <div className="bg-slate-900 text-white p-3 rounded-xl shadow-xl text-xs max-w-xs border border-slate-700">
                      <p className="font-bold text-blue-400 mb-1">{dataItem.name}</p>
                      <p className="text-slate-300 font-medium">Input Value: {dataItem.value}</p>
                      <p className="text-emerald-400 font-bold mt-1">
                        Impact: +{dataItem.score} pts / {dataItem.max} max
                      </p>
                      <p className="text-[11px] text-slate-400 mt-2 border-t border-slate-800 pt-1.5 italic">
                        "{dataItem.increaseReason}"
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="score" radius={[6, 6, 0, 0]}>
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Details List */}
      <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
        {data.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between text-xs bg-slate-50 p-2 rounded-lg border border-slate-100">
            <span className="font-medium text-slate-700">{item.feature}</span>
            <div className="flex items-center gap-2">
              <span className="text-slate-500 font-mono">{item.value}</span>
              <span className="font-bold text-indigo-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                +{item.score_impact} / {item.max_possible_impact} pts
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
