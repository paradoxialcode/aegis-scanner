import json
import os

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")

# ── Pre-defined CVSS vectors for known finding types ──
# These map finding names to their CVSS v3.1 vector and score
CVSS_MAPPING = {
    # Nmap-based findings
    "FTP Open": {
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "severity": "High"
    },
    "Telnet Open": {
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "Critical"
    },
    "MySQL Exposed": {
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "severity": "High"
    },
    "PostgreSQL Exposed": {
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "severity": "High"
    },
    "MongoDB Exposed": {
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "Critical"
    },
    "Redis Exposed": {
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "Critical"
    },
    "HTTP Alt Port Open": {
        "cvss_score": 5.3,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
        "severity": "Medium"
    },
    "SMB Open": {
        "cvss_score": 8.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "High"
    },
    "NetBIOS Open": {
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "severity": "High"
    },
    # OWASP-based findings
    "SQL Injection Detected": {
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "severity": "Critical"
    },
    "Reflected Cross-Site Scripting (XSS)": {
        "cvss_score": 8.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N",
        "severity": "High"
    },
    "Stored Cross-Site Scripting (XSS)": {
        "cvss_score": 9.0,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N",
        "severity": "Critical"
    },
    "Directory Listing Enabled": {
        "cvss_score": 5.3,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
        "severity": "Medium"
    },
    "Sensitive Data Over HTTP": {
        "cvss_score": 9.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
        "severity": "Critical"
    },
    "Outdated Apache Version": {
        "cvss_score": 6.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N",
        "severity": "Medium"
    },
    "Admin Panel Accessible Without Auth": {
        "cvss_score": 3.7,
        "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N",
        "severity": "Low"
    },
    "No Account Lockout Policy": {
        "cvss_score": 7.2,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "severity": "High"
    },
    "No Rate Limiting Detected": {
        "cvss_score": 0.0,
        "cvss_vector": None,
        "severity": "Informational"
    },
    "No Login Event Logging": {
        "cvss_score": 3.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N",
        "severity": "Low"
    },
}


def get_severity_from_score(score):
    """Map a CVSS score to a severity label"""
    if score >= 9.0:
        return "Critical"
    elif score >= 7.0:
        return "High"
    elif score >= 4.0:
        return "Medium"
    elif score > 0.0:
        return "Low"
    else:
        return "Informational"


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(data):
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def score_findings():
    print("[CVSS] Starting scoring engine...")

    results = load_results()
    findings = results.get("findings", [])

    if not findings:
        print("[CVSS] No findings to score.")
        return

    scored = 0
    for finding in findings:
        name = finding.get("name", "")

        # Check if we have a pre-defined mapping for this finding
        if name in CVSS_MAPPING:
            mapping = CVSS_MAPPING[name]
            finding["cvss_score"]  = mapping["cvss_score"]
            finding["cvss_vector"] = mapping["cvss_vector"]
            finding["severity"]    = mapping["severity"]
            scored += 1
        else:
            # Unknown finding — assign medium by default
            if finding["cvss_score"] is None:
                finding["cvss_score"]  = 5.0
                finding["cvss_vector"] = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N"
                finding["severity"]    = "Medium"
                scored += 1

        print(f"[CVSS] {finding['id']} -> {finding['cvss_score']} [{finding['severity']}]")

    # ── Update metadata counts ──
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Informational": 0}
    for finding in findings:
        sev = finding.get("severity", "Informational")
        if sev in counts:
            counts[sev] += 1

    results["scan_metadata"]["total_findings"]  = len(findings)
    results["scan_metadata"]["critical"]        = counts["Critical"]
    results["scan_metadata"]["high"]            = counts["High"]
    results["scan_metadata"]["medium"]          = counts["Medium"]
    results["scan_metadata"]["low"]             = counts["Low"]
    results["scan_metadata"]["informational"]   = counts["Informational"]

    # ── Calculate overall risk score (weighted average) ──
    if findings:
        scores = [f["cvss_score"] for f in findings if f["cvss_score"] is not None]
        if scores:
            # Weight towards highest scores
            risk_score = round((max(scores) * 0.6) + (sum(scores) / len(scores) * 0.4), 1)
            results["scan_metadata"]["risk_score"] = min(risk_score, 10.0)

    results["findings"] = findings
    save_results(results)

    print(f"[CVSS] Scored {scored} findings")
    print(f"[CVSS] Risk score: {results['scan_metadata']['risk_score']}")
    print("[CVSS] Scoring complete!")


if __name__ == "__main__":
    score_findings()