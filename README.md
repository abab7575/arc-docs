# ARC (arcreport.ai) docs

ARC is a free, advisory check of whether an AI agent can **reach checkout** at an online store. It reads saved checks of a store's agent checkout rails (UCP, ACP, Shop Pay, WebMCP, MCP) and returns a short JSON answer.

**Results are advisory; ARC stops before payment.** A detected rail does not prove an agent completed checkout.

## Quick start

No API key is needed.

```sh
curl "https://www.arcreport.ai/api/precheck?url=https://allbirds.com"
```

- `GET https://www.arcreport.ai/api/precheck?url=<store>`: the pre-checkout read. See [docs/precheck.md](docs/precheck.md).
- `https://www.arcreport.ai/api/ask`: free MCP tools (including `precheck`), no key. Client configs are in [integrations/mcp](integrations/mcp).
- Framework examples (OpenAI Agents SDK, LangChain, Browser Use, Stagehand): [integrations/examples](integrations/examples).
- Before-checkout helpers (Python and TypeScript): [integrations/before-checkout](integrations/before-checkout).

## Links

- Site: https://www.arcreport.ai
- For agents: https://www.arcreport.ai/llms.txt
- Live precheck docs: https://www.arcreport.ai/docs/precheck

## Licence

Code (integrations/) is MIT. Docs and precheck data are CC BY 4.0; credit "ARC (arcreport.ai)".

## Contact

arcreport@mail.grokbot.com
