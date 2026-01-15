import subprocess
import requests
import random
import time
import dns.resolver

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

# Targeted Block Categories
BLOCKED_WEB = {
    "Specific_Sites": ["https://www.ebay.com", "https://www.wikipedia.org"],
    "France_GeoIP": [
        "https://www.lemonde.fr", 
        "https://www.lefigaro.fr", 
        "https://www.bnf.fr", 
        "https://www.service-public.fr",
        "https://www.ameli.fr"
    ],
    "China_GeoIP": [
        "https://www.baidu.com", "https://www.taobao.com", "https://www.qq.com", 
        "https://www.sina.com.cn", "https://www.jd.com", "https://www.weibo.com"
    ]
}

# General Traffic for Reporting
ALLOWED_WEB = [
    "https://www.facebook.com", "https://www.instagram.com", "https://www.reddit.com",
    "https://www.bbc.com", "https://www.asahi.com", "https://www.globo.com",
    "https://www.nytimes.com", "https://www.amazon.com", "https://www.microsoft.com"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def log(category, target, result):
    print(f"[{time.strftime('%H:%M:%S')}] {category:15} | {target:30} | {result}")

def test_dns(server_ip, domain):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [server_ip]
    resolver.timeout = 2
    resolver.lifetime = 2
    try:
        resolver.resolve(domain, 'A')
        status = "ALLOWED"
    except:
        status = "BLOCKED"
    log(f"DNS (@{server_ip})", domain, status)

def run_suite():
    print("=== STARTING FIREWALL TEST (FRANCE/CHINA/DNS/WEB) ===\n")

    # 1. DNS PHASE
    print("--- Phase 1: DNS Lookups ---")
    for d in DNS_TEST_DOMAINS["OpenDNS_Targets"]:
        test_dns(DNS_SERVERS["OpenDNS"], d)
    for d in DNS_TEST_DOMAINS["Google_Blocked"] + DNS_TEST_DOMAINS["Google_Allowed"]:
        test_dns(DNS_SERVERS["Google"], d)

    # 2. WEB PHASE (Blocked & GeoIP)
    print("\n--- Phase 2: Blocked/GeoIP Web Targets ---")
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Flatten all blocked categories
    blocked_pool = BLOCKED_WEB["Specific_Sites"] + BLOCKED_WEB["France_GeoIP"] + BLOCKED_WEB["China_GeoIP"]
    for url in blocked_pool:
        try:
            session.get(url, timeout=3)
            log("WEB_BLOCK_TEST", url, "FAIL (Got Through)")
        except:
            log("WEB_BLOCK_TEST", url, "SUCCESS (Blocked)")

    # 3. WEB PHASE (Allowed Noise)
    print("\n--- Phase 3: Allowed Traffic Generation ---")
    random.shuffle(ALLOWED_WEB)
    for url in ALLOWED_WEB:
        try:
            time.sleep(random.uniform(0.5, 1.5))
            resp = session.get(url, timeout=5)
            log("WEB_ALLOWED", url, f"OK ({resp.status_code})")
        except:
            log("WEB_ALLOWED", url, "FAILED")

if __name__ == "__main__":
    run_suite()
