'use client';

import { ShieldAlert } from 'lucide-react'
import { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import TopCards from '@/components/TopCards';
import Charts from '@/components/Charts';
import PortsTable from '@/components/PortsTable';
import FindingsTable from '@/components/FindingsTable';
import { ScanResults } from '@/lib/data';
import { Download, Loader2 } from 'lucide-react';

<div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800">
  <div className="ml-12 flex items-center gap-2">
    <ShieldAlert size={20} className="text-dashboard-accent" />
    <span className="font-bold text-white tracking-tight">AEGIS</span>
  </div>
</div>

export default function Dashboard() {
  const [data, setData] = useState<ScanResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/results', { cache: 'no-store' });
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const resultData = await response.json();
        setData(resultData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const handleDownloadReport = () => {
    // In a real app, we might use a specific ID. Here we just use a generic 'latest'.
    window.location.href = '/api/report/latest';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dashboard-bg flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 text-dashboard-accent animate-spin" />
          <p className="text-gray-400 font-medium">Loading scan results...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-dashboard-bg flex items-center justify-center">
        <div className="bg-dashboard-card p-8 rounded-xl border border-red-900/50 max-w-md text-center">
          <div className="w-16 h-16 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-bold">!</span>
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-400 mb-6">{error || 'No data available'}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-dashboard-accent text-dashboard-bg font-semibold px-6 py-2 rounded-lg hover:bg-dashboard-accent-hover transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dashboard-bg flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col min-h-screen">
        <Header />
        
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">Scan Overview</h2>
              <p className="text-gray-400 text-sm">Target: {data.scan_metadata.target}</p>
            </div>
            
            <button 
              onClick={handleDownloadReport}
              className="flex items-center gap-2 bg-dashboard-accent text-dashboard-bg font-semibold px-5 py-2.5 rounded-lg hover:bg-dashboard-accent-hover transition-colors"
            >
              <Download size={18} />
              <span>Generate Report</span>
            </button>
          </div>
          
          <TopCards metadata={data.scan_metadata} />
          
          <Charts metadata={data.scan_metadata} findings={data.findings} />
          
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            <div className="xl:col-span-1">
              <PortsTable ports={data.nmap_results.open_ports} />
            </div>
            <div className="xl:col-span-2">
              <FindingsTable findings={data.findings} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
