// Check before checkout (Stagehand). Advisory only: ARC says whether an agent can likely reach checkout; ARC stops before payment.
export async function arcPrecheck(storeUrl: string) {
  const u = new URL("https://www.arcreport.ai/api/precheck");
  u.search = new URLSearchParams({ url: storeUrl, ref: "stagehand" }).toString();
  const r = await fetch(u, { headers: { "User-Agent": "stagehand-agent/1.0 undici", "X-ARC-Client": "stagehand" } });
  if (!r.ok) throw new Error(`ARC precheck ${r.status}`);
  return r.json(); // { stale, last_checked, reachable_checkout, rails[] }
}
// Usage: const c = await arcPrecheck(page.url()); if (!c.reachable_checkout || c.stale) { /* stop or ask the user */ } else { await page.act("go to checkout"); }
