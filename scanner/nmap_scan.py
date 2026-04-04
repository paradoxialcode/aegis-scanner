import nmap
import json
import os
import datetime

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(data):
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def run_nmap(target):
    print(f"[NMAP] Starting scan on target: {target}")

    nm = nmap.PortScanner()

    # Run scan: -sV = service version, -O = OS detection, -T4 = aggressive timing
    try:
        nm.scan(hosts=target, arguments="-sV -O -T4 --top-ports 1000")
    except Exception as e:
        print(f"[NMAP] Scan error: {e}")
        return

    # Check if target was scanned
    if target not in nm.all_hosts():
        print(f"[NMAP] No results for target: {target}")
        return

    host = nm[target]

    # ── Collect open ports ──
    open_ports = []
    for proto in host.all_protocols():
        for port in sorted(host[proto].keys()):
            port_info = host[proto][port]
            if port_info["state"] == "open":
                open_ports.append({
                    "port": port,
                    "protocol": proto,
                    "state": port_info["state"],
                    "service": port_info.get("name", "unknown"),
                    "version": f"{port_info.get('product', '')} {port_info.get('version', '')}".strip(),
                    "os_guess": ""
                })

    # ── OS detection ──
    os_detection = "Unknown"
    if "osmatch" in host and host["osmatch"]:
        os_detection = host["osmatch"][0].get("name", "Unknown")

    # ── Hostname ──
    hostname = ""
    if host.hostname():
        hostname = host.hostname()

    # ── MAC address ──
    mac_address = ""
    if "addresses" in host and "mac" in host["addresses"]:
        mac_address = host["addresses"]["mac"]

    print(f"[NMAP] Found {len(open_ports)} open ports")
    print(f"[NMAP] OS detected: {os_detection}")

    # ── Load and update results.json ──
    results = load_results()

    results["scan_metadata"]["target"] = target
    results["scan_metadata"]["scan_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results["nmap_results"]["open_ports"] = open_ports
    results["nmap_results"]["os_detection"] = os_detection
    results["nmap_results"]["hostname"] = hostname
    results["nmap_results"]["mac_address"] = mac_address

    # ── Add nmap-based findings ──
    # Check for outdated/risky services
    risky_ports = {
        21:   ("FTP Open",              "A06 - Vulnerable Components", "FTP transmits data in plaintext. Disable or replace with SFTP."),
        23:   ("Telnet Open",           "A02 - Cryptographic Failures", "Telnet transmits credentials in plaintext. Replace with SSH."),
        3306: ("MySQL Exposed",         "A05 - Security Misconfiguration", "MySQL port accessible externally. Restrict to localhost."),
        5432: ("PostgreSQL Exposed",    "A05 - Security Misconfiguration", "PostgreSQL port accessible externally. Restrict to localhost."),
        27017:("MongoDB Exposed",       "A05 - Security Misconfiguration", "MongoDB port accessible externally. Enable authentication and restrict access."),
        6379: ("Redis Exposed",         "A05 - Security Misconfiguration", "Redis port accessible externally. Enable auth and restrict access."),
        8080: ("HTTP Alt Port Open",    "A05 - Security Misconfiguration", "Alternate HTTP port open. Ensure it is intentional and secured."),
        445:  ("SMB Open",              "A05 - Security Misconfiguration", "SMB port open. Patch regularly and restrict external access."),
        139:  ("NetBIOS Open",          "A05 - Security Misconfiguration", "NetBIOS open. Disable if not needed, high risk of exploitation."),
    }

    nmap_findings = []
    finding_counter = 1

    for port_info in open_ports:
        port = port_info["port"]
        if port in risky_ports:
            name, category, remediation = risky_ports[port]
            nmap_findings.append({
                "id": f"FINDING-N{finding_counter:03d}",
                "source": "nmap",
                "category": category,
                "name": name,
                "description": f"Port {port}/{port_info['protocol']} is open and running {port_info['service']} ({port_info['version']}).",
                "affected_url": f"{target}:{port}",
                "evidence": f"Nmap scan: {port}/{port_info['protocol']} open {port_info['service']} {port_info['version']}",
                "severity": None,
                "cvss_score": None,
                "cvss_vector": None,
                "remediation": remediation,
                "references": []
            })
            finding_counter += 1

    # Remove old nmap findings and add new ones
    results["findings"] = [f for f in results["findings"] if f["source"] != "nmap"]
    results["findings"].extend(nmap_findings)

    save_results(results)
    print(f"[NMAP] Wrote {len(nmap_findings)} findings to results.json")
    print("[NMAP] Scan complete!")


if __name__ == "__main__":
    target = input("Enter target IP: ").strip()
    run_nmap(target)