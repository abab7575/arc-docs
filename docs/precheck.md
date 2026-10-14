# Pre-checkout read: `GET /api/precheck`

Ask whether ARC already knows if an agent can **reach checkout** at a store. The answer is built from saved checks. ARC does not fetch that URL and does not start a scan.

Results are advisory; ARC stops before payment. A detected rail does not prove an agent completed checkout. `reachable_checkout` is true only when a saved check returned a checkout link. The saved result is ARC's automated check, not a live agent purchase or session.

Live version: https://www.arcreport.ai/docs/precheck

## Request

```
GET https://www.arcreport.ai/api/precheck?url=<product or store URL>
```

- `http` and `https` URLs only. Pass a full URL such as `https://allbirds.com`; a bare hostname returns `{"error": "Pass an http(s) product or store URL."}`.
- No API key.
- The same read is the `precheck` tool on the MCP endpoint `https://www.arcreport.ai/api/ask`. (`https://www.arcreport.ai/api/mcp` does not serve this tool.)

```sh
curl -sD - "https://www.arcreport.ai/api/precheck?url=https://allbirds.com/products/shoe"
```

## Response fields

| Field | Meaning |
|---|---|
| `host` | Hostname, lowercased, without a leading `www` or trailing dot. A subdomain can resolve to the registrable host ARC already lists (e.g. `shop.example.co.uk` → `example.co.uk`). |
| `last_checked` | ISO time of the saved check. `null` when there is none. |
| `checked_ago` | Coarse age of `last_checked`, e.g. "3 hours ago". "never checked" when the time is missing or unparseable. |
| `stale` | `true` when `last_checked` is 24 hours old or older, or missing. `false` only when the saved check is newer than 24 hours. Always present. Treat `stale: true` as unknown. |
| `known` | `true` when ARC's public catalog, a saved rails check, or directory check history has this host. `false` for a host ARC has not published (including stores that opted out). |
| `reachable_checkout` | `true` when a saved check returned a checkout link, `false` when that check finished without one, `null` when ARC has no completed check. |
| `rails` | Array of `{name, status, proves}` for UCP, ACP, Shop Pay, WebMCP and MCP. `Checkout WebMCP` is included when a saved Shopify reading exists. `null` when `known` is false. |
| `rails[].proves` | A sentence describing what that saved status records. Every one includes "Does not prove an agent completed checkout." |
| `blockers` | Standard sentences for a saved block. Empty when nothing blocked the check. `null` when `known` is false. |
| `confidence` | `high` (completed check in the last 7 days), `medium` (last 30 days), `low` (older or failed evidence), `none` (no evidence). |
| `report_outcome` | `https://www.arcreport.ai/docs/outcome-report`: where to report one checkout attempt. |
| `source` | `ARC (arcreport.ai)` |
| `licence` | `CC BY 4.0` |
| `scan_url` | Link to the free scan page when the host is unknown. `null` when `known` is true. Opening this API does not run the scan. |
| `lastReachableCheck` | Optional. A separate, newer plain-HTTP check: `{checkedAt, proves, evidenceLevel: "http-only"}`. It does not re-verify the checkout link or rails. Absent when there is no such check. |
| `reachability_stale` | Optional. `true` when `lastReachableCheck` is 24 hours old or older, or its time is missing. Absent when `lastReachableCheck` is absent. Does not change `stale`. |

## Example response

A real response for `https://www.allbirds.com` on 14 Oct 2026 (values change as stores are re-checked):

```json
{
  "host": "allbirds.com",
  "last_checked": "2026-10-14T14:11:51.000Z",
  "checked_ago": "2 hours ago",
  "stale": false,
  "known": true,
  "reachable_checkout": true,
  "rails": [
    { "name": "UCP", "status": "valid", "proves": "The saved check found a UCP profile that passed validation. That alone does not show an agent can reach checkout. Does not prove an agent completed checkout." },
    { "name": "ACP", "status": "not_found", "proves": "The saved check did not find an ACP signal. Does not prove an agent completed checkout." },
    { "name": "Shop Pay", "status": "detected", "proves": "The saved UCP file listed a Shop Pay payment handler. Does not prove an agent completed checkout." },
    { "name": "WebMCP", "status": "yes", "proves": "The saved check detected Shopify's WebMCP adapter in storefront HTML. That is not a live browser session. Does not prove an agent completed checkout." },
    { "name": "MCP", "status": "yes", "proves": "The saved check got an answer from a storefront or UCP MCP endpoint. Does not prove an agent completed checkout." },
    { "name": "Checkout WebMCP", "status": "detected", "proves": "The saved Shopify checkout HTML declared Checkout WebMCP tools. Buyer approval is still required. No order is placed. Does not prove an agent completed checkout." }
  ],
  "blockers": [],
  "confidence": "high",
  "source": "ARC (arcreport.ai)",
  "licence": "CC BY 4.0",
  "report_outcome": "https://www.arcreport.ai/docs/outcome-report",
  "scan_url": null,
  "lastReachableCheck": {
    "checkedAt": "2026-10-14T11:28:00.400Z",
    "proves": "HTTP reachable; robots allows ARCbot; platform=shopify detected from homepage; no checkout tested",
    "evidenceLevel": "http-only"
  },
  "reachability_stale": false
}
```

## Caching

Successful responses send `Cache-Control: public, s-maxage=300, stale-while-revalidate=86400`. Cache one answer per host on your side too; the helpers in `integrations/before-checkout` keep one for 24 hours.

## Rate limit

60 requests a minute per network. Request 61 in that minute gets status 429 with a `Retry-After` header. Respect it; don't retry in a loop.

## Privacy

A successful answer increments a daily total for that host. The raw client address and user agent are not stored.

## Licence

The JSON is CC BY 4.0. Credit "ARC (arcreport.ai)".
