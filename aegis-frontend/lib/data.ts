import fs from 'fs';
import path from 'path';

export interface ScanMetadata {
  target: string;
  scan_date: string;
  total_findings: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  informational: number;
}

export interface OpenPort {
  port: number;
  protocol: string;
  state: string;
  service: string;
}

export interface Finding {
  id: string;
  name: string;
  category: string;
  severity: string;
  cvss_score: number;
  affected_url: string;
  evidence: string;
  remediation: string;
}

export interface ScanResults {
  scan_metadata: ScanMetadata;
  nmap_results: {
    open_ports: OpenPort[];
  };
  findings: Finding[];
}

export async function getScanResults(): Promise<ScanResults> {
  const filePath = path.join(process.cwd(), '..', 'aegis-backend', 'results.json');
  const fileContents = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(fileContents) as ScanResults;
}
