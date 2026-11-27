'use client';

import { useState } from 'react';
import { Finding } from '@/lib/data';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function FindingsTable({ findings }: { findings: Finding[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-severity-critical/20 text-severity-critical border-severity-critical/30';
      case 'high': return 'bg-severity-high/20 text-severity-high border-severity-high/30';
      case 'medium': return 'bg-severity-medium/20 text-severity-medium border-severity-medium/30';
      case 'low': return 'bg-severity-low/20 text-severity-low border-severity-low/30';
      default: return 'bg-gray-800 text-gray-300 border-gray-700';
    }
  };

  const toggleExpand = (id: string) => {
    setExpanded(expanded === id ? null : id);
  };

  return (
    <div className="bg-dashboard-card rounded-xl border border-gray-800 overflow-hidden mb-8">
      <div className="p-6 border-b border-gray-800 flex justify-between items-center">
        <h3 className="text-white font-semibold">Vulnerabilities</h3>
        <span className="text-xs text-gray-500">{findings.length} findings — click to expand</span>
      </div>
      <div className="divide-y divide-gray-800">
        {findings.map((finding) => (
          <div key={finding.id}>
            {/* Main row */}
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-800/20 transition-colors"
              onClick={() => toggleExpand(finding.id)}
            >
              <div className="flex items-center gap-4 min-w-0">
                <span className="text-gray-500 font-mono text-xs shrink-0">{finding.id}</span>
                <span className="text-white font-medium truncate">{finding.name}</span>
                <span className="text-gray-500 text-xs hidden md:block shrink-0">{finding.category}</span>
              </div>
              <div className="flex items-center gap-3 shrink-0 ml-4">
                <span className={`px-2.5 py-1 rounded border text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                  {finding.severity}
                </span>
                <span className="text-gray-300 font-mono text-sm">{finding.cvss_score.toFixed(1)}</span>
                {expanded === finding.id
                  ? <ChevronUp size={16} className="text-gray-400" />
                  : <ChevronDown size={16} className="text-gray-400" />
                }
              </div>
            </div>

            {/* Expanded detail */}
            {expanded === finding.id && (
              <div className="bg-gray-900/50 border-t border-gray-800 p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Affected URL</p>
                  <p className="text-dashboard-accent font-mono text-xs break-all">{finding.affected_url}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Evidence</p>
                  <p className="text-yellow-400 font-mono text-xs bg-black/30 p-2 rounded">
                    {(finding as any).evidence || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Remediation</p>
                  <p className="text-gray-300 text-xs">{finding.remediation}</p>
                </div>
              </div>
            )}
          </div>
        ))}
        {findings.length === 0 && (
          <div className="p-8 text-center text-gray-500">No vulnerabilities found.</div>
        )}
      </div>
    </div>
  );
}