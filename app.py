import json
import os
import threading
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "aegis_secret"

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")

# ── Scan state (tracks progress for scanning page) ──
scan_state = {
    "running": False,
    "stage": "",
    "progress": 0,
    "logs": [],
    "done": False,
    "error": None
}


def load_results():
    try:
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def reset_scan_state():
    scan_state["running"] = False
    scan_state["stage"] = ""
    scan_state["progress"] = 0
    scan_state["logs"] = []
    scan_state["done"] = False
    scan_state["error"] = None


def reset_results(target):
    """Reset results.json for a fresh scan"""
    empty = {
        "scan_metadata": {
            "target": target,
            "scan_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scanner_version": "1.0.0",
            "duration_seconds": 0,
            "total_findings": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0,
            "risk_score": 0.0
        },
        "nmap_results": {
            "open_ports": [],
            "os_detection": "",
            "hostname": "",
            "mac_address": ""
        },
        "findings": []
    }
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(empty, f, indent=2)


def run_scan_background(target):
    """Runs the full scan pipeline in a background thread"""
    import time
    start_time = time.time()

    try:
        # ── Stage 1: Nmap ──
        scan_state["stage"] = "Nmap Scan"
        scan_state["progress"] = 10
        scan_state["logs"].append(f"[INFO] Target acquired: {target}")
        scan_state["logs"].append("[RUN ] Launching Nmap scanner...")

        from scanner.nmap_scan import run_nmap
        run_nmap(target)

        scan_state["progress"] = 40
        scan_state["logs"].append("[OK  ] Nmap scan complete")

        # ── Stage 2: OWASP (placeholder for now) ──
        scan_state["stage"] = "OWASP Tests"
        scan_state["progress"] = 45
        scan_state["logs"].append("[RUN ] Starting OWASP Top 10 tests...")
        scan_state["logs"].append("[INFO] OWASP module coming soon...")
        scan_state["progress"] = 65
        scan_state["logs"].append("[OK  ] OWASP tests complete")

        # ── Stage 3: CVSS Scoring (placeholder for now) ──
        scan_state["stage"] = "CVSS Scoring"
        scan_state["progress"] = 70
        scan_state["logs"].append("[RUN ] Calculating CVSS scores...")
        scan_state["logs"].append("[INFO] CVSS module coming soon...")
        scan_state["progress"] = 85
        scan_state["logs"].append("[OK  ] Scoring complete")

        # ── Stage 4: Finalise ──
        scan_state["stage"] = "Finalising"
        scan_state["progress"] = 90
        scan_state["logs"].append("[RUN ] Writing final results...")

        # Update duration in results.json
        results = load_results()
        if results:
            duration = int(time.time() - start_time)
            results["scan_metadata"]["duration_seconds"] = duration
            with open(RESULTS_PATH, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)

        scan_state["progress"] = 100
        scan_state["logs"].append("[DONE] Scan complete. Redirecting to results...")
        scan_state["done"] = True

    except Exception as e:
        scan_state["error"] = str(e)
        scan_state["logs"].append(f"[ERR ] Scan failed: {e}")
        scan_state["done"] = True


# ── Routes ──

@app.route("/")
def index():
    reset_scan_state()
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    target = request.form.get("target", "").strip()
    if not target:
        return redirect(url_for("index"))

    # Reset everything for fresh scan
    reset_scan_state()
    reset_results(target)

    # Start scan in background thread
    scan_state["running"] = True
    thread = threading.Thread(target=run_scan_background, args=(target,))
    thread.daemon = True
    thread.start()

    return render_template("scanning.html", target=target)


@app.route("/api/scan_status")
def scan_status():
    """Frontend polls this to get live scan progress"""
    return jsonify({
        "stage": scan_state["stage"],
        "progress": scan_state["progress"],
        "logs": scan_state["logs"],
        "done": scan_state["done"],
        "error": scan_state["error"]
    })


@app.route("/results")
def results():
    data = load_results()
    if not data:
        return redirect(url_for("index"))
    return render_template("results.html", data=data)


@app.route("/api/results")
def api_results():
    data = load_results()
    if not data:
        return jsonify({"error": "No results found"}), 404
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)