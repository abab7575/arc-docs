# Check before checkout: ARC precheck examples

Each snippet calls `GET https://www.arcreport.ai/api/precheck?url=<store>&ref=<framework>` before an agent's checkout step.

**What the check proves:** it's advisory. It reports whether ARC's saved check found signs that an agent can **reach checkout** at that store (rails such as UCP, ACP, MCP and WebMCP), along with `last_checked` and `stale`. It doesn't prove an agent completed checkout. ARC stops before payment. Show `last_checked` to your user, and treat `stale: true` as unknown.

| File | Framework | User-Agent | ref |
|---|---|---|---|
| openai_agents_precheck.py | OpenAI Agents SDK | openai-agents/1.0 python-httpx | openai-agents |
| langchain_precheck.py | LangChain | langchain-agent/1.0 python-httpx | langchain |
| browser_use_precheck.py | Browser Use | browser-use-agent/1.0 python-requests | browser-use |
| stagehand_precheck.ts | Stagehand | stagehand-agent/1.0 undici | stagehand |

Install: `pip install httpx openai-agents` / `pip install httpx langchain-core` / `pip install browser-use` / Node 18+ (global fetch).
No API key is needed.
