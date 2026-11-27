'use client';

import { ShieldAlert } from 'lucide-react'
import Link from 'next/link';
import Sidebar from '@/components/Sidebar';
import { Shield, Search, FileText, Activity } from 'lucide-react';

<div className="flex items-center gap-3 px-6 py-4 border-b border-gray-800">
  <div className="ml-12 flex items-center gap-2">
    <ShieldAlert size={20} className="text-dashboard-accent" />
    <span className="font-bold text-white tracking-tight">AEGIS</span>
  </div>
</div>

export default function Home() {
  return (
    <div className="min-h-screen bg-dashboard-bg grid-bg" style={{ position: 'relative', overflow: 'hidden' }}>
      <div className="glow-orb" />
      <Sidebar />

      <div className="flex-1 flex flex-col min-h-screen" style={{ position: 'relative', zIndex: 1 }}>

        <main className="flex-1 flex flex-col items-center justify-center p-8">

          {/* Hero */}
          <div className="text-center mb-16">
            <div className="flex items-center justify-center mb-6">
              <div 
                className="w-20 h-20 rounded-2xl bg-dashboard-accent/10 border-2 border-dashboard-accent flex items-center justify-center"
                style={{
                  boxShadow: '0 0 30px rgba(212, 255, 63, 0.3), 0 0 60px rgba(212, 255, 63, 0.1), 0 0 100px rgba(212, 255, 63, 0.05)'
                }}
              >
                <Shield size={40} className="text-dashboard-accent" style={{ filter: 'drop-shadow(0 0 8px rgba(212, 255, 63, 0.8))' }} />
              </div>
            </div>

            <h1 className="text-6xl font-black text-white tracking-tight mb-2">
              AE<span className="text-dashboard-accent">GIS</span>
            </h1>
            <p className="text-gray-400 text-lg mb-2">Automated Network Vulnerability Scanner</p>
            <p className="text-gray-600 text-sm">v1.0.0 — B.Tech Cybersecurity</p>

            <div className="flex items-center justify-center gap-3 mt-8">
              <Link
                href="/scan"
                className="flex items-center gap-2 bg-dashboard-accent text-dashboard-bg font-bold px-8 py-3 rounded-lg hover:bg-dashboard-accent-hover transition-colors text-sm"
              >
                <Search size={18} />
                START NEW SCAN
              </Link>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 bg-transparent border border-gray-700 text-gray-300 font-medium px-8 py-3 rounded-lg hover:border-gray-500 hover:text-white transition-colors text-sm"
              >
                <Activity size={18} />
                VIEW LAST SCAN
              </Link>
            </div>
          </div>

          {/* Feature cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl">
            <div className="bg-dashboard-card border border-gray-800 rounded-xl p-6 text-center">
              <div className="w-10 h-10 bg-dashboard-accent/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Search size={20} className="text-dashboard-accent" />
              </div>
              <h3 className="text-white font-semibold mb-2">Nmap Scanner</h3>
              <p className="text-gray-500 text-sm">Port discovery, service detection and OS fingerprinting</p>
            </div>

            <div className="bg-dashboard-card border border-gray-800 rounded-xl p-6 text-center">
              <div className="w-10 h-10 bg-dashboard-accent/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield size={20} className="text-dashboard-accent" />
              </div>
              <h3 className="text-white font-semibold mb-2">OWASP Top 10</h3>
              <p className="text-gray-500 text-sm">Automated testing against the most critical web vulnerabilities</p>
            </div>

            <div className="bg-dashboard-card border border-gray-800 rounded-xl p-6 text-center">
              <div className="w-10 h-10 bg-dashboard-accent/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FileText size={20} className="text-dashboard-accent" />
              </div>
              <h3 className="text-white font-semibold mb-2">PDF Reports</h3>
              <p className="text-gray-500 text-sm">Professional reports with CVSS scores and remediation steps</p>
            </div>
          </div>

        </main>

        {/* Footer */}
        <footer className="text-center py-4 text-gray-700 text-xs border-t border-gray-900">
          AEGIS — Automated Network Vulnerability Scanner &nbsp;|&nbsp; B.Tech Cybersecurity 2nd Year Mini Project
        </footer>

      </div>
    </div>
  );
}
