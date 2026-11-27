# AEGIS - Automated Network Vulnerability Scanner

AEGIS runs the whole vulnerability assessment pipeline from one place: Nmap network scanning, OWASP Top 10 (2021) web testing, CVSS v3.1 scoring and PDF report generation. A Flask backend exposes a REST API, and a Next.js dashboard shows live scan progress and results.

Built as a B.Tech Cybersecurity and Digital Forensics mini project.

> **Authorized use only.** AEGIS sends real scan traffic and attack-style probes (SQL injection and XSS payloads, default credential checks, SSRF vectors). Run it only against systems you own or have written permission to test. Safe legal targets are `scanme.nmap.org` (keep scans light, per the Nmap project's rules), your own `127.0.0.1`, and deliberately vulnerable labs such as DVWA or WebGoat.

## Features

- Nmap scanning: open ports, services and versions, OS detection, hostname and MAC address, with custom Nmap flags.
- OWASP Top 10 (2021) testing using HTTP probing and response parsing.
- CVSS v3.1 score for every finding, plus a weighted overall risk score per scan.
- Live scan terminal view, polled from the backend every 2 seconds.
- Dashboard with summary cards, severity donut chart, ports table and an expandable findings table (evidence and remediation per finding).
- One-click PDF report download.
- Nmap cheatsheet panel on the scan page.
- Single-command startup: `python main.py` launches both servers.

## Repository layout

```text
aegis-scanner/
|-- aegis-backend/
|   |-- main.py             entry point: starts Flask and Next.js, or scans from the CLI
|   |-- app.py              Flask server and API routes
|   |-- requirements.txt    Python dependencies
|   |-- scanner/            nmap_scan.py, owasp_tests.py
|   |-- scoring/            cvss_score.py
|   |-- output/             report.py (PDF generator)
|   |-- templates/          Flask HTML pages (base, index, scanning, results)
|   `-- static/             css/style.css, js/matrix.js
|-- aegis-frontend/         Next.js 15 dashboard (TypeScript, Tailwind CSS)
|   |-- app/                pages (home, scan, dashboard) and API routes (results, report)
|   |-- components/         Sidebar, Header, TopCards, Charts, PortsTable, FindingsTable
|   |-- data/               sample results.json
|   |-- hooks/, lib/        shared helpers
|   `-- package.json, .env.example, config files
|-- .gitignore
|-- LICENSE
`-- README.md
```

Scan results are written to `aegis-backend/results.json` at run time (it is not committed).

## Requirements

| Tool | Version |
|---|---|
| Python | 3.10 or newer |
| Node.js | 18 or newer (20 LTS recommended) |
| Nmap | Installed on the system and available on `PATH` ([nmap.org/download](https://nmap.org/download.html)) |
| Git | Any recent version |

Tested on Windows 10/11 and Ubuntu 20.04/22.04. The Python packages are Flask, Flask-CORS, python-nmap, requests, BeautifulSoup4, cvss, FPDF2 and Matplotlib; `pip` installs them from `requirements.txt`.

## Download and run

**1. Clone the repository**

```bash
git clone https://github.com/paradoxialcode/aegis-scanner.git
cd aegis-scanner
```

If the repository is private you need access to it. Git will ask you to sign in with your GitHub account.

**2. Install the backend dependencies**

A virtual environment keeps them separate from your other projects.

Windows (PowerShell):

```powershell
cd aegis-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux or macOS:

```bash
cd aegis-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Install the frontend dependencies**

```bash
cd ../aegis-frontend
npm install
```

**4. Start AEGIS**

```bash
cd ../aegis-backend
python main.py
```

This starts the Flask backend on `http://127.0.0.1:5000` and the Next.js frontend on `http://localhost:3000`. Press `Ctrl+C` to stop both.

**5. Run a scan**

1. Open `http://localhost:3000`.
2. Click **START NEW SCAN**.
3. Enter a target IP or hostname (for example `scanme.nmap.org`) and, optionally, custom Nmap flags.
4. Click **EXECUTE SCAN** and wait for it to finish.
5. Open the **Dashboard** to see the results.
6. Click **Generate Report** to download the PDF.

### Command-line mode

```bash
python main.py scanme.nmap.org               # scan from the terminal
python main.py scanme.nmap.org --skip-owasp  # network scan only
python main.py scanme.nmap.org --no-pdf      # skip PDF generation
```

### Testing the OWASP module against DVWA

1. Install XAMPP and start Apache and MySQL.
2. Place DVWA in `htdocs/dvwa`.
3. Open `http://localhost/dvwa/setup.php` and create the database.
4. Log in with the default DVWA credentials (`admin` / `password`).
5. Scan `http://localhost/dvwa` from AEGIS.

DVWA is intentionally vulnerable. Run it on localhost only and never expose it to a network.

## API

| Method | Route | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/scan` | Start a scan (JSON body: `target`, `flags`); returns `202 Accepted` |
| GET | `/api/scan_status` | Live scan progress (polling endpoint) |
| GET | `/api/results` | Full scan results as JSON |
| GET | `/api/report/latest` | Download the generated PDF report |

The API has no authentication. It is meant to run on your own machine, so keep it bound to `127.0.0.1`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `nmap program was not found in path` | Install Nmap and reopen the terminal so `PATH` updates. Check with `nmap --version`. |
| OS detection returns nothing | Nmap needs elevated rights for `-O`. Run the terminal as Administrator (Windows) or with `sudo` (Linux). |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again. |
| Port 3000 or 5000 already in use | Stop the other program using it, then start AEGIS again. |
| Frontend does not start | Run `npm install` inside `aegis-frontend` and confirm `node --version` is 18 or newer. |

## Team

| Member | Area |
|---|---|
| Maitrey Suthar | Project lead, Nmap scanner, Flask API, integration (`nmap_scan.py`, `main.py`, `app.py`) |
| Aditya Vishwakarma | OWASP testing engine (`owasp_tests.py`) |
| Ashish Yadav | CVSS scoring and data (`cvss_score.py`, `results.json`) |
| Omkar Jaiswal | Dashboard and PDF report (Next.js frontend, `report.py`) |


## License

Released under the [MIT License](LICENSE).

## Acknowledgements

Nmap, the OWASP Top 10, the CVSS standard (FIRST.org), and the Python and Next.js ecosystems.
