# Check before checkout (OpenAI Agents SDK). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
import httpx
from agents import function_tool

@function_tool
def arc_precheck(store_url: str) -> dict:
    """Call before any checkout step. Returns ARC's advisory reach-checkout check (stale, last_checked, rails)."""
    r = httpx.get("https://www.arcreport.ai/api/precheck", params={"url": store_url, "ref": "openai-agents"},
                  headers={"User-Agent": "openai-agents/1.0 python-httpx"}, timeout=20)
    r.raise_for_status(); return r.json()
