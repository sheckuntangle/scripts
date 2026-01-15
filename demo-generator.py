import subprocess
import requests
import random
import time
import dns.resolver
import uuid

# --- CONFIGURATION ---
# Basic ICMP Targets
PING_TARGETS = {
    "Blocked": "9.9.9.9",
    "Allowed": "8.8.8.8"
}

# DNS Servers to test
DNS_SERVERS = {
    "OpenDNS": "208.67.222.222", 
    "Google": "8.8.8.8"           
}

# Domains to look up via specific servers
DNS_TEST_DOMAINS = {
    "OpenDNS_Targets": ["example.com", "mytest.org"],
    "Google_Blocked": ["msn.com", "yahoo.com"],
    "Google_Allowed": ["github.com", "stackoverflow.com", "python.org"]
}

# Anchor IPs for Geo-IP (Statically tied to these countries)
GEO_ANCHORS = {
    "China": ["114.114.114.114", "223.5.5.5", "183.60.15.245"],
    "France": ["194.2.0.20", "212.27.48.10", "51.15.0.1"]
}

# URL Filtering Targets
WEB_BLOCKED = ["https://www.ebay.com", "https://www.wikipedia.org"]
WEB_ALLOWED = [
    "https://www.facebook.com", "https://www.instagram.com", "https://www.reddit.com",
    "https://www.bbc.com", "https://www.asahi.com", "https://www.globo.com"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache"
}

def log(category, target, result):
    print(f"[{time.strftime('%H:%M:%S')}] {category:15} | {target:30} | {result}")

def run_ping(host):
    # Sends 1 packet with a 1-second timeout
    res = subprocess.run(["ping", "-c", "1", "-W", "1", host], capture_output=True)
    return "REACHABLE" if res.returncode == 0 else "BLOCKED/TIMEOUT"

def test_dns_direct(server_ip, domain):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.timeout = 2
    try:
        resolver.resolve(domain, 'A')
        log(f"DNS (@{server_ip})", domain, "ALLOWED")
    except:
        log(f"DNS (@{server_ip})", domain, "BLOCKED")

def run_test_suite():
    print("=== STARTING FULL FIREWALL VALIDATION SUITE ===\n")

    # 1. INITIAL PING PHASE
    print("--- Phase 1: Basic ICMP Pings ---")
    log("PING (Rule Test)", PING_TARGETS["Blocked"], run_ping(PING_TARGETS["Blocked"]))
    log("PING (Rule Test)", PING_TARGETS["Allowed"], run_ping(PING_TARGETS["Allowed"]))

    # 2. DNS PHASE
    print("\n--- Phase 2: DNS Filtering ---")
    for d in DNS_TEST_DOMAINS["OpenDNS_Targets"]:
        test_dns_direct(DNS_SERVERS["OpenDNS"], d)
    for d in DNS_TEST_DOMAINS["Google_Blocked"] + DNS_TEST_DOMAINS["Google_Allowed"]:
        test_dns_direct(DNS_SERVERS["Google"], d)

    # 3. GEO-IP ANCHOR PHASE (Ping + HTTP)
    print("\n--- Phase 3: Geo-IP Anchors (ICMP & TCP) ---")
    for country, ips in GEO_ANCHORS.items():
        for ip in ips:
            # Check ICMP for Geo-Block
            p_status = run_ping(ip)
            log(f"GEO_{country}_ICMP", ip, p_status)
            
            # Check HTTP for Geo-Block
            try:
                requests.get(f"http://{ip}", headers=HEADERS, timeout=2)
                log(f"GEO_{country}_HTTP", ip, "ALLOWED")
            except:
                log(f"GEO_{country}_HTTP", ip, "BLOCKED")

    # 4. WEB DOMAIN PHASE
    print("\n--- Phase 4: URL Filtering (Cacheless) ---")
    all_web = WEB_BLOCKED + WEB_ALLOWED
    random.shuffle(all_web)
    for url in all_web:
        full_url = f"{url}?cb={uuid.uuid4().hex[:6]}"
        try:
            resp = requests.get(full_url, headers=HEADERS, timeout=4)
            log("WEB_FILTER", url, f"ALLOWED ({resp.status_code})")
        except:
            log("WEB_FILTER", url, "BLOCKED")

if __name__ == "__main__":
    run_test_suite()
