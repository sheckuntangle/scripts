import subprocess
import requests
import random
import time
import dns.resolver
import uuid

# --- CONFIGURATION ---
# DNS Servers to test (Should be blocked)
DNS_SERVERS = {
    "OpenDNS": "208.67.222.222", 
    "Google": "8.8.8.8"           
}

# Domains to look up via specific servers
DNS_TEST_DOMAINS = {
    "OpenDNS_Targets": ["example.com", "mytest.org"], # internal-dev.net removed
    "Google_Blocked": ["msn.com", "yahoo.com"],
    "Google_Allowed": ["github.com", "stackoverflow.com", "python.org"]
}

# Anchor IPs: These are statically tied to specific countries in MaxMind
GEO_ANCHORS = {
    "China": ["114.114.114.114", "223.5.5.5", "183.60.15.245"],
    "France": ["194.2.0.20", "212.27.48.10", "51.15.0.1"]
}

# Standard URL Filtering Targets
WEB_BLOCKED = ["https://www.ebay.com", "https://www.wikipedia.org"]
WEB_ALLOWED = [
    "https://www.facebook.com", "https://www.instagram.com", "https://www.reddit.com",
    "https://www.bbc.com", "https://www.asahi.com", "https://www.globo.com",
    "https://www.nytimes.com", "https://www.amazon.com"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

def log(category, target, result):
    print(f"[{time.strftime('%H:%M:%S')}] {category:15} | {target:30} | {result}")

def test_dns_direct(server_ip, domain):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.cache = None
    resolver.timeout = 2
    resolver.lifetime = 2
    try:
        resolver.resolve(domain, 'A')
        log(f"DNS (@{server_ip})", domain, "ALLOWED")
    except:
        log(f"DNS (@{server_ip})", domain, "BLOCKED")

def run_test_suite():
    print("=== STARTING CACHELESS FIREWALL TEST SUITE ===\n")

    # 1. DNS PHASE
    print("--- Phase 1: DNS Filtering ---")
    for d in DNS_TEST_DOMAINS["OpenDNS_Targets"]:
        test_dns_direct(DNS_SERVERS["OpenDNS"], d)
    for d in DNS_TEST_DOMAINS["Google_Blocked"] + DNS_TEST_DOMAINS["Google_Allowed"]:
        test_dns_direct(DNS_SERVERS["Google"], d)

    # 2. GEO-IP ANCHOR PHASE
    print("\n--- Phase 2: Geo-IP (Direct IP Anchors) ---")
    for country, ips in GEO_ANCHORS.items():
        for ip in ips:
            try:
                # Using HTTP to the IP to trigger firewall inspection
                requests.get(f"http://{ip}", headers=HEADERS, timeout=3)
                log(f"GEO_{country}", ip, "ALLOWED")
            except:
                log(f"GEO_{country}", ip, "BLOCKED")

    # 3. WEB DOMAIN PHASE
    print("\n--- Phase 3: Web & URL Filtering ---")
    all_web = WEB_BLOCKED + WEB_ALLOWED
    random.shuffle(all_web)
    for url in all_web:
        # Cache-buster ensures the firewall sees a unique URI
        full_url = f"{url}?cb={uuid.uuid4().hex[:6]}"
        try:
            # New request object for every call (no session) for blank slate
            resp = requests.get(full_url, headers=HEADERS, timeout=4)
            log("WEB_FILTER", url, f"ALLOWED ({resp.status_code})")
        except:
            log("WEB_FILTER", url, "BLOCKED")
        time.sleep(random.uniform(0.5, 1.0))

if __name__ == "__main__":
    run_test_suite()
