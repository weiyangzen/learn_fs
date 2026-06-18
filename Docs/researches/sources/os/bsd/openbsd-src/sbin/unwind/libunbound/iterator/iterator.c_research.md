# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.c

`iterator.c` implements Unbound's recursive iterative resolver module. It registers the `iterator` module function block and drives the resolver state machine from initial cache/config lookup through authoritative target selection, response classification, CNAME/DNAME chasing, referrals, priming, and final response construction.

The main state paths are `processInitRequest()`, `processInitRequest2()`, `processInitRequest3()`, `processQueryTargets()`, `processQueryResponse()`, `processPrimeResponse()`, `processCollectClass()`, `processDSNSFind()`, and `processFinished()`, orchestrated by `iter_handle()` and entered through `iter_operate()`. Per-query state is allocated in `iter_new()` and cleaned in `iter_clear()`.

Initial resolution checks local/RPZ/auth-zone data, positive and negative caches, no-cache stub/forward policy, forwarding zones, cached delegations, auth-zone delegations, stub priming, and root priming. It handles non-recursive referral returns, qclass `ANY` by spawning per-class subqueries, and DS-query edge cases by searching for the correct parent-side NS point.

Target handling builds and updates delegation points, fetches missing A/AAAA nameserver addresses with subqueries, enforces dependency depth and target/query quotas, performs parent-side glue fallback, NXNS-style fallback, root safety-belt fallback, and optional hardened referral-path checks. Server selection respects IPv4/IPv6/NAT64 availability, do-not-query/private policy via helpers, infra-cache state, blacklists, TCP/TLS upstream flags, ratelimits, retry counts, and target-fetch policy.

Response handling parses packets, extracts EDNS options, scrubs/sanitizes responses, classifies them as answer/referral/CNAME/lame/recursive-lame/throwaway, stores useful data in message/rrset/negative/parent-side caches, marks lame or DNSSEC-lame servers, follows CNAME/DNAME chains, validates referral shape, prefetches DNSKEYs, and finalizes answer flags. It also implements qname minimisation, 0x20/caps-for-ID fallback, DNSSEC expected-data checks, serve-expired DNSKEY minimization, and EDE/error-info propagation.

Important safety controls include maximum query restarts, dependency depth, referrals, upstream sends, target lookups, per-delegation target lookups, NXDOMAIN nameserver lookups, and global upstream-query quota. Memory ownership is mostly regional for per-query data, with shared `target_count`/`nxns_dp` reference-counted manually across subqueries.
