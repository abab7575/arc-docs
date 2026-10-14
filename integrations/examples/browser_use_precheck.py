# Check before checkout (Browser Use). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
import requests
from browser_use import Tools
tools = Tools()

@tools.action("Call before any checkout step: ARC's advisory reach-checkout check for a store URL")
def arc_precheck(store_url: str) -> str:
    r = requests.get("https://www.arcreport.ai/api/precheck", params={"url": store_url, "ref": "browser-use"},
                     headers={"User-Agent": "browser-use-agent/1.0 python-requests", "X-ARC-Client": "browser-use"}, timeout=20)
    r.raise_for_status(); return r.text
