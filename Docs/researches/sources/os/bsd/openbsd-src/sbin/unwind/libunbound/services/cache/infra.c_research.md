# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.c

## Purpose
Implements Unbound's infrastructure cache for OpenBSD `unwind`: authoritative-server RTT tracking, EDNS capability/lame-server state, delegation-point rate limiting, client-IP rate limiting, and per-client wait limits.

## Main Responsibilities
- Create, resize, and destroy `struct infra_cache` and its slabhash-backed tables.
- Track per `(server address, zone)` health with TTL, RTT/RTO, probe delay, EDNS support, DNSSEC lameness, recursion lameness, type-specific lameness, and timeout counters.
- Implement delegation-point ratelimits with exact and below-domain overrides.
- Implement client-IP ratelimits and client-IP mesh wait limits, with separate defaults/trees for DNS Cookie clients.
- Provide memory accounting and hash/delete/compare callbacks for slabhash entries.

## Key Data Flow
- `infra_create()` builds `hosts`, `domain_rates`, `client_ip_rates`, `domain_limits`, and wait-limit trees from `struct config_file`.
- `infra_host()` looks up or creates an infra host entry before sending to an upstream server. Expired entries are reinitialized while preserving severe timeout/probe state when useful.
- `infra_rtt_update()` updates RTT state after success or timeout, increments A/AAAA/other timeout counters on loss, and clears counters on success.
- `infra_get_lame_rtt()` exposes lameness and RTT to server selection, including single-probe behavior for hosts near or above `PROBE_MAXRTO`.
- `infra_ratelimit_inc()/dec()/exceeded()` charge or release delegation-point query counts in a two-second `RATE_WINDOW`.
- `infra_ip_ratelimit_inc()` charges per-client address QPS, ignoring source port via `hash_addr(..., use_port=0)`.
- `infra_wait_limit_allowed/inc/dec()` uses the same client-IP rate table's `mesh_wait` field to limit outstanding replies.

## Important Functions
- `still_useful_timeout()`: returns a timeout below `USEFUL_SERVER_TOP_TIMEOUT` but above the RTT band, keeping bad servers probeable without fully selecting them.
- `infra_compfunc()`, `hash_infra()`: key infra entries by full socket address including port plus zone dname.
- `setup_domain_limits()`: parses configured ratelimit domains into a `name_tree`.
- `setup_wait_limits()`: initializes address-tree wait limits and adds loopback defaults with limit `-1`.
- `infra_find_ratelimit()`: resolves exact domain limit, nearest parent `below` limit, or global `infra_dp_ratelimit`.
- `infra_rate_max()`: returns current-second rate or window max when backoff is enabled.
- `check_ip_ratelimit()`: logs the first crossing of a client-IP limit with parsed query details when possible.

## Concurrency and Lifetime
Slabhash lookups return locked entries. Mutating operations request write locks; read operations unlock before returning. New entries are inserted after allocation and lock initialization. Domain-limit and wait-limit trees are rebuilt during `infra_adjust()` when cache sizing is unchanged; slabhashes are recreated when configured sizes/slabs differ.

## Edge Cases and Risks
- Infra host expiration intentionally preserves severe timeout/probe state to avoid immediately trusting an unresponsive server.
- Client-IP rate limiting only checks `infra_ip_ratelimit` as the top-level enabled flag, so cookie-specific limiting depends on ordinary IP limiting being enabled.
- `infra_adjust()` reapplies domain limits but does not rebuild wait-limit trees unless the whole cache is recreated.
- Allocation failures in rate-entry creation are mostly treated as non-fatal and may allow traffic.
