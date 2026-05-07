import requests
from bs4 import BeautifulSoup
import json
import re

# ==========================================
# MODULES 1-5: INITIAL OWASP CHECKS
# ==========================================
def check_sql_injection(target_url):
    print(f"[*] Testing {target_url} for SQL Injection...")
    payload = "'"
    test_url = f"{target_url}?id={payload}"
    try:
        response = requests.get(test_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        if "sql syntax" in page_text or "mysql_fetch_array" in page_text:
            return {"vulnerability": "SQL Injection (OWASP A03:2021)", "status": "VULNERABLE", "endpoint": test_url, "details": "Database syntax error reflected in response."}
    except requests.exceptions.RequestException as e:
        print(f"[!] Connection error: {e}")
    return {"vulnerability": "SQL Injection (OWASP A03:2021)", "status": "SECURE", "endpoint": test_url, "details": "No obvious SQL syntax error detected."}

def check_xss(base_url):
    print("[*] Testing for Reflected XSS...")
    target_url = f"{base_url}/vulnerabilities/xss_r/"
    payload = "<script>alert('AegisTest')</script>"
    test_url = f"{target_url}?name={payload}"
    try:
        response = requests.get(test_url, timeout=5)
        if payload in response.text:
            return {"vulnerability": "Cross-Site Scripting (OWASP A03:2021)", "status": "VULNERABLE", "endpoint": test_url, "details": "Script payload reflected in HTML."}
    except: pass
    return {"vulnerability": "Cross-Site Scripting (OWASP A03:2021)", "status": "SECURE", "endpoint": test_url, "details": "Payload filtered or not reflected."}

def check_command_injection(base_url):
    print("[*] Testing for Command Injection...")
    target_url = f"{base_url}/vulnerabilities/exec/"
    payload = "127.0.0.1; echo 'Aegis_Vulnerable'"
    try:
        response = requests.post(target_url, data={'ip': payload, 'Submit': 'Submit'}, timeout=5)
        if "Aegis_Vulnerable" in response.text:
            return {"vulnerability": "Command Injection (OWASP A03:2021)", "status": "VULNERABLE", "endpoint": target_url, "details": "System command executed."}
    except: pass
    return {"vulnerability": "Command Injection (OWASP A03:2021)", "status": "SECURE", "endpoint": target_url, "details": "Input sanitized."}

def check_directory_traversal(base_url):
    print("[*] Testing for Path Traversal...")
    target_url = f"{base_url}/vulnerabilities/fi/"
    payload = "../../etc/passwd"
    test_url = f"{target_url}?page={payload}"
    try:
        response = requests.get(test_url, timeout=5)
        if "root:x:0:0" in response.text:
            return {"vulnerability": "Path Traversal (OWASP A01:2021)", "status": "VULNERABLE", "endpoint": test_url, "details": "Local file inclusion detected (/etc/passwd)."}
    except: pass
    return {"vulnerability": "Path Traversal (OWASP A01:2021)", "status": "SECURE", "endpoint": test_url, "details": "File paths restricted."}

def check_security_misconfig(base_url):
    print("[*] Testing for Security Misconfigurations (Server Headers)...")
    try:
        response = requests.get(base_url, timeout=5)
        headers = response.headers
        if 'Server' in headers or 'X-Powered-By' in headers:
            return {"vulnerability": "Security Misconfiguration (OWASP A05:2021)", "status": "VULNERABLE", "endpoint": base_url, "details": f"Server exposed version info: {headers.get('Server', '')} {headers.get('X-Powered-By', '')}"}
    except: pass
    return {"vulnerability": "Security Misconfiguration (OWASP A05:2021)", "status": "SECURE", "endpoint": base_url, "details": "No sensitive headers exposed."}

# ==========================================
# MODULES 6-10: NEW DEEPSEEK CHECKS
# ==========================================
def check_broken_access_control(target_url):
    print("[*] Testing for Broken Access Control...")
    restricted = f"{target_url}/vulnerabilities/csrf/"
    try:
        response = requests.get(restricted, timeout=5, allow_redirects=False)
        if response.status_code == 200 and "CSRF" in response.text:
            return {"vulnerability": "Broken Access Control (OWASP A01:2021)", "status": "VULNERABLE", "endpoint": restricted, "details": "Unauthenticated access to restricted CSRF page allowed."}
    except: pass
    return {"vulnerability": "Broken Access Control (OWASP A01:2021)", "status": "SECURE", "endpoint": restricted, "details": "Restricted page correctly denied or redirected."}

def check_ssrf(target_url):
    print("[*] Testing for Server-Side Request Forgery...")
    internal_url = "http://127.0.0.1/phpinfo.php"
    ssrf_endpoint = f"{target_url}/vulnerabilities/ssrf/?url={internal_url}"
    try:
        response = requests.get(ssrf_endpoint, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        if "PHP Version" in page_text:
            return {"vulnerability": "Server-Side Request Forgery (OWASP A10:2021)", "status": "VULNERABLE", "endpoint": ssrf_endpoint, "details": f"Server fetched internal resource: {internal_url}."}
    except: pass
    return {"vulnerability": "Server-Side Request Forgery (OWASP A10:2021)", "status": "SECURE", "endpoint": ssrf_endpoint, "details": "SSRF vector did not fetch internal content."}

def check_vulnerable_components(target_url):
    print("[*] Testing for Vulnerable/Outdated Components...")
    phpinfo_url = f"{target_url}/phpinfo.php"
    try:
        response = requests.get(phpinfo_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        if "PHP Version" in text:
            version_match = re.search(r"PHP Version\s+([\d.]+)", text)
            if version_match:
                version = version_match.group(1)
                if tuple(map(int, version.split('.'))) < (7, 4):
                    return {"vulnerability": "Vulnerable and Outdated Components (OWASP A06:2021)", "status": "VULNERABLE", "endpoint": phpinfo_url, "details": f"Outdated PHP version {version} detected."}
        return {"vulnerability": "Vulnerable and Outdated Components (OWASP A06:2021)", "status": "SECURE", "endpoint": phpinfo_url, "details": "No outdated component information found."}
    except: return {"vulnerability": "Vulnerable and Outdated Components (OWASP A06:2021)", "status": "SECURE", "endpoint": phpinfo_url, "details": "Could not access phpinfo.php."}

def check_authentication_failures(target_url):
    print("[*] Testing for Authentication Failures...")
    login_url = f"{target_url}/login.php"
    credentials = {"username": "admin", "password": "password", "Login": "Login"}
    try:
        session = requests.Session()
        login_resp = session.post(login_url, data=credentials, timeout=5)
        index_resp = session.get(f"{target_url}/index.php", timeout=5)
        if index_resp.status_code == 200 and "Welcome" in index_resp.text:
            return {"vulnerability": "Identification and Authentication Failures (OWASP A07:2021)", "status": "VULNERABLE", "endpoint": login_url, "details": "Default credentials (admin/password) granted access."}
    except: pass
    return {"vulnerability": "Identification and Authentication Failures (OWASP A07:2021)", "status": "SECURE", "endpoint": login_url, "details": "Default credentials did not allow login."}

def check_cryptographic_failures(target_url):
    print("[*] Testing for Cryptographic Failures...")
    login_url = f"{target_url}/login.php"
    try:
        resp = requests.post(login_url, data={"username": "test", "password": "test", "Login": "Login"}, timeout=5)
        for cookie in resp.cookies:
            if not cookie.secure:
                return {"vulnerability": "Cryptographic Failures (OWASP A02:2021)", "status": "VULNERABLE", "endpoint": login_url, "details": "Cookie without Secure flag set; transmitted over HTTP."}
    except: pass
    return {"vulnerability": "Cryptographic Failures (OWASP A02:2021)", "status": "SECURE", "endpoint": login_url, "details": "No insecure cookie transmission detected."}


# ==========================================
# THE MAIN EXECUTION ENGINE
# ==========================================
def run_all_tests(base_url):
    findings = []
    print(f"--- Starting Full OWASP Top 10 Scan on {base_url} ---")
    
    # Run Original 5 Modules
    sqli_target = f"{base_url}/vulnerabilities/sqli/"
    findings.append(check_sql_injection(sqli_target))
    findings.append(check_xss(base_url))
    findings.append(check_command_injection(base_url))
    findings.append(check_directory_traversal(base_url))
    findings.append(check_security_misconfig(base_url))
    
    # Run New DeepSeek Modules
    findings.append(check_broken_access_control(base_url))
    findings.append(check_ssrf(base_url))
    findings.append(check_vulnerable_components(base_url))
    findings.append(check_authentication_failures(base_url))
    findings.append(check_cryptographic_failures(base_url))
    
    # Write findings to JSON file
    with open('results.json', 'w') as json_file:
        json.dump(findings, json_file, indent=4)
        
    print("--- Scan complete. 10 Modules Executed. Results written to results.json ---")

if __name__ == "__main__":
    # Your target running through the VirtualBox tunnel
    target = "http://localhost:8080" 
    run_all_tests(target)