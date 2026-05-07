'use client';

import { useState } from 'react';
import { LayoutDashboard, ShieldAlert, Activity, FileText, Menu } from 'lucide-react';
import Link from 'next/link';

export default function Sidebar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Hamburger button - always visible top left */}
      <button
        onClick={() => setOpen(!open)}
        style={{ position: 'fixed', top: '16px', left: '16px', zIndex: 9999 }}
        className="w-10 h-10 bg-dashboard-card border border-gray-700 rounded-lg flex items-center justify-center text-gray-400 hover:text-white"
      >
        <Menu size={18} />
      </button>

      {/* Overlay */}
      {open && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 9998, background: 'rgba(0,0,0,0.5)' }}
          onClick={() => setOpen(false)}
        />
      )}

      {/* Drawer */}
      <aside
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          width: '256px',
          zIndex: 9999,
          transform: open ? 'translateX(0)' : 'translateX(-100%)',
          transition: 'transform 0.3s ease',
          background: '#121212',
          borderRight: '1px solid #1f2937',
          display: 'flex',
          flexDirection: 'column',
          padding: '24px 0',
        }}
      >
        <div className="flex items-center px-6 mb-10 mt-2">
          <div className="w-8 h-8 rounded bg-dashboard-accent flex items-center justify-center text-dashboard-bg font-bold">
            <ShieldAlert size={20} />
          </div>
          <span className="ml-3 font-bold text-lg tracking-tight text-white">AEGIS</span>
        </div>

        <nav className="flex flex-col w-full gap-2 px-3">
          <Link href="/" onClick={() => setOpen(false)} className="flex items-center p-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 w-full transition-colors">
            <LayoutDashboard size={20} />
            <span className="ml-3 font-medium">Home</span>
          </Link>
          <Link href="/scan" onClick={() => setOpen(false)} className="flex items-center p-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 w-full transition-colors">
            <Activity size={20} />
            <span className="ml-3 font-medium">Scans</span>
          </Link>
          <Link href="/dashboard" onClick={() => setOpen(false)} className="flex items-center p-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 w-full transition-colors">
            <FileText size={20} />
            <span className="ml-3 font-medium">Dashboard</span>
          </Link>
          <Link href="#" onClick={() => setOpen(false)} className="flex items-center p-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 w-full transition-colors">
            <FileText size={20} />
            <span className="ml-3 font-medium">Reports</span>
          </Link>
        </nav>

        <div className="mt-auto px-6">
          <p className="text-xs text-gray-700">AEGIS v1.0.0</p>
          <p className="text-xs text-gray-700">B.Tech Cybersecurity</p>
        </div>
      </aside>
    </>
  );
}