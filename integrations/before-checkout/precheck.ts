/**
 * Call precheck before checkout and read proves, stale, and checked_ago honestly.
 *
 * Set PRECHECK_USER_AGENT to the name of your agent. The fallback is a placeholder.
 * Set PRECHECK_URL to a mock in CI. This file does not fetch the store and it
 * does not call a model.
 */

import { pathToFileURL } from "node:url";

// On any error or timeout, treat the store as unknown, not as no.

// Set PRECHECK_USER_AGENT to the name of your agent. The fallback is a placeholder.
export const USER_AGENT = process.env.PRECHECK_USER_AGENT ?? "my-agent/1.0 (+https://example.com/contact)";
const DEFAULT_ENDPOINT = "https://www.arcreport.ai/api/precheck";
const DAY_MS = 24 * 60 * 60 * 1000;
const cache = new Map<string, { at: number; body: PrecheckBody }>();
const EXAMPLE_URL = "https://allbirds.com/products/shoe";

export const LIMITS = {
  checked_ago:
    'Coarse age of last_checked, copied unchanged. "never checked" means the check time is missing or unparseable. null means the saved time is in the future, so no age is stated.',
  stale:
    "Copied unchanged. True when last_checked is 24 hours old or older, or the check time is missing or unparseable. False only when the saved check is newer than 24 hours.",
  proves:
    "Copied unchanged from each rail. The sentence describes that saved status. It does not prove an agent completed checkout. null rails means ARC returned no proves sentence.",
  reachable_checkout:
    "Copied unchanged. True only when a saved check returned a checkout link. False when that check finished without one. null when there is no completed check. This is not an agent that finished checkout.",
} as const;

type Rail = { name?: unknown; status?: unknown; proves?: unknown };
type PrecheckBody = {
  host?: unknown;
  known?: unknown;
  reachable_checkout?: unknown;
  checked_ago?: unknown;
  stale?: unknown;
  rails?: unknown;
};

export function endpoint(): string {
  return process.env.PRECHECK_URL ?? DEFAULT_ENDPOINT;
}

function storeHost(url: string): string {
  try {
    return new URL(url).hostname.toLowerCase().replace(/\.$/, "").replace(/^www\./, "") || url;
  } catch {
    return url;
  }
}

function retryAfterSeconds(header: string | null): number {
  if (!header) return 60;
  const asNumber = Number(header);
  if (Number.isFinite(asNumber) && asNumber >= 0) return Math.ceil(asNumber);
  const when = Date.parse(header);
  if (Number.isFinite(when)) return Math.max(0, Math.ceil((when - Date.now()) / 1000));
  return 60;
}

export async function fetchPrecheck(url: string): Promise<PrecheckBody> {
  const host = storeHost(url);
  const saved = cache.get(host);
  // One saved answer per host for 24 hours. The limit is 60 requests a minute.
  if (saved && Date.now() - saved.at < DAY_MS) return saved.body;
  // Send the store origin only (scheme and host), not the full product URL.
  const target = endpoint() + "?url=" + encodeURIComponent(new URL(url).origin);
  const res = await fetch(target, {
    headers: { "user-agent": USER_AGENT, accept: "application/json" },
    signal: AbortSignal.timeout(10000),
  });
  if (res.status === 429) {
    // Respect Retry-After. Do not retry in a loop.
    throw new Error("rate limited, retry after " + retryAfterSeconds(res.headers.get("retry-after")) + " s");
  }
  if (!res.ok) throw new Error("precheck HTTP " + res.status);
  const payload: unknown = await res.json();
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("precheck response was not a JSON object");
  }
  const body = payload as PrecheckBody;
  cache.set(host, { at: Date.now(), body });
  return body;
}

/** Copy the saved fields. Do not rewrite a missing check into a fresh one. */
export function honest(body: PrecheckBody) {
  const rails = Array.isArray(body.rails)
    ? body.rails.filter((rail): rail is Rail => Boolean(rail) && typeof rail === "object").map((rail) => ({
        name: rail.name ?? null,
        status: rail.status ?? null,
        proves: rail.proves ?? null,
      }))
    : null;
  return {
    host: body.host ?? null,
    known: body.known ?? null,
    reachable_checkout: body.reachable_checkout ?? null,
    checked_ago: body.checked_ago ?? null,
    stale: body.stale ?? null,
    rails,
    limits: LIMITS,
  };
}

export async function readingFor(url: string) {
  return honest(await fetchPrecheck(url));
}

async function main() {
  const url = process.env.PRECHECK_EXAMPLE_URL ?? EXAMPLE_URL;
  console.log(JSON.stringify({ reading: await readingFor(url) }));
}

const isDirect = process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isDirect) {
  main().catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : "precheck failed");
    process.exit(1);
  });
}
