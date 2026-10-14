# Check before checkout (Browser Use). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
# On any error or timeout, treat the store as unknown, not as no.
import requests
from urllib.parse import urlsplit
from browser_use import Tools
tools = Tools()

@tools.action("Call before any checkout step: ARC's advisory reach-checkout check for a store URL")
def arc_precheck(store_url: str) -> str:
    p = urlsplit(store_url); origin = f"{p.scheme}://{p.netloc}"  # send the store origin only, not the product URL
    r = requests.get("https://www.arcreport.ai/api/precheck", params={"url": origin, "ref": "browser-use"},
                     headers={"User-Agent": "browser-use-agent/1.0 python-requests", "X-ARC-Client": "browser-use"}, timeout=10)
    r.raise_for_status(); return r.text
