import subprocess
import requests
import random
import time
import dns.resolver
import uuid

# --- CONFIGURATION ---
DNS_SERVERS = {
    "OpenDNS": "208.67.222.222", 
    "Google": "8.8.8.8"           
}

DNS_TEST_DOMAINS = {
    "OpenDNS_Targets": ["example.com", "mytest.org", "internal-dev.net"], 
    "Google_Blocked": ["msn.com", "yahoo.com"],
    "Google_Allowed": ["github.com", "stackoverflow.com", "python.org"]
}

BLOCKED_WEB = {
    "Specific_Sites": ["https://www.ebay.com", "https://www.wikipedia.org"],
    "France_GeoIP": [
        "https://www.lemonde.fr", "https://www.lefigaro.fr", 
        "https://www.bnf.fr", "https://www.service-public.fr"
    ],
    "China_GeoIP": [
        "https://www.baidu.com", "https://www.taobao.com", "https://www.qq.com"
    ]
}

ALLOWED_WEB = [
    "https://www.facebook.com", "https://www.instagram.com", "https://www.reddit.com",
    "https://www.bbc.com", "https://www.asahi.com", "https://www.globo.com"
]

# CACHELESS HEADERS
# Pragma and Cache-Control: no-cache tell the network to ignore any cached copies
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

def log(category, target, result):
    print(f"[{time.strftime('%H:%M:%S')}] {category:15} | {target:30} | {result}")

def test_dns_cacheless(server_ip, domain):
    # This bypasses Ubuntu's systemd-resolved and talks directly to the IP
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.cache = None  # Explicitly disable internal library caching
    resolver.timeout = 2
    resolver.lifetime = 2
    try:
        resolver.resolve(domain, 'A')
        status = "ALLOWED"
    except:
        status = "BLOCKED"
    log(f"DNS (@{server_ip})", domain, status)

def run_suite():
    print("=== STARTING CACHELESS FIREWALL TEST ===\n")

    # 1. DNS PHASE (Direct Socket)
    print("--- Phase 1: DNS Lookups (Bypassing System Cache) ---")
    for d in DNS_TEST_DOMAINS["OpenDNS_Targets"]:
        test_dns_cacheless(DNS_SERVERS["OpenDNS"], d)
    for d in DNS_TEST_DOMAINS["Google_Blocked"] + DNS_TEST_DOMAINS["Google_Allowed"]:
        test_dns_cacheless(DNS_SERVERS["Google"], d)

    # 2. WEB PHASE (With Cache-Busting)
    print("\n--- Phase 2 & 3: Web Targets (Cache-Busting Enabled) ---")
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Combine all sites for a varied run
    all_sites = []
    for cat in BLOCKED_WEB: all_sites.extend(BLOCKED_WEB[cat])
    all_sites.extend(ALLOWED_WEB)
    random.shuffle(all_sites)

    for url in all_sites:
        # Cache Buster: Append a unique ID to the URL so the firewall sees a new request
        cache_buster = f"?cb={uuid.uuid4().hex[:8]}"
        test_url = url + cache_buster
        
        try:
            # We don't use a persistent session for TCP to force new handshakes
            resp = requests.get(test_url, headers=HEADERS, timeout=4)
            log("WEB_TEST", url, f"ALLOWED ({resp.status_code})")
        except:
            log("WEB_TEST", url, "BLOCKED")
        time.sleep(random.uniform(0.5, 1.2))

if __name__ == "__main__":
    run_suite()
