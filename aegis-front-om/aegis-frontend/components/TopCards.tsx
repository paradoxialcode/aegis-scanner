import { ScanMetadata } from '@/lib/data';
import { AlertTriangle, Shield, Server, Activity } from 'lucide-react';

export default function TopCards({ metadata }: { metadata: ScanMetadata }) {
  // Determine overall risk level based on critical/high findings
  let riskLevel = 'Low';
  let riskColor = 'text-severity-low';
  
  if (metadata.critical > 0) {
    riskLevel = 'Critical';
    riskColor = 'text-severity-critical';
  } else if (metadata.high > 0) {
    riskLevel = 'High';
    riskColor = 'text-severity-high';
  } else if (metadata.medium > 0) {
    riskLevel = 'Medium';
    riskColor = 'text-severity-medium';
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-gray-400 font-medium text-sm">Total Findings</h3>
          <div className="p-2 bg-gray-800/50 rounded-lg">
            <AlertTriangle size={18} className="text-gray-300" />
          </div>
        </div>
        <div className="text-3xl font-bold text-white mb-1">{metadata.total_findings}</div>
        <div className="text-xs text-gray-500">Across all categories</div>
      </div>

      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-gray-400 font-medium text-sm">Risk Level</h3>
          <div className="p-2 bg-gray-800/50 rounded-lg">
            <Shield size={18} className={riskColor} />
          </div>
        </div>
        <div className={`text-3xl font-bold mb-1 ${riskColor}`}>{riskLevel}</div>
        <div className="text-xs text-gray-500">Based on highest severity</div>
      </div>

      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-gray-400 font-medium text-sm">Target</h3>
          <div className="p-2 bg-gray-800/50 rounded-lg">
            <Server size={18} className="text-gray-300" />
          </div>
        </div>
        <div className="text-xl font-bold text-white mb-1 truncate" title={metadata.target}>
          {metadata.target}
        </div>
        <div className="text-xs text-gray-500">Scanned host</div>
      </div>

      <div className="bg-dashboard-card p-6 rounded-xl border border-gray-800 flex flex-col">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-gray-400 font-medium text-sm">Scan Date</h3>
          <div className="p-2 bg-gray-800/50 rounded-lg">
            <Activity size={18} className="text-dashboard-accent" />
          </div>
        </div>
        <div className="text-lg font-bold text-white mb-1">
          {new Date(metadata.scan_date).toLocaleDateString()}
        </div>
        <div className="text-xs text-gray-500">
          {new Date(metadata.scan_date).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
