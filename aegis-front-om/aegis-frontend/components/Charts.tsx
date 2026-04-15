'use client';

import { ScanMetadata, Finding } from '@/lib/data';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

interface ChartsProps {
  metadata: ScanMetadata;
  findings: Finding[];
}

export default function Charts({ metadata, findings }: ChartsProps) {
  // Data for Pie Chart (Severity Distribution)
  const severityData = [
    { name: 'Critical', value: metadata.critical, color: '#EF4444' },
    { name: 'High', value: metadata.high, color: '#F97316' },
    { name: 'Medium', value: metadata.medium, color: '#EAB308' },
    { name: 'Low', value: metadata.low, color: '#22C55E' },
    { name: 'Info', value: metadata.informational, color: '#6B7280' },
  ].filter(item => item.value > 0);

  // Data for Bar Chart (Findings by Category)
  const categoryCounts = findings.reduce((acc, finding) => {
    acc[finding.category] = (acc[finding.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const categoryData = Object.keys(categoryCounts).map(category => ({
    name: category,
    count: categoryCounts[category]
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Severity Distribution */}
      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800">
        <h3 className="text-white font-semibold mb-6">Severity Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#121212', borderColor: '#374151', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="bottom" height={36} iconType="circle" />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Findings by Category */}
      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800">
        <h3 className="text-white font-semibold mb-6">Findings by Category</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryData} margin={{ top: 5, right: 30, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="name" stroke="#9CA3AF" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis stroke="#9CA3AF" tick={{ fill: '#9CA3AF', fontSize: 12 }} axisLine={false} tickLine={false} />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: '#121212', borderColor: '#374151', color: '#fff' }}
                cursor={{ fill: '#1F2937' }}
              />
              <Bar dataKey="count" fill="#D4FF3F" radius={[4, 4, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
