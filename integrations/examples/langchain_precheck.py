# Check before checkout (LangChain). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
# On any error or timeout, treat the store as unknown, not as no.
import httpx
from urllib.parse import urlsplit
from langchain_core.tools import tool

@tool
def arc_precheck(store_url: str) -> dict:
    """Call before any checkout step. Returns ARC's advisory reach-checkout check (stale, last_checked, rails)."""
    p = urlsplit(store_url); origin = f"{p.scheme}://{p.netloc}"  # send the store origin only, not the product URL
    r = httpx.get("https://www.arcreport.ai/api/precheck", params={"url": origin, "ref": "int-langchain-py"},
                  headers={"User-Agent": "langchain-agent/1.0 python-httpx", "X-ARC-Client": "int-langchain-py"}, timeout=10)
    r.raise_for_status(); return r.json()
