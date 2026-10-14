// Check before checkout (Stagehand). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
// On any error or timeout, treat the store as unknown, not as no.
export async function arcPrecheck(storeUrl: string) {
  const origin = new URL(storeUrl).origin; // send the store origin only, not the product URL
  const u = new URL("https://www.arcreport.ai/api/precheck");
  u.search = new URLSearchParams({ url: origin, ref: "stagehand" }).toString();
  const r = await fetch(u, {
    headers: { "User-Agent": "stagehand-agent/1.0 undici", "X-ARC-Client": "stagehand" },
    signal: AbortSignal.timeout(10000),
  });
  if (!r.ok) throw new Error(`ARC precheck ${r.status}`);
  return r.json(); // { stale, last_checked, reachable_checkout, rails[] }
}
// Usage: const c = await arcPrecheck(page.url()); if (!c.reachable_checkout || c.stale) { /* stop or ask the user */ } else { await page.act("go to checkout"); }
