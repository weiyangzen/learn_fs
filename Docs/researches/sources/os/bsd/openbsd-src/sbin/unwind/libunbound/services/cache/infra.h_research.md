# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/infra.h

## Purpose
Declares the infrastructure cache API and data structures used by Unbound services for upstream-server health, EDNS/lameness knowledge, domain/client ratelimits, and wait limits.

## Key Types
- `struct infra_key`: slabhash key for a server address plus zone name.
- `struct infra_data`: cached server metadata: TTL, probe delay, RTT estimator, EDNS version/known flag, DNSSEC/recursion/type lameness, and A/AAAA/other timeout counters.
- `struct infra_cache`: top-level owner for host cache, domain rate table, domain limit tree, client-IP rate table, and wait-limit netblock trees.
- `struct domain_limit_data`: name-tree node with exact and below-domain QPS limits.
- `struct rate_key` / `struct rate_data`: delegation-point QPS key and two-second counter window.
- `struct ip_rate_key`: client address key for IP ratelimit and wait-count tracking.
- `struct wait_limit_netblock_info`: address-tree node with configured outstanding-wait limit.

## Constants and Globals
- `TIMEOUT_COUNT_MAX`: allows limited type-specific probes before marking a server unusable for that qtype class.
- `PROBE_MAXRTO`: external probe threshold for high RTO values.
- `RATE_WINDOW`: two-second rate tracking window.
- `infra_dp_ratelimit`, `infra_ip_ratelimit`, `infra_ip_ratelimit_cookie`: process-global configured ratelimits.

## API Surface
- Lifecycle/configuration: `infra_create()`, `infra_delete()`, `infra_adjust()`.
- Host health: `infra_host()`, `infra_lookup_nottl()`, `infra_rtt_update()`, `infra_update_tcp_works()`, `infra_get_host_rto()`.
- Capability/lameness: `infra_set_lame()`, `infra_edns_update()`, `infra_get_lame_rtt()`.
- Domain ratelimit: `infra_ratelimit_inc()`, `infra_ratelimit_dec()`, `infra_ratelimit_exceeded()`, `infra_find_ratelimit()`, `infra_rate_max()`.
- Client-IP ratelimit and wait limits: `infra_ip_ratelimit_inc()`, `infra_wait_limit_allowed()`, `infra_wait_limit_inc()`, `infra_wait_limit_dec()`.
- Tree setup/free helpers exported for tests or config reload code.
- Slabhash callback functions for infra, domain-rate, and IP-rate tables.

## Design Notes
The header exposes enough internals for unit tests and other resolver modules to inspect timing, lameness, and ratelimit behavior. It also documents lock expectations: `infra_lookup_nottl()` can return read- or write-locked entries, and array/cache users must unlock entries they obtain.

## Dependencies
Depends on Unbound utility infrastructure: `lruhash`, `dnstree`, `rtt`, `netevent`, and message reply/query structures. It is tightly coupled to resolver server selection, mesh wait accounting, and configuration parsing.
