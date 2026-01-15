import subprocess
import requests
import random
import time
import dns.resolver
import uuid
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
PING_TARGETS = {"Blocked": "9.9.9.9", "Allowed": "8.8.8.8"}
DNS_SERVERS = {"OpenDNS": "208.67.222.222", "Google": "8.8.8.8"}

# Static Geo-IP Anchors (Ensures specific country flags in logs)
GEO_ANCHORS = {
    "China": ["114.114.114.114", "223.5.5.5", "183.60.15.245"],
    "France": ["194.2.0.20", "212.27.48.10", "51.15.0.1"]
}

# Regional Web Pools (Global Diversity)
GLOBAL_WEB_POOL = {
    "North_America": ["https://www.google.com", "https://www.amazon.com", "https://www.nytimes.com", "https://www.cnn.com", "https://www.homedepot.com"],
    "South_America": ["https://www.globo.com", "https://www.mercadolivre.com.br", "https://www.uol.com.br", "https://www.infobae.com"],
    "Europe": ["https://www.bbc.co.uk", "https://www.spiegel.de", "https://www.elpais.com", "https://www.corriere.it", "https://www.rtve.es", "https://www.heise.de"],
    "Asia_Pacific": ["https://www.asahi.com", "https://www.naver.com", "https://www.rakuten.co.jp", "https://www.indiatimes.com", "https://www.canva.com", "https://www.shopee.tw"],
    "Middle_East_Africa": ["https://www.aljazeera.com", "https://www.news24.com", "https://www.kuna.net.kw", "https://www.yallakora.com"],
    "Social_Tech": ["https://www.facebook.com", "https://www.instagram.com", "https://www.reddit.com", "https://www.linkedin.com", "https://www.github.com", "https://www.netflix.com"]
}

WEB_BLOCKED = ["https://www.ebay.com", "https://www.wikipedia.org"]

# Assets to generate multiple 443 hits per domain
SUB_ASSETS = ["/favicon.ico", "/robots.txt", "/sitemap.xml", "/apple-touch-icon.png"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive"
}

def log(category, target, result):
    print(f"[{time.strftime('%H:%M:%S')}] {category:15} | {target:35} | {result}")

def fetch_realistic_site(url):
    """Simulates a browser loading a page + its assets to generate multiple 443 logs."""
    try:
        with requests.Session() as s:
            s.headers.update(HEADERS)
            # 1. Main Page Hit
            cb = f"?cb={uuid.uuid4().hex[:6]}"
            s.get(url + cb, timeout=6)
            log("443_HTTPS", url, "MAIN PAGE OK")
            
            # 2. Asset Multiplier (Generates 3 more logs for the same domain)
            for asset in random.sample(SUB_ASSETS, 3): 
                time.sleep(random.uniform(0.1, 0.5))
                s.get(url + asset, timeout=4)
                log("443_HTTPS_ASSET", f"{url}{asset}", "ASSET OK")
    except Exception:
        log("443_HTTPS", url, "BLOCKED/TIMEOUT")

def run_test_suite():
    print("=== STARTING GLOBAL HIGH-VOLUME TRAFFIC GENERATOR ===\n")

    # 1. Pings
    for ip in ["9.9.9.9", "8.8.8.8"]:
        res = subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True)
        log("ICMP", ip, "REACHABLE" if res.returncode == 0 else "BLOCKED")

    # 2. DNS Lookups
    resolver = dns.resolver.Resolver(configure=False)
    for s_name, s_ip in DNS_SERVERS.items():
        resolver.nameservers = [s_ip]
        for d in ["microsoft.com", "yahoo.com"]:
            try:
                resolver.resolve(d, 'A')
                log(f"DNS (@{s_ip})", d, "ALLOWED")
            except:
                log(f"DNS (@{s_ip})", d, "BLOCKED")

    # 3. Web Phase (Heavy Multi-Threading)
    all_sites = WEB_BLOCKED.copy()
    for region in GLOBAL_WEB_POOL:
        all_sites.extend(GLOBAL_WEB_POOL[region])
    
    random.shuffle(all_sites)

    print(f"\n--- Launching {len(all_sites)} Global Targets (Approx {len(all_sites)*4} HTTPS Events) ---")
    
    # max_workers=5 simulates 5 users browsing simultaneously
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(fetch_realistic_site, all_sites)

if __name__ == "__main__":
    run_test_suite()
