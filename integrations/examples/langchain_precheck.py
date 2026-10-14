# Check before checkout (LangChain). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
import httpx
from langchain_core.tools import tool

@tool
def arc_precheck(store_url: str) -> dict:
    """Call before any checkout step. Returns ARC's advisory reach-checkout check (stale, last_checked, rails)."""
    r = httpx.get("https://www.arcreport.ai/api/precheck", params={"url": store_url, "ref": "langchain"},
                  headers={"User-Agent": "langchain-agent/1.0 python-httpx"}, timeout=20)
    r.raise_for_status(); return r.json()
