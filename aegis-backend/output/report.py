import json
import os
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from fpdf import FPDF

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "report.pdf")

REMEDIATION_DETAIL = {
    "SSH Open": [
        "Disable root login: Set 'PermitRootLogin no' in /etc/ssh/sshd_config",
        "Use key-based authentication only: Set 'PasswordAuthentication no'",
        "Change default port from 22 to a non-standard port to reduce automated attacks",
        "Implement fail2ban to block repeated failed login attempts",
        "Restrict SSH access by IP using AllowUsers or firewall rules",
    ],
    "HTTP Open": [
        "Install an SSL/TLS certificate (free via Let's Encrypt)",
        "Configure web server to redirect all HTTP traffic to HTTPS",
        "Enable HSTS header: 'Strict-Transport-Security: max-age=31536000'",
        "Disable HTTP port 80 in firewall if HTTPS is fully configured",
        "Test SSL configuration at ssllabs.com/ssltest",
    ],
    "MySQL Exposed": [
        "Bind MySQL to localhost: Set 'bind-address = 127.0.0.1' in my.cnf",
        "Block port 3306 in firewall for external access",
        "Use strong passwords for all MySQL accounts",
        "Remove anonymous user accounts: DROP USER ''@'localhost'",
        "Disable remote root login in MySQL",
    ],
    "FTP Open": [
        "Disable FTP entirely and replace with SFTP (SSH File Transfer Protocol)",
        "If FTP must be used, enforce FTPS (FTP over SSL/TLS)",
        "Restrict FTP access by IP using firewall rules",
        "Use chroot jail to limit FTP user access to specific directories",
        "Enable logging of all FTP activity for audit purposes",
    ],
    "SMB Open": [
        "Apply all Windows security patches immediately (SMB has critical CVEs)",
        "Block SMB ports 445 and 139 at the firewall for external access",
        "Disable SMBv1 which has known critical vulnerabilities",
        "Enable SMB signing to prevent man-in-the-middle attacks",
        "Audit SMB shares and remove unnecessary public shares",
    ],
    "RDP Open": [
        "Never expose RDP directly to the internet - use VPN instead",
        "Enable Network Level Authentication (NLA) for RDP connections",
        "Implement account lockout after failed attempts to prevent brute force",
        "Use strong, unique passwords for all accounts with RDP access",
        "Monitor RDP logs for suspicious login attempts",
    ],
    "Ncat Open": [
        "Immediately investigate whether this is a legitimate service or backdoor",
        "Check running processes: 'netstat -tulnp | grep 9929'",
        "If not legitimate, kill the process and investigate for compromise",
        "Block the port immediately at the firewall level",
        "Run a full malware scan on the system",
    ],
    "Suspicious Port Open": [
        "Port 31337 is associated with Back Orifice malware - treat as critical",
        "Immediately isolate the system from the network",
        "Run a full antivirus and rootkit scan",
        "Check running processes and open files on this port",
        "Review system logs for signs of compromise",
    ],
    "SQL Injection Detected": [
        "Use parameterized queries or prepared statements in all database calls",
        "Never concatenate user input directly into SQL strings",
        "Implement an ORM (Object Relational Mapper) to abstract database calls",
        "Apply input validation and sanitization on all user-supplied data",
        "Use a Web Application Firewall (WAF) as an additional layer",
        "Conduct a full code review of all database-interacting functions",
    ],
    "Reflected Cross-Site Scripting (XSS)": [
        "HTML-encode all user-supplied data before rendering in the browser",
        "Implement Content Security Policy (CSP) headers",
        "Use modern frameworks that auto-escape output (React, Angular, Vue)",
        "Validate and sanitize all input on both client and server side",
        "Set HttpOnly and Secure flags on all session cookies",
    ],
    "default": [
        "Review the affected component and apply the latest security patches",
        "Follow the principle of least privilege for all services",
        "Implement network segmentation to limit exposure",
        "Enable logging and monitoring for the affected service",
        "Consult the vendor's security advisory for specific guidance",
    ]
}


def clean(text):
    """Sanitize text for Latin-1 / fpdf core fonts. Replaces common Unicode
    characters that charmap/Latin-1 cannot encode."""
    if text is None:
        return "N/A"
    text = str(text)
    replacements = {
        '\u2192': '->',   # →
        '\u2190': '<-',   # ←
        '\u2194': '<->',  # ↔
        '\u2013': '-',    # en dash
        '\u2014': '--',   # em dash
        '\u2018': "'",    # left single quote
        '\u2019': "'",    # right single quote
        '\u201c': '"',    # left double quote
        '\u201d': '"',    # right double quote
        '\u2022': '-',    # bullet
        '\u2026': '...',  # ellipsis
        '\u00ae': '(R)',  # ®
        '\u00a9': '(C)',  # ©
        '\u00b0': 'deg',  # °
        '\u00d7': 'x',    # ×
        '\u00f7': '/',    # ÷
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Final fallback: drop anything still outside Latin-1
    return text.encode('latin-1', errors='replace').decode('latin-1')


def generate_donut_chart(meta):
    labels = []
    sizes = []
    colors = []

    color_map = {
        'Critical':      '#FF4C4C',
        'High':          '#FF8C00',
        'Medium':        '#F9A825',
        'Low':           '#00C853',
        'Informational': '#8B949E',
    }

    for label, key in [('Critical','critical'),('High','high'),('Medium','medium'),('Low','low'),('Informational','informational')]:
        val = meta.get(key, 0)
        if val > 0:
            labels.append(f"{label} ({val})")
            sizes.append(val)
            colors.append(color_map[label])

    if not sizes:
        sizes = [1]
        labels = ['No Findings']
        colors = ['#30363D']

    fig, ax = plt.subplots(figsize=(4, 4), facecolor='#0D1117')
    wedges, _ = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.5, edgecolor='#0D1117', linewidth=2)
    )

    ax.set_facecolor('#0D1117')

    legend = ax.legend(
        wedges, labels,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=2,
        fontsize=8,
        frameon=False,
        labelcolor='#8B949E'
    )

    ax.text(0, 0, str(meta.get('total_findings', 0)),
            ha='center', va='center', fontsize=22, fontweight='bold', color='#F0F6FC')
    ax.text(0, -0.18, 'TOTAL', ha='center', va='center', fontsize=7, color='#8B949E')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor='#0D1117', transparent=False)
    plt.close()
    buf.seek(0)
    return buf


def load_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class AEGISReport(FPDF):

    def header(self):
        self.set_fill_color(0, 255, 136)
        self.rect(0, 0, 210, 3, 'F')
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(0, 255, 136)
        self.set_xy(10, 8)
        self.cell(0, 10, "AEGIS", ln=False)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(139, 148, 158)
        self.set_xy(35, 12)
        self.cell(0, 6, "Automated Network Vulnerability Scanner")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(139, 148, 158)
        self.set_xy(140, 8)
        self.cell(60, 5, "VULNERABILITY ASSESSMENT REPORT", align="R")
        self.set_font("Helvetica", "", 8)
        self.set_xy(140, 13)
        self.cell(60, 4, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="R")
        self.set_draw_color(48, 54, 61)
        self.set_line_width(0.3)
        self.line(10, 22, 200, 22)
        self.ln(18)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(139, 148, 158)
        self.cell(0, 5, "AEGIS v1.0.0  |  B.Tech Cybersecurity - 2nd Year  |  Page " + str(self.page_no()), align="C")
        self.set_fill_color(0, 255, 136)
        self.rect(0, 294, 210, 3, 'F')

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(240, 246, 252)
        self.set_fill_color(22, 27, 34)
        self.set_draw_color(48, 54, 61)
        self.rect(10, self.get_y(), 190, 8, 'F')
        self.set_xy(13, self.get_y() + 1)
        self.cell(0, 6, clean(title))
        self.ln(12)

    def severity_color(self, severity):
        s = severity.lower() if severity else "informational"
        if s == "critical":     return (255, 76, 76)
        if s == "high":         return (255, 140, 0)
        if s == "medium":       return (249, 168, 37)
        if s == "low":          return (0, 200, 83)
        return (139, 148, 158)

    def badge(self, x, y, text, color):
        self.set_fill_color(*color)
        self.set_text_color(13, 17, 23)
        self.set_font("Helvetica", "B", 8)
        self.set_xy(x, y)
        self.cell(22, 5, clean(text).upper(), align="C", fill=True)
        self.set_text_color(240, 246, 252)

    def info_row(self, label, value):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(139, 148, 158)
        self.cell(40, 6, clean(label).upper())
        self.set_font("Helvetica", "", 9)
        self.set_text_color(240, 246, 252)
        self.cell(0, 6, clean(value))
        self.ln(7)

    def labeled_field(self, label, value, label_color, value_color):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*label_color)
        self.cell(30, 5, clean(label))
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*value_color)
        value_str = clean(value)[:90]
        self.cell(0, 5, value_str)
        self.ln(6)


def generate_report():
    print("[REPORT] Generating enhanced PDF report...")

    results = load_results()
    meta = results.get("scan_metadata", {})
    nmap = results.get("nmap_results", {})
    findings = results.get("findings", [])

    pdf = AEGISReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    pdf.set_fill_color(13, 17, 23)
    pdf.rect(0, 0, 210, 297, 'F')

    # -- 1. Executive Summary --
    pdf.section_title("1. EXECUTIVE SUMMARY")
    pdf.info_row("Target",    meta.get("target", "N/A"))
    pdf.info_row("Scan Date", meta.get("scan_date", "N/A"))
    pdf.info_row("Duration",  f"{meta.get('duration_seconds', 0)}s")
    pdf.info_row("OS",        nmap.get("os_detection", "Unknown"))
    pdf.info_row("Hostname",  nmap.get("hostname", "N/A"))
    pdf.info_row("Version",   meta.get("scanner_version", "1.0.0"))
    pdf.ln(3)

    # Risk score box
    risk = meta.get("risk_score", 0.0)
    pdf.set_fill_color(22, 27, 34)
    pdf.set_draw_color(48, 54, 61)
    pdf.rect(10, pdf.get_y(), 90, 22, 'FD')
    r, g, b = (255, 76, 76) if risk >= 9 else (255, 140, 0) if risk >= 7 else (249, 168, 37) if risk >= 4 else (0, 200, 83)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(r, g, b)
    pdf.set_xy(12, pdf.get_y() + 3)
    pdf.cell(40, 10, f"{risk}")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(139, 148, 158)
    pdf.set_xy(45, pdf.get_y() - 3)
    pdf.cell(0, 5, "/ 10.0  OVERALL RISK SCORE")
    pdf.ln(28)

    # -- 2. Findings Breakdown + Donut Chart --
    pdf.section_title("2. FINDINGS BREAKDOWN")

    counts = [
        ("TOTAL",         meta.get("total_findings", 0),  (240, 246, 252)),
        ("CRITICAL",      meta.get("critical", 0),         (255, 76, 76)),
        ("HIGH",          meta.get("high", 0),             (255, 140, 0)),
        ("MEDIUM",        meta.get("medium", 0),           (249, 168, 37)),
        ("LOW",           meta.get("low", 0),              (0, 200, 83)),
        ("INFO",          meta.get("informational", 0),    (139, 148, 158)),
    ]

    stat_y = pdf.get_y()
    x = 10
    for label, count, color in counts:
        pdf.set_fill_color(22, 27, 34)
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.4)
        pdf.rect(x, stat_y, 29, 16, 'FD')
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*color)
        pdf.set_xy(x + 2, stat_y + 1)
        pdf.cell(25, 8, str(count), align="C")
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(139, 148, 158)
        pdf.set_xy(x + 2, stat_y + 9)
        pdf.cell(25, 4, label, align="C")
        x += 31

    pdf.ln(22)

    # Donut chart
    chart_buf = generate_donut_chart(meta)
    chart_y = pdf.get_y()
    pdf.image(chart_buf, x=65, y=chart_y, w=80)
    pdf.ln(88)

    # -- 3. Open Ports --
    pdf.section_title("3. OPEN PORTS")
    open_ports = nmap.get("open_ports", [])
    if open_ports:
        pdf.set_fill_color(22, 27, 34)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(139, 148, 158)
        for col, w in [("PORT", 25), ("PROTOCOL", 30), ("SERVICE", 50), ("VERSION", 85)]:
            pdf.cell(w, 6, col, fill=True)
        pdf.ln(7)
        for i, port in enumerate(open_ports):
            pdf.set_fill_color(22, 27, 34) if i % 2 == 0 else pdf.set_fill_color(13, 17, 23)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(0, 255, 136)
            pdf.cell(25, 6, clean(str(port.get("port", ""))), fill=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(240, 246, 252)
            pdf.cell(30, 6, clean(port.get("protocol", "")).upper(), fill=True)
            pdf.cell(50, 6, clean(port.get("service", "")), fill=True)
            pdf.set_text_color(139, 148, 158)
            pdf.cell(85, 6, clean(port.get("version", ""))[:40], fill=True)
            pdf.ln(6)
    else:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(139, 148, 158)
        pdf.cell(0, 6, "No open ports detected.")
        pdf.ln(8)
    pdf.ln(4)

    # -- 4. Vulnerability Findings --
    pdf.section_title("4. VULNERABILITY FINDINGS")

    if not findings:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(139, 148, 158)
        pdf.cell(0, 6, "No vulnerabilities found.")
        pdf.ln(8)
    else:
        for finding in findings:
            severity = finding.get("severity", "Informational")
            color = pdf.severity_color(severity)
            name = finding.get("name", "")

            remediation_steps = REMEDIATION_DETAIL.get(name, REMEDIATION_DETAIL["default"])

            card_height = 70 + (len(remediation_steps) * 6)
            if pdf.get_y() + card_height > 265:
                pdf.add_page()
                pdf.set_fill_color(13, 17, 23)
                pdf.rect(0, 0, 210, 297, 'F')

            card_y = pdf.get_y()

            # Card background
            pdf.set_fill_color(22, 27, 34)
            pdf.set_draw_color(*color)
            pdf.set_line_width(0.3)
            pdf.rect(10, card_y, 190, card_height, 'FD')

            # Left accent bar
            pdf.set_fill_color(*color)
            pdf.rect(10, card_y, 2, card_height, 'F')

            # Finding ID + badge + CVSS
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(139, 148, 158)
            pdf.set_xy(14, card_y + 2)
            pdf.cell(0, 4, clean(finding.get("id", "")))
            pdf.badge(155, card_y + 2, severity, color)

            cvss = finding.get("cvss_score")
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*color)
            pdf.set_xy(178, card_y + 1)
            pdf.cell(20, 6, f"{cvss:.1f}" if cvss is not None else "N/A", align="R")

            # Finding name
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(240, 246, 252)
            pdf.set_xy(14, card_y + 8)
            pdf.cell(140, 6, clean(name)[:65])

            # Category
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(139, 148, 158)
            pdf.set_xy(14, card_y + 15)
            pdf.cell(0, 5, clean(finding.get("category", "")))

            # Divider
            pdf.set_draw_color(48, 54, 61)
            pdf.set_line_width(0.2)
            pdf.line(14, card_y + 22, 198, card_y + 22)

            current_y = card_y + 25

            # Affected URL
            pdf.set_xy(14, current_y)
            pdf.labeled_field(
                "OPEN PORT:",
                clean(str(finding.get("affected_url", "N/A"))),
                (0, 255, 136),
                (14, 165, 233)
            )
            current_y += 7

            # Evidence
            evidence = finding.get("evidence", "")
            if evidence:
                pdf.set_xy(14, current_y)
                pdf.labeled_field(
                    "EVIDENCE:",
                    clean(str(evidence))[:85],
                    (249, 168, 37),
                    (249, 200, 100)
                )
                current_y += 7

            # Remediation header
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(0, 255, 136)
            pdf.set_xy(14, current_y)
            pdf.cell(0, 5, "REMEDIATION STEPS:")
            current_y += 7

            # Remediation steps
            for step in remediation_steps:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(200, 210, 200)
                pdf.set_xy(16, current_y)
                pdf.cell(4, 5, "-")
                pdf.set_xy(20, current_y)
                pdf.cell(0, 5, clean(step)[:95])
                current_y += 6

            pdf.ln(card_height + 6)

    # Save
    pdf.output(OUTPUT_PATH)
    print(f"[REPORT] Enhanced PDF saved to: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generate_report()