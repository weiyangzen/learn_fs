# sources/object-store/openstack-swift/swift/common/middleware/cname_lookup.py

## Purpose
`cname_lookup.py` rewrites requests for vanity hostnames by following DNS CNAME records until a configured Swift storage domain is found. When a match is resolved, it rewrites `HTTP_HOST` and uses `RewriteContext` so downstream middleware sees the storage host while client-visible response locations can be adjusted.

## Important APIs, Types, and Functions
`lookup_cname(domain, resolver)` performs a CNAME query and returns `(ttl, result)`, with `False` representing no record and `None` representing transient DNS failure. `_CnameLookupContext` specializes `RewriteContext`. `CNAMELookupMiddleware` validates configuration, owns the resolver and cache, and performs request rewriting.

## Control Flow
Initialization requires `dnspython`, normalizes configured storage domains, validates optional nameserver IP/port strings, and builds a resolver. On each call it extracts the host, preserves an optional port, ignores IP addresses and hosts already in storage domains, then follows up to `lookup_depth` CNAME hops. It uses memcache when available, caching negative and positive results by TTL. A successful storage-domain match rewrites `HTTP_HOST`; failure returns `400 Bad Request`.

## State and Persistence
The middleware lazily stores a memcache client reference and caches CNAME results in external memcache under `cname-...` keys. Resolver configuration is process-local. No Swift metadata is persisted.

## Dependencies and Integration Points
It depends on `dns.resolver`, `dns.exception`, Swift cache discovery, socket-string parsing, IP validation, `RewriteContext`, and `/info` registration. It should run before domain remapping or proxy routing that depends on host-derived account/container data.

## Risks and Edge Cases
DNS failures can return immediate `400` depending on lookup result. The code caches using the original given domain in one branch and looks up using the current chain domain, so cache behavior across deep CNAME chains is subtle. Nameserver validation rejects hostnames and accepts only valid IPs with optional ports. Very large lookup depths increase latency and DNS/cache load.

## Test Signals
Tests should cover missing `dnspython`, storage-domain normalization, host-with-port preservation, IP bypass, nameserver validation, positive CNAME chains, no-record and transient-DNS failure behavior, memcache hit/miss and TTL caching, lookup-depth exhaustion, and `RewriteContext` location rewriting.
