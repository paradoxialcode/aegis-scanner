'use client';

import { ShieldAlert } from 'lucide-react'
import { useState, useEffect, useRef } from 'react';
import Sidebar from '@/components/Sidebar';
import { useRouter } from 'next/navigation';
import { Play, Terminal, Loader2 } from 'lucide-react';

<div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800">
  <div className="ml-12 flex items-center gap-2">
    <ShieldAlert size={20} className="text-dashboard-accent" />
    <span className="font-bold text-white tracking-tight">AEGIS</span>
  </div>
</div>

export default function ScanPage() {
  const router = useRouter();
  const [target, setTarget] = useState('');
  const [customFlags, setCustomFlags] = useState('');
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // Auto scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, []);

  const pollStatus = async () => {
    try {
      const res = await fetch('http://127.0.0.1:5000/api/scan_status');
      const data = await res.json();

      setProgress(data.progress);
      setStage(data.stage || 'Running...');
      setLogs(data.logs || []);

      if (data.done) {
        if (data.error) {
          setError(data.error);
          setScanning(false);
        } else {
          // Wait a moment then redirect to dashboard
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
        }
        return;
      }

      // Keep polling
      pollRef.current = setTimeout(pollStatus, 1500);
    } catch (err) {
      setError('Lost connection to scanner. Is Flask running?');
      setScanning(false);
    }
  };

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;

    setScanning(true);
    setError(null);
    setLogs([]);
    setProgress(0);
    setStage('Initialising...');

    try {
      // Send scan request to Flask
      const formData = new FormData();
      formData.append('target', target);
      formData.append('custom_flags', customFlags);

      const res = await fetch('http://127.0.0.1:5000/scan', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Failed to start scan');

      // Start polling status
      pollRef.current = setTimeout(pollStatus, 1000);
    } catch (err) {
      setError('Failed to connect to Flask backend. Make sure it is running on port 5000.');
      setScanning(false);
    }
  };

  const getLogColor = (log: string) => {
    if (log.includes('[OK  ]') || log.includes('[DONE]')) return 'text-green-400';
    if (log.includes('[ERR ]')) return 'text-red-400';
    if (log.includes('[RUN ]')) return 'text-dashboard-accent';
    if (log.includes('[FIND]') || log.includes('[WARN]')) return 'text-yellow-400';
    return 'text-gray-400';
  };

  return (
    <div className="min-h-screen bg-dashboard-bg flex">
      <Sidebar />

      <div className="flex-1 flex flex-col min-h-screen">

        <div className="mt-3 mb-8 pl-16">
          <h1 className="text-2xl font-bold text-white mb-2">New Scan</h1>
          <p className="text-gray-400 text-sm">Enter a target IP or hostname to begin scanning</p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

          {/* Scan Form */}
          <div className="bg-dashboard-card rounded-xl border border-gray-800 p-6">
            <h2 className="text-white font-semibold mb-6 flex items-center gap-2">
              <Terminal size={18} className="text-dashboard-accent" />
              Scan Configuration
            </h2>

            <form onSubmit={handleScan} className="space-y-5">
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                  Target IP / Hostname
                </label>
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="e.g. 192.168.1.1 or scanme.nmap.org"
                  disabled={scanning}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-600 font-mono text-sm focus:outline-none focus:border-dashboard-accent transition-colors disabled:opacity-50"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                  Custom Nmap Flags (Optional)
                </label>
                <input
                  type="text"
                  value={customFlags}
                  onChange={(e) => setCustomFlags(e.target.value)}
                  placeholder="e.g. -v -p 1-1000 --script vuln"
                  disabled={scanning}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-600 font-mono text-sm focus:outline-none focus:border-dashboard-accent transition-colors disabled:opacity-50"
                />
              </div>

              {/* Warning */}
              <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4 text-xs text-yellow-400">
                ⚠ Only scan systems you own or have written authorisation to test.
                Unauthorised scanning is illegal.
              </div>

              <button
                type="submit"
                disabled={scanning || !target.trim()}
                className="w-full flex items-center justify-center gap-2 bg-dashboard-accent text-dashboard-bg font-bold py-3 rounded-lg hover:bg-dashboard-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {scanning ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    SCANNING...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    EXECUTE SCAN
                  </>
                )}
              </button>

              {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                  {error}
                </div>
              )}
            </form>

            {/* Nmap Cheatsheet */}
            <div className="mt-6 border-t border-gray-800 pt-6">
              <h3 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
                Nmap Quick Reference
              </h3>
              <div className="space-y-2">
                {[
                  ['-sV', 'Detect service versions'],
                  ['-O', 'OS fingerprinting'],
                  ['-T4', 'Aggressive timing'],
                  ['-p 80,443', 'Scan specific ports'],
                  ['-sS', 'TCP SYN stealth scan'],
                  ['-A', 'Aggressive (OS + version + scripts)'],
                  ['--top-ports 100', 'Scan top 100 ports'],
                  ['-oN out.txt', 'Save results to file'],
                ].map(([cmd, desc]) => (
                  <div key={cmd} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-dashboard-accent">{cmd}</span>
                    <span className="text-gray-500">{desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Live Terminal */}
          <div className="bg-dashboard-card rounded-xl border border-gray-800 overflow-hidden flex flex-col">
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <span className="text-xs text-gray-500 font-mono ml-2">aegis@scanner:~$</span>
              </div>
              {scanning && (
                <span className="text-xs text-dashboard-accent font-mono animate-pulse">
                  ● SCANNING {progress}%
                </span>
              )}
            </div>

            {/* Progress bar */}
            {scanning && (
              <div className="px-4 pt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>{stage}</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div
                    className="bg-dashboard-accent h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Terminal output */}
            <div className="flex-1 p-4 font-mono text-xs overflow-y-auto h-96 space-y-1">
              {logs.length === 0 && !scanning && (
                <p className="text-gray-600">
                  Enter a target and click Execute Scan to begin...
                </p>
              )}
              {logs.map((log, i) => (
                <div key={i} className={getLogColor(log)}>
                  {log}
                </div>
              ))}
              {progress === 100 && !error && (
                <div className="text-dashboard-accent mt-2">
                  ✓ Scan complete! Redirecting to dashboard...
                </div>
              )}
              <div ref={logsEndRef} />
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
