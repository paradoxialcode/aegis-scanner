import json
import os
import time
import subprocess
import sys
import argparse
from datetime import datetime

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")
BACKEND_DIR  = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "aegis-frontend")

BANNER = """
  ___  ___ _____ ___ ___ 
 / _ \| __|/ __||_ _/ __|
| (_) | _|| (_ | | |\__ \\
 \___/|___|\___||___|___/

  Automated Network Vulnerability Scanner
  B.Tech Cybersecurity - 2nd Year
  v1.0.0
"""


def print_banner():
    print("\033[92m" + BANNER + "\033[0m")


def log(tag, msg, color="\033[0m"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\033[90m[{timestamp}]\033[0m {color}[{tag}]\033[0m {msg}")


def start_servers():
    processes = []

    # Start Flask
    log("SERVER", "Starting Flask backend on port 5000...", "\033[96m")
    flask_proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=BACKEND_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    processes.append(("Flask", flask_proc))
    time.sleep(2)
    log("SERVER", "Flask running at http://127.0.0.1:5000", "\033[92m")

    # Start Next.js
    frontend_path = os.path.abspath(FRONTEND_DIR)
    if os.path.exists(frontend_path):
        log("SERVER", "Starting Next.js frontend on port 3000...", "\033[96m")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        nextjs_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(("Next.js", nextjs_proc))
        time.sleep(4)
        log("SERVER", "Next.js running at http://localhost:3000", "\033[92m")
    else:
        log("SERVER", f"Frontend not found at {frontend_path} - skipping", "\033[93m")

    return processes


def stop_servers(processes):
    print()
    for name, proc in processes:
        log("SERVER", f"Stopping {name}...", "\033[91m")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    log("SERVER", "All servers stopped.", "\033[91m")


def reset_results(target):
    empty = {
        "scan_metadata": {
            "target": target,
            "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scanner_version": "1.0.0",
            "duration_seconds": 0,
            "total_findings": 0,
            "critical": 0, "high": 0, "medium": 0,
            "low": 0, "informational": 0,
            "risk_score": 0.0
        },
        "nmap_results": {
            "open_ports": [], "os_detection": "",
            "hostname": "", "mac_address": ""
        },
        "findings": []
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(empty, f, indent=2)


def run_pipeline(target, skip_owasp=False, generate_pdf=True):
    start_time = time.time()
    log("INIT", f"Starting AEGIS scan on target: \033[92m{target}\033[0m", "\033[96m")
    reset_results(target)

    # Stage 1: Nmap
    print("\n" + "="*50)
    log("NMAP", "Starting network scan...", "\033[92m")
    try:
        from scanner.nmap_scan import run_nmap
        run_nmap(target)
        log("NMAP", "Scan complete!", "\033[92m")
    except Exception as e:
        log("NMAP", f"Error: {e}", "\033[91m")
        return False

    # Stage 2: OWASP
    print("\n" + "="*50)
    if skip_owasp:
        log("OWASP", "Skipping OWASP tests (--skip-owasp flag)", "\033[93m")
    else:
        log("OWASP", "Starting OWASP Top 10 tests...", "\033[95m")
        try:
            from scanner.owasp_tests import run_owasp
            run_owasp(target)
            log("OWASP", "Tests complete!", "\033[95m")
        except ImportError:
            log("OWASP", "Module not ready yet - skipping", "\033[93m")
        except Exception as e:
            log("OWASP", f"Error: {e}", "\033[91m")

    # Stage 3: CVSS
    print("\n" + "="*50)
    log("CVSS", "Calculating CVSS scores...", "\033[93m")
    try:
        from scoring.cvss_score import score_findings
        score_findings()
        log("CVSS", "Scoring complete!", "\033[93m")
    except Exception as e:
        log("CVSS", f"Error: {e}", "\033[91m")
        return False

    # Update duration
    duration = int(time.time() - start_time)
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)
    results["scan_metadata"]["duration_seconds"] = duration
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Stage 4: PDF
    print("\n" + "="*50)
    if generate_pdf:
        log("REPORT", "Generating PDF report...", "\033[94m")
        try:
            from output.report import generate_report
            report_path = generate_report()
            log("REPORT", f"PDF saved: {report_path}", "\033[94m")
        except Exception as e:
            log("REPORT", f"Error: {e}", "\033[91m")

    # Summary
    print("\n" + "="*50)
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)
    meta = results["scan_metadata"]

    print("\n\033[92m SCAN COMPLETE \033[0m")
    print(f"  Target:      {meta['target']}")
    print(f"  Duration:    {meta['duration_seconds']}s")
    print(f"  Findings:    {meta['total_findings']} total")
    print(f"  Critical:    \033[91m{meta['critical']}\033[0m")
    print(f"  High:        \033[93m{meta['high']}\033[0m")
    print(f"  Medium:      \033[33m{meta['medium']}\033[0m")
    print(f"  Low:         \033[92m{meta['low']}\033[0m")
    print(f"  Risk Score:  {meta['risk_score']}/10.0")
    print(f"\n  Dashboard: \033[96mhttp://localhost:3000/dashboard\033[0m\n")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEGIS - Automated Network Vulnerability Scanner")
    parser.add_argument("target", nargs="?", help="Target IP or hostname (optional)")
    parser.add_argument("--skip-owasp", action="store_true", help="Skip OWASP tests")
    parser.add_argument("--no-pdf",     action="store_true", help="Skip PDF generation")
    parser.add_argument("--no-servers", action="store_true", help="Do not auto-start servers")
    args = parser.parse_args()

    print_banner()
    processes = []

    if not args.no_servers:
        print("="*50)
        log("AEGIS", "Starting servers...", "\033[96m")
        processes = start_servers()
        print("="*50)

    if args.target:
        run_pipeline(
            target=args.target,
            skip_owasp=args.skip_owasp,
            generate_pdf=not args.no_pdf
        )
    else:
        log("AEGIS", "Servers running! Open browser to scan:", "\033[92m")
        print(f"\n  \033[96mhttp://localhost:3000\033[0m\n")
        log("AEGIS", "Press Ctrl+C to stop all servers.", "\033[93m")

    if processes:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            stop_servers(processes)